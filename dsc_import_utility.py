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


import os
from getpass import getpass
import svn.remote
from server_utils import DscServerUtils
import argparse
import svn_utils
import csv_utils

from settings import *

# get command line arguments
arguments = argparse.ArgumentParser(description="This script batch imports device servers/classes to Tango Controls "
                                                "Device Classes Catalogue.",
                                    epilog="Please configure the script in settings.py to make it comply with your "
                                           "environment.")
arguments.add_argument("--csv-file", dest='csv_file', default=None, help="If provided the script will parse the CSV_FILE instead "
                                                           "of an SVN repository defined in settings.py.", )

args = arguments.parse_args()

print "You are going to update a device servers catalogue info on the server: %s" % SERVER_BASE_URL

# login to server
if USER_LOGIN is None or USER_PASSWORD is None:
    login = raw_input('Login: ')
    password = getpass()
else:
    login = USER_LOGIN
    password = USER_PASSWORD

dsc_sever = DscServerUtils()

dsc_sever.login_to_catalogue(login, password)


# get list of device servers to be processed
ds_list = []

if args.csv_file is None:
    # by default list of device servers is got from an SVN repository
    print
    print "Using SVN as source of device servers list."
    print
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

else:
    # if SV file provided the list is built according to it
    print
    print "Using %s file to build a list of device servers." % args.csv_file
    print
    ds_list = csv_utils.get_device_servers_list(args.csv_file)

print 'Found %d device servers.' % len(ds_list)

# update the catalogue
dsc_sever.update_catalogue(ds_list)
