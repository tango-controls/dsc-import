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
import urllib2
from getpass import getpass
import requests
import requests.auth
import requests.packages
import os.path
import os
from dateutil import parser as date_parser
from datetime import datetime
from pytz import utc
from time import sleep
import re
from xmi_from_html import get_xmi_from_html
from settings import *
# import cred



# process of importing:

print "You are going to update a devcie servers catalogue info on the server: %s" % SERVER_BASE_URL

login = raw_input('Login: ')
password = getpass()


client = requests.session()
client.verify = VERIFY_CERT
client.max_redirects = 5
client.headers = {'User-Agent': 'DSC-Importer'}

# client.cert = CERTS

if not VERIFY_CERT:
   requests.packages.urllib3.disable_warnings()

if TEST_SERVER_AUTH:
    print 'You are going to connect to test server which requires a basic authentication first.'
    ba_login = raw_input('Basic auth login: ')
    ba_password = getpass('Basic auth password: ')
    client.auth = requests.auth.HTTPBasicAuth(ba_login, ba_password)

client.get(SERVER_LOGIN_URL)

csrftoken = client.cookies['csrftoken']
print csrftoken

login_data = dict(login=login, password=password, csrfmiddlewaretoken=csrftoken)
r = client.post(SERVER_LOGIN_URL, data=login_data, headers={'Referer':SERVER_LOGIN_URL})
referrer=SERVER_LOGIN_URL

if r.status_code!=200:
    print "wrong password or sever connection error."
    print r.headers
    print r.status_code
    exit()
else:
    print 'Successfully logged in to catalogue server.'


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
ds_list = svn_utils.get_device_servers_list(repo,REPO_START_PATH,10)

ds_problems = []
ds_skipped = []

print 'Found %d device servers.' % len(ds_list)

xmi_updated = 0
xmi_added = 0
xmi_not_changed = 0

