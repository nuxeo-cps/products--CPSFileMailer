# (C) Copyright 2008 Tonal
# Author: Georges Racinet <georges@racinet.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

import os
import errno
import sys
import random

import Acquisition
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Globals import InitializeClass
from DateTime.DateTime import DateTime
from zExceptions import BadRequest

from zope.interface import implements

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ManagePortal

from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor

from interfaces import IFileMailerTool

TOKEN_DIR = 'filetokens'

class FileMailerTool(UniqueObject, PropertiesPostProcessor,
                     SimpleItemWithProperties):

    id = 'portal_filemailer'
    meta_type = 'File Mailer Tool'

    generic_setup_name = 'filemailer'
    generic_setup_logger_id = 'filemailer'

    implements(IFileMailerTool)

    security = ClassSecurityInfo()

    manage_options = SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_genericSetupExport.html',
         },
        )

    _propertiesBaseClass = SimpleItemWithProperties
    _properties=(
            {'id': 'tok_lifetime', 'type': 'int', 'mode':'w',
             'label': 'Lifetime of tokens (hours)'},
            {'id': 'base_url', 'type': 'string', 'mode':'w',
             'label': 'Public portal url (for emails, in case it differs from what contributors see)'},
            {'id': 'fields_mapping', 'type': 'lines', 'mode':'w',
             'label': 'Fields to retrieve (lines of <portal_type>:<field id>)'},
            )
    tok_lifetime = 12
    base_url = ''
    fields_mapping = ()
    fields_mapping_c = {}

    def _postProcessProperties(self):
        """Extract the fields_mapping dict."""

        self.fields_mapping = tuple(l for l in self.fields_mapping if l.strip())
        self.fields_mapping_c = dict(l.strip().split(':')
                                     for l in self.fields_mapping)

    def _getTokensDirectory(self):
        return getToolByName(self, 'portal_directories')._getOb(TOKEN_DIR)

    security.declarePublic('getBaseUrl')
    def getBaseUrl(self):
        """Return base url.

        Defaults to standard meaning of 'base_url."""
        return self.getProperty('base_url') or getToolByName(
            self, 'portal_url').getPortalObject().absolute_url()

    security.declarePublic('createTokenFor')
    def createTokenFor(self, proxy):
        """See interface."""

        # GR better to have the calling script issue the getContent()
        # and hence trigger security check ?
        if not _checkPermission(View, proxy):
            raise Unauthorized
        doc = proxy.getContent()
        docid = doc.getId() # includes rev
        exp = DateTime() + self.tok_lifetime / 24.0
        entry = { 'doc': docid,
                  'expiration': exp}

        tdir = self._getTokensDirectory()
        # now creation. In theory, the try/except approach should be faster
        # than using _hasEntry (avoid a stupid db miss). In practice,  most
        # dir implementations of _createEntry do call _hasEntry first (at least
        # we got it just once
        while True:
            token =  ''.join((hex(random.randrange(sys.maxint))[2:]
                                  for i in range(3)))
            entry['token'] = token
            try:
                tdir._createEntry(entry)
            except KeyError:
                pass
            else:
                break

        return token, self._extractFile(doc).title, exp

    def _purgeOutdatedTokens(self):
        """See interface.

        Dumb implementation based on the poor ZODBDirectory request
        capabilities."""

        tdir = self._getTokensDirectory()
        removed, kept = 0, 0
        # See #1927: searchEntries and return fields
        for tok in tdir.listEntryIds():
            entry = tdir._getEntry(tok)
            if entry['expiration'].isPast():
                removed += 1
                tdir._deleteEntry(tok)
            else:
                kept += 1
        return removed, kept

    security.declareProtected(ManagePortal, 'purgeOutdatedTokens')
    def purgeOutdatedTokens(self, REQUEST=None):
        """See interface."""

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        return "Removed %d outdated tokens and kept %d active ones.\n" % self._purgeOutdatedTokens()

    security.declarePublic('retrieveDoc')
    def retrieveDoc(self, token):
        """See interface.
        """
        tdir = self._getTokensDirectory()
        try:
            entry = tdir._getEntry(token)
        except KeyError:
            raise Unauthorized

        if entry['expiration'].isPast():
            raise Unauthorized

        repotool = getToolByName(self, 'portal_repository')
        try:
            doc = repotool._getOb(entry['doc'])
        except KeyError, AttributeError:
            raise Unauthorized

        return doc

    security.declarePublic('retrieveFile')
    def retrieveFile(self, token):
        """See interface.
        """
        return self._extractFile(self.retrieveDoc(token))

    def _extractFile(self, doc):
        """Return the File object for doc according to conf."""
        ptype = doc.portal_type
        field = self.fields_mapping_c.get(doc.portal_type)
        if field is None:
            raise ValueError("portal_type '%s' unknown" % ptype)

        # bypass of DataModel to avoid security problems
        return getattr(doc, field, None)

    def __getitem__(self, name):
        """Retrieve file if needed and wrap it in a FileServer instance.
        """
        req = self.REQUEST
        token = req.form.get('token')
        if token is None:
            return super().__getitem__(name)

        f = self.retrieveFile(token)
        if f.title_or_id() != name:
            # I can't see any legit use of this, but a few nasty ones
            raise BadRequest(
                "! File name changed. Should have been '%s'" % f.title_or_id())
        return FileServer(f, req).__of__(self)


class FileServer(Acquisition.Explicit):

    security = ClassSecurityInfo()

    def __init__(self, f, req):
        self.file = f
        self.req = req

    security.declarePublic('index_html')
    def index_html(self):
        """Serve the file."""
        resp = self.req.RESPONSE
        resp.setHeader('Content-Disposition',
                       'attachment; filename=%s' % self.file.title_or_id())
        return self.file.index_html(self.req, resp)
