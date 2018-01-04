"""
    (c) by Piotr Goryl, 3Controls, 2016/17 for Tango Controls Community

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import svn_utils
import svn.remote
import os
from getpass import getpass
from settings import *
from server_utils import DscServerUtils

# process of importing:

print "You are going to update a device servers catalogue info on the server: %s" % SERVER_BASE_URL


# login to server
if USER_LOGIN is None or USER_PASSWORD is None:
    login = raw_input('Login: ')
    password = getpass()
else:
    login = USER_LOGIN
    password = USER_PASSWORD

DscServerUtils.login_to_catalogue(login, password)


# getting list of device server from a SVN repository
if REPO_SYNC_COMMAND != '':
    print 'Synchronizing local repository...'
    print 'Using a commnad: %s' % REPO_SYNC_COMMAND
    os.system(REPO_SYNC_COMMAND)
    print '...local repository synchronized.'
    print '-------------------------------'
else:
    print 'Local repository will not be synchronized.'

print 'Getting a list of device server in the repository...'


repo = svn.remote.RemoteClient(LOCAL_REPO_URL)
ds_list = svn_utils.get_device_servers_list(repo, REPO_START_PATH, 10)

print 'Found %d device servers.' % len(ds_list)

DscServerUtils.update_catalogue(ds_list)
