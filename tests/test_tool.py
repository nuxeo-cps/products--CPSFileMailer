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
#
# $Id: __init__.py 890 2008-06-18 18:26:32Z joe $

import unittest
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSFileMailer.tests.layer import CPSFileMailerLayer

from OFS.Image import File
from AccessControl import Unauthorized
from Products.CPSFileMailer.tool import FileMailerTool

class FileMailerToolTestCase(unittest.TestCase):
    def setUp(self):
        self.fmtool = FileMailerTool()
        
    def test_fields_mapping(self):
        self.fmtool.manage_changeProperties(
            fields_mapping=('Type:attached', 'Other:file '))
        self.assertEquals(self.fmtool.fields_mapping_c, {'Type': 'attached', 
                                                         'Other': 'file'})
        self.fmtool.manage_changeProperties(
            fields_mapping=('', 'Type:attached', ' '))
        self.assertEquals(self.fmtool.fields_mapping_c, {'Type': 'attached'}) 

        self.fmtool.manage_changeProperties(fields_mapping=())
        self.assertEquals(self.fmtool.fields_mapping_c, {}) 

class FileMailerToolIntegrationTestCase(CPSTestCase):

    layer = CPSFileMailerLayer

    def afterSetUp(self):
        self.login('manager')
        self.ws = self.portal.workspaces
        self.wftool = self.portal.portal_workflow
        self.fmtool = self.portal.portal_filemailer
        f = File('file', 'truc.txt', 'here it is')
        docname = self.wftool.invokeFactoryFor(self.ws, 'File', 'item', 
                                                file=f)
        self.doc = getattr(self.ws, docname)

    def testCreateToken(self):
        token, _, _ = self.fmtool.createTokenFor(self.doc)
        tdir = self.portal.portal_directories.filetokens
        entry = tdir._getEntry(token)
        self.assertEquals(entry.get('doc'), self.doc.getContent().getId())
        self.assertTrue(entry.get('expiration').isFuture())

    def testRetrieveFile(self):
        token, _, _ = self.fmtool.createTokenFor(self.doc)
        f = self.fmtool.retrieveFile(token)
        self.assertFalse(f is None)
        self.assertEquals(f.title, 'truc.txt')

    def testRetrieveOtherFile(self):
        self.fmtool.manage_changeProperties(fields_mapping=('File:other',))
        self.doc.getContent().other = File('other', 'autre.pdf', 'content')
        token, _, _ = self.fmtool.createTokenFor(self.doc)
        f = self.fmtool.retrieveFile(token)
        self.assertFalse(f is None)
        self.assertEquals(f.title, 'autre.pdf')
        self.assertEquals(str(f), 'content')

    def testTraversal(self):
        token, filename, _ = self.fmtool.createTokenFor(self.doc)
        self.logout()

        # now modelling what happens if client follows link
        # first traverse, finally call index_html
        base = self.portal.absolute_url()
        self.portal.REQUEST.form['token'] = token

        path = self.portal.portal_filemailer.getPhysicalPath() + (filename,)
        # BaseRequest.traverse() needs a non empty list of parents, whose
        # last item is more or less the beginning of traversal
        self.portal.REQUEST['PARENTS'] = [self.app]
        meth = self.portal.REQUEST.traverse('/'.join(path))
        self.assertEquals('here it is', meth())

        # Now, a restrictedTraverse from code (yes, that's a totally different
        # piece of code being executed)
        fs = self.portal.portal_filemailer.restrictedTraverse(filename)
        self.assertEquals('here it is', fs.index_html())

    def testWrongToken(self):
        token, _, _ = self.fmtool.createTokenFor(self.doc)
        self.assertRaises(Unauthorized, self.fmtool.retrieveFile, '000')

    def testExpired(self):
        # trick the took into setting the expiration in the past
        self.fmtool.tok_lifetime = -1
        token, _, exp = self.fmtool.createTokenFor(self.doc)
        self.assertTrue(exp.isPast())
        self.assertRaises(Unauthorized, self.fmtool.retrieveFile, token)

    def testPurge(self):
        tdir = self.portal.portal_directories.filetokens
        # two valid tokens
        self.fmtool.createTokenFor(self.doc)
        self.fmtool.createTokenFor(self.doc)
        self.fmtool.tok_lifetime = -1
        # one outdated one
        self.fmtool.createTokenFor(self.doc)

        # reality check
        self.assertEquals(3, len(tdir.listEntryIds()))
        removed, kept = self.fmtool._purgeOutdatedTokens()
        self.assertEquals(removed, 1) 
        self.assertEquals(kept, 2) 
        # reality check
        self.assertEquals(2, len(tdir.listEntryIds()))

    def testPurgeTTW(self):
        # one valid token
        self.fmtool.createTokenFor(self.doc)
        self.fmtool.tok_lifetime = -1
        # two outdated ones
        self.fmtool.createTokenFor(self.doc)
        self.fmtool.createTokenFor(self.doc)
        line = self.fmtool.purgeOutdatedTokens()
        self.assertTrue(isinstance(line, str))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FileMailerToolTestCase),
        unittest.makeSuite(FileMailerToolIntegrationTestCase),
        ))
