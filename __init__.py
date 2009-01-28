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

from AccessControl import ModuleSecurityInfo

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CPSCore.interfaces import ICPSSite
from Products.CPSCore.upgrade import registerUpgradeCategory

registerDirectory('skins', globals())

def initialize(registrar):
    """Initialize Paris Montagne Contacts content and tools.
    """

    profile_registry.registerProfile(
        'default',
        'CPS File Mailer',
        "CPS File Mailer, default configuration",
        'profiles/default',
        'CPSFileMailer',
        EXTENSION,
        for_=ICPSSite)