for ds in ds_list:
    print
    print '------------------------------------'
    print 'Processing %s' % ds['path']
    try:


        # device server name:
        ds_name = os.path.basename(ds['path'])
        if len(ds_name) > 0:
            auto_ds_name = False
            print 'Device server name from path: %s' % ds_name
        else:
            auto_ds_name = True
            print 'Cannot guess name of device server from the path.'
        # developement status
        development_status = 'new'
        if ds.has_key('tag'):
            development_status = 'released'

        family_parsed = re.match(FAMILY_FROM_PATH_PARSER, ds['path'])
        family = None

        if family_parsed is not None:
            family = family_parsed.group(1)
            if family is not None:
                print "Class family from the path is %s." % family

        documentation_URL = ''
        documentation_title = ''
        link_documentation = False
        if ADD_LINK_TO_DOCUMENTATION:
            if family is not None:
                documentation_URL = DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/'+ ds_name + '.pdf'
                documentation_title = 'PDF generated from POGO'

                doc_check_client = requests.session()
                r = requests.get(documentation_URL, allow_redirects=False)
                if r.status_code!=200:
                    print 'It seems this device server is not documented in a standard path.'
                    link_documentation = False
                else:
                    link_documentation = True
            else:
                print 'Cannot link documentation since a class family has not been properly detected.'

        xmi_from_doc = False
        xmi_from_url = True
        xmi_content = ''
        files = {}

        # case when there is no .xmi files

        if len(ds['xmi_files'])==0:
            print 'No .xmi files found in this path.'
            # can use documentation if device server name can be guessed.
            if USE_DOC_FOR_NON_XMI and not auto_ds_name:
                print 'Trying to use documentation to build an .xmi file.'
                xmi_from_doc = True
                xmi_from_url = False
                if family is None:
                    print 'Cannot parse the path for a family!'
                    ds_problems.append(ds)
                    continue

                xmi_content = get_xmi_from_html(description_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/ClassDescription.html',
                                                attributes_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/Attributes.html',
                                                commands_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/Commands.html',
                                                properties_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/Properties.html'
                                                )
                print 'XMI from doc size is %d.' % len(xmi_content)
                files['xmi_file'] = (ds_name+'.xmi',xmi_content)
                with open(LOG_PATH+'/'+files['xmi_file'][0],'wb') as f:
                    f.write(xmi_content)

                ds['xmi_files'] = [{
                    'name': ds_name+'.xmi',
                    'path': '',
                    'element': { 'date': datetime.now(utc) }
                },]


            else:
                print 'Skipping this path.'
                ds_skipped.append(ds)
                continue


        print 'Checking if the device server already exists in the catalogue...'

        r = client.get(SERVER_LIST_URL+REMOTE_REPO_URL+'/'+ds['path'], headers={'Referer':referrer})
        referrer = SERVER_LIST_URL+REMOTE_REPO_URL+'/'+ds['path']
        ds_on_server = r.json()
        # print "The following device servers match repository are in the catalogue: "
        # print ds_on_server

        if len(ds_on_server)>1:
            print 'There are %d device servers registered with this repository path. ' \
                  'Import utility does not handle such a case. Skipping.  ' % len(ds_on_server)
            ds_skipped.append(ds)
            continue

        if len(ds_on_server)==1:
            print 'This device server already exists in the catalogue. It will be updated if necessary.'
            server_ds_pk, server_ds = ds_on_server.popitem()
            ds_adding = False
            if server_ds['last_update_method'] == 'manual':
                print 'This device server has been updated manually on the server. It will not be updated via script.'
                continue
            doc_pk = ''
            if link_documentation:
                for doc in server_ds['documentation']:
                    if doc['updated_by_script']:
                        if doc['title']!=documentation_title or doc['url']!=documentation_URL:
                            doc_pk = doc['pk']
                            break
                        else:
                            link_documentation = False

        else:
            ds_adding = True
            print 'This is a new device server. It will  be added to the catalogue.'

        ds_repo_url = REMOTE_REPO_URL + '/' + ds['path']

        repository_tag = ds.get('tag', '')



        # readme file
        upload_readme = False
        if len(ds['readme_files'])>0:
            readme_file = ds['readme_files'][0]
            readme_name = readme_file['name']
            print 'There is a readme file: %s' % readme_name
            if os.path.splitext(readme_name)[1] not in ['.txt', '.TXT',
                                                         '.md', '.MD',
                                                         '', '.doc', '.DOC',
                                                         '.rst', '.RST',
                                                         '.pdf', '.PDF',
                                                         '.html', '.HTML', '.htm', '.HTM']:
                print 'I will skip file of unknown extension.'
            else:
                if ds_adding or FORCE_UPDATE or \
                        date_parser.parse(server_ds['last_update']) < readme_file['element']['date']:
                    # print "README date on SVN: %s" % readme_file['element']['date']
                    # print "README date in the catalogue: %s" % date_parser.parse(server_ds['last_update'])
                    # get file from the server
                    readme_url_response = urllib2.urlopen(REMOTE_REPO_URL + '/' + readme_file['path'] + \
                                                          '/' + readme_file['name'])
                    readme_file_size = int(readme_url_response.info().get('Content-Length',0))
                    if readme_file_size < 5 or readme_file_size > 2000000:
                        print 'Readme file size %d is out of limits. Skipping.' % readme_file_size
                    else:
                        print 'It will be uploaded.'
                        read_file_content=readme_url_response.read()
                        files['readme_file'] = (readme_name, read_file_content)
                        upload_readme = 1
                else:
                    print 'Will skip the readme upload since it is elder than the last update of device server.'

        # .XMIs
        first_xmi=True

        # print 'Files to be uploaded:'
        # print files

        # print 'XMI files: '
        # print ds['xmi_files']

        for xmi in ds['xmi_files']:
            print "XMI file: %s" % xmi['name']
            xmi_url = REMOTE_REPO_URL + '/' + xmi['path'] + '/' + xmi['name']
            # skip
            if str(xmi['name']).strip().lower().endswith('.multi.xmi'):
                continue

            if first_xmi:
                if ds_adding:
                    client.get(SERVER_ADD_URL, headers={'Referer':referrer})  # sets the cookie
                    referrer = SERVER_ADD_URL
                    csrftoken = client.cookies['csrftoken']
                    r = client.post(SERVER_ADD_URL,
                                data={
                                    'csrfmiddlewaretoken': csrftoken,
                                    'script_operation': True,
                                    'ds_info_copy': auto_ds_name,
                                    'development_status': development_status,
                                    'name': ds_name,
                                    'description': '',
                                    'xmi_file_url':xmi_url,
                                    'use_url_xmi_file': xmi_from_url,
                                    'use_manual_info': False,
                                    'use_uploaded_xmi_file': xmi_from_doc,
                                    'repository_url': ds_repo_url,
                                    'repository_type': 'SVN',
                                    'repository_tag': repository_tag,
                                    'upload_readme': upload_readme,
                                    'submit': 'create',
                                    'available_in_repository': True,
                                    'other_documentation1': link_documentation,
                                    'documentation1_title': documentation_title,
                                    'documentation1_url': documentation_URL,
                                    'documentation1_pk': doc_pk,
                                    'documentation1_type': 'Generated'
                                },
                                files=files,  headers={'Referer':referrer})

                    print 'Adding result: %d' % r.status_code
                    add_result = r

                    sleep(1)
                    r = client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'],  headers={'Referer':referrer})
                    referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']
                    ds_on_server = r.json()
                    if len(ds_on_server) == 1:
                        server_ds_pk, server_ds = ds_on_server.popitem()
                        first_xmi = False
                        xmi_added += 1
                        print 'The device server has been added to the catalogue.'
                    else:
                        print 'It seems the device server has not been added to the catalogue...'
                        ds_problems.append(ds)
                        f = open(LOG_PATH + '/problematic-add-result.html', 'wb')
                        f.write(add_result.content)
                        f.close()
                        break

                elif FORCE_UPDATE or date_parser.parse(server_ds['last_update'])<xmi['element']['date']:
                    print 'Updating with XMI: %s' % xmi['name']
                    client.get(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update/', headers={'Referer':referrer})
                    referrer = SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update/'
                    csrftoken = client.cookies['csrftoken']
                    r = client.post(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update/',
                                data={
                                    'csrfmiddlewaretoken': csrftoken,
                                    'script_operation': True,
                                    'ds_info_copy': auto_ds_name,
                                    'development_status': development_status,
                                    'name': ds_name,
                                    'last_update_method': server_ds['last_update_method'],
                                    'description': '',
                                    'add_class': False,
                                    'only_github': FORCE_ONLY_GITHUB and not date_parser.parse(server_ds['last_update'])<xmi['element']['date'],
                                    'xmi_file_url':xmi_url,
                                    'use_url_xmi_file': xmi_from_url,
                                    'use_manual_info': False,
                                    'use_uploaded_xmi_file': xmi_from_doc,
                                    'repository_url': ds_repo_url,
                                    'repository_type': 'SVN',
                                    'repository_tag': repository_tag,
                                    'upload_readme': upload_readme,
                                    'submit': 'update',
                                    'available_in_repository': True,
                                    'other_documentation1': link_documentation,
                                    'documentation1_title': documentation_title,
                                    'documentation1_url': documentation_URL,
                                    'documentation1_pk': doc_pk,
                                    'documentation1_type': 'Generated'
                                },
                                files=files, headers={'Referer':referrer})
                    print 'Update result: %d' % r.status_code
                    update_result = r

                    r = client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'], headers={'Referer': referrer})
                    referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']
                    ds_on_server = r.json()
                    if len(ds_on_server) == 1:
                        u_server_ds_pk, u_server_ds = ds_on_server.popitem()
                        if date_parser.parse(server_ds['last_update'])<date_parser.parse(u_server_ds['last_update']):
                            server_ds = u_server_ds
                            print '.XMI has been successfully updated in the catalogue.'
                            first_xmi = False
                            xmi_updated += 1
                        else:
                            print 'It seems the device server has not been properly updated in the catalogue...'
                            ds_problems.append(ds)
                            f = open(LOG_PATH + '/problematic-update-result.html', 'wb')
                            f.write(update_result.content)
                            f.close()
                            break
                    else:
                        print 'It seems the device server has not been properly updated in the catalogue...'
                        ds_problems.append(ds)
                        break

                    first_xmi = False
                    sleep(1)
                else:
                    xmi_not_changed += 1
                    print 'Skipping update with the XMI: %s. Seems the catalogue is up to date for it.' % xmi['name']

            elif ds_adding or FORCE_UPDATE or date_parser.parse(server_ds['last_update']) < xmi['element']['date']:
                print 'Updating with XMI: %s' % xmi['name']
                client.get(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/', headers={'Referer':referrer})
                referrer = SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/'
                csrftoken = client.cookies['csrftoken']
                r = client.post(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update/',
                            data={
                                'csrfmiddlewaretoken': csrftoken,
                                'script_operation': True,
                                'ds_info_copy': False,
                                'name': ds_name,
                                'last_update_method': server_ds['last_update_method'],
                                'development_status': development_status,
                                'description': '',
                                'add_class': True,
                                'xmi_file_url':xmi_url,
                                'use_url_xmi_file': xmi_from_url,
                                'use_manual_info': False,
                                'use_uploaded_xmi_file': xmi_from_doc,
                                'repository_url': ds_repo_url,
                                'repository_type': 'SVN',
                                'repository_tag': repository_tag,
                                'upload_readme': False,
                                'submit': 'update',
                                'available_in_repository': True
                            }, headers={'Referer':referrer})
                print 'Update result: %d' % r.status_code
                xmi_updated += 1
                sleep(1)
            else:
                xmi_not_changed += 1
                print 'Skipping update with the XMI: %s. Seems the catalogue is up to date for it.' % xmi['name']




    except Exception as e:
        print e.message
        ds_problems.append(ds)

print '\nImport summary:'
print '---------------------------'
print 'Skippend %d device servers (no xmi files).' % len(ds_skipped)
print 'Problems with %d device servers (errors in processing).' % len(ds_problems)

print 'Count of updated or added XMI files: %d' % (xmi_added+xmi_updated)
print 'Count of untouched (not changed) xmi files: %d ' % (xmi_not_changed)








