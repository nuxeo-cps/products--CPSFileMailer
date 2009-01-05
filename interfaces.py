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

from zope.interface import Interface

class IFileMailerTool(Interface):
    """FileMailer Tool.
    """

    def createTokenFor(proxy):
        """Create a new token entry in the filetokens directory.
        
        Return token and file name
        """

    def retrieveFile(token):
        """Retrieve the OFS.Image.File object associated with the token."""

    def getBaseUrl():
        """Return base url prop or standard portal base url."""

    def purgeOutdatedTokens(REQUEST=None):
        """Purge outdated tokens and return a simple status line."""

    def _purgeOutdatedTokens():
        """Purge outdated tokens and return (number of removed, of kept)"""
