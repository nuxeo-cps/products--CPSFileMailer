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

# Zope3 component architecture
from zope.component import adapts
from zope.interface import implements

# Standard GenericSetup base classes and functions
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from Products.CMFCore.utils import getToolByName

TOOL = 'portal_filemailer'
NAME = 'filemailer'

def exportFileMailerTool(context):
    """Export our Filemailer tool configuration
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importFileMailerTool(context):
    """Import filemailer tool configuration
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)
