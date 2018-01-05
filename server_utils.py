"""
    (c) by Piotr Goryl, 3Controls, 2017/18 for Tango Controls Community

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
from dateutil import parser as date_parser
from datetime import datetime
from pytz import utc
from time import sleep
import re
import urllib2
import requests.auth


from xmi_from_html import get_xmi_from_html



from datetime import datetime
from pytz import utc
import requests

from settings import *


class DscServerUtils:

    client = None

    csrftoken = None

    referrer = None

    def __init__(self):
        pass

    def login_to_catalogue(self, login, password):

        self.client = requests.session()
        self.client.verify = VERIFY_CERT
        self.client.max_redirects = 5
        self.client.headers = {'User-Agent': 'DSC-Importer'}

        # self.client.cert = CERTS

        if not VERIFY_CERT:
            requests.packages.urllib3.disable_warnings()

        if TEST_SERVER_AUTH:
            print 'You are going to connect to test server which requires a basic authentication first.'
            ba_login = raw_input('Basic auth login: ')
            ba_password = getpass('Basic auth password: ')
            self.client.auth = requests.auth.HTTPBasicAuth(ba_login, ba_password)

        self.client.get(SERVER_LOGIN_URL)

        self.csrftoken = self.client.cookies['csrftoken']
        print self.csrftoken

        login_data = dict(login=login, password=password, csrfmiddlewaretoken=self.csrftoken)
        r = self.client.post(SERVER_LOGIN_URL, data=login_data, headers={'Referer': SERVER_LOGIN_URL})
        self.referrer = SERVER_LOGIN_URL

        if r.status_code != 200:
            print "wrong password or sever connection error."
            print r.headers
            print r.status_code
            exit()
        else:
            print 'Successfully logged in to catalogue server.'

    def update_catalogue(self, ds_list):
        """
        Updates catalogue
        :param ds_list:
        :return:
        """
        # counters for device servers processed
        xmi_updated = 0
        xmi_added = 0
        xmi_not_changed = 0
        ds_problems = []
        ds_skipped = []

        for ds in ds_list:
            print
            print '------------------------------------'
            print 'Processing %s' % ds.get('path', ds.get('name', ''))

            try:

                # device server name:
                ds_name = os.path.basename(ds.get('path', ds.get('name', '')))
                if len(ds_name) > 0:
                    auto_ds_name = False
                    print 'Device server name: %s' % ds_name
                else:
                    auto_ds_name = True
                    print 'Cannot guess name of device server from the path nor ds name directly provided.'

                # development status
                development_status = 'new'
                if ds.has_key('tag'):
                    development_status = 'released'

                family_parsed = re.match(FAMILY_FROM_PATH_PARSER, ds.get('path', ''))
                family = None

                if family_parsed is not None:
                    family = family_parsed.group(1)
                    if family is not None:
                        print "Class family from the path is %s." % family

                # documentation
                documentation_URL = ''
                documentation_title = ''
                documentation_type = ''
                documentation_pk = ''
                link_documentation = False

                if ADD_LINK_TO_DOCUMENTATION and ds.get('documentation_url', None) is None:
                    if family is not None:
                        documentation_URL = DOCUMENTATION_BASE_URL + family + '/' + ds_name + '/' + ds_name + '.pdf'
                        documentation_title = 'PDF generated from POGO'
                        documentation_type = 'Generated'

                        doc_check_client = requests.session()
                        r = requests.get(documentation_URL, allow_redirects=False)
                        if r.status_code != 200:
                            print 'It seems this device server is not documented in a standard path.'
                            link_documentation = False
                        else:
                            link_documentation = True
                    else:
                        print 'Cannot link documentation since a class family has not been properly detected.'

                elif ds.get('documentation_url', None) is not None:
                    # add documentation provided within list
                    documentation_URL = ds.get('documentation_url')
                    documentation_title = ds.get('documentation_title', 'Pogo')
                    documentation_type = ds.get('documentation_type', 'Generated')
                    link_documentation = True

                xmi_from_doc = False
                xmi_from_url = True
                xmi_content = ''
                files = {}

                # case when there is no .xmi files
                if len(ds['xmi_files']) == 0:

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

                        xmi_content = get_xmi_from_html(description_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name
                                                                        + '/ClassDescription.html',
                                                        attributes_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name
                                                                       + '/Attributes.html',
                                                        commands_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name
                                                                     + '/Commands.html',
                                                        properties_url=DOCUMENTATION_BASE_URL + family + '/' + ds_name
                                                                       + '/Properties.html'
                                                        )
                        print 'XMI from doc size is %d.' % len(xmi_content)
                        files['xmi_file'] = (ds_name + '.xmi', xmi_content)
                        with open(LOG_PATH + '/' + files['xmi_file'][0], 'wb') as f:
                            f.write(xmi_content)

                        ds['xmi_files'] = [{
                            'name': ds_name + '.xmi',
                            'path': '',
                            'element': {'date': datetime.now(utc)},
                            'content': xmi_content
                        },
                        ]
                    else:
                        print 'Skipping this path.'
                        ds_skipped.append(ds)
                        continue

                print 'Checking if the device server already exists in the catalogue...'

                if ds.get('repository_url', None) is not None:
                    r = self.client.get(SERVER_LIST_URL + ds.get('repository_url'), headers={'Referer': self.referrer})
                    self.referrer = SERVER_LIST_URL + ds.get('repository_url')
                else:
                    r = self.client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'], headers={'Referer': self.referrer})
                    self.referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']

                ds_on_server = r.json()

                if len(ds_on_server) > 1:
                    print 'There are %d device servers registered with this repository path. ' \
                          'Import utility does not handle such a case. Skipping.  ' % len(ds_on_server)
                    ds_skipped.append(ds)
                    continue

                if len(ds_on_server) == 1:
                    print 'This device server already exists in the catalogue. It will be updated if necessary.'
                    server_ds_pk, server_ds = ds_on_server.popitem()
                    ds_adding = False
                    if server_ds['last_update_method'] == 'manual':
                        print 'This device server has been updated manually on the server. It will not be updated via script.'
                        continue

                    if link_documentation:
                        for doc in server_ds['documentation']:
                            if doc['updated_by_script']:
                                if doc['title'] != documentation_title or doc['url'] != documentation_URL:
                                    documentation_pk = doc['pk']
                                    break
                                else:
                                    link_documentation = False

                else:
                    ds_adding = True
                    print 'This is a new device server. It will  be added to the catalogue.'

                ds_repo_url = ds.get('repository_url', REMOTE_REPO_URL + '/' + ds.get('path', ''))

                repository_tag = ds.get('tag', '')

                # prepare readme file for upload
                upload_readme = False

                if len(ds['readme_files']) > 0:
                    readme_file = ds['readme_files'][0]
                    readme_name = readme_file['name']
                    print 'There is a readme file: %s' % readme_name
                    if os.path.splitext(readme_name)[1] not in ['.txt', '.TXT', '.md', '.MD',
                                                                '', '.doc', '.DOC',
                                                                '.rst', '.RST',
                                                                '.pdf', '.PDF',
                                                                '.html', '.HTML', '.htm', '.HTM']:
                        print 'File with unknown extension skipped.'
                    else:
                        if ds_adding or FORCE_UPDATE or \
                                        date_parser.parse(server_ds['last_update']) < readme_file['element']['date']:

                            readme_url_response = urllib2.urlopen(readme_file.get('readme_url',
                                                                                  REMOTE_REPO_URL + '/' + readme_file[
                                                                                      'path']
                                                                                  + '/' + readme_file['name']))
                            readme_file_size = int(readme_url_response.info().get('Content-Length', 0))
                            if readme_file_size < 5 or readme_file_size > 2000000:
                                print 'Readme file size %d is out of limits. Skipping.' % readme_file_size
                            else:
                                print 'It will be uploaded.'
                                read_file_content = readme_url_response.read()
                                files['readme_file'] = (readme_name, read_file_content)
                                upload_readme = 1
                        else:
                            print 'Will skip the readme upload since it is elder than the last update of device server.'

                # Iterate through .XMIs and update catalogue
                first_xmi = True

                # check if any of the xmi needs update
                xmi_need_update = False
                for xmi in ds['xmi_files']:
                    if not ds_adding and date_parser.parse(server_ds['last_update']) < xmi['element']['date']:
                        xmi_need_update = True
                        break

                for xmi in ds['xmi_files']:
                    print "XMI file: %s" % xmi['name']

                    xmi_url = xmi.get('xmi_url', REMOTE_REPO_URL + '/' + xmi.get('path', '') + '/' + xmi.get('name'))
                    # skip
                    if str(xmi['name']).strip().lower().endswith('.multi.xmi'):
                        continue

                    if xmi.has_key('content'):
                        files['xmi_file'] = (xmi['name'], xmi['content'])
                        xmi_from_url = False

                    # prepare common data to be sent
                    data_to_send = {
                        'script_operation': True,
                        'ds_info_copy': auto_ds_name,
                        'development_status': development_status,
                        'name': ds_name,
                        'description': '',
                        'xmi_file_url': xmi_url,
                        'use_url_xmi_file': xmi_from_url,
                        'use_manual_info': False,
                        'use_uploaded_xmi_file': xmi_from_doc,
                        'available_in_repository': True,
                        'repository_url': ds_repo_url,
                        'repository_type': ds.get('repository_type', 'SVN'),
                        'repository_tag': repository_tag,
                        'upload_readme': False,
                    }

                    if first_xmi:
                        # documentation is updated only with the first xmi file
                        data_to_send.update({
                            'upload_readme': upload_readme,
                            'other_documentation1': link_documentation,
                            'documentation1_title': documentation_title,
                            'documentation1_url': documentation_URL,
                            'documentation1_pk': documentation_pk,
                            'documentation1_type': documentation_type,
                        })

                        if ds_adding:
                            # case when device server does not yet exists on the server
                            # connect to the adding form
                            self.client.get(SERVER_ADD_URL, headers={'Referer': self.referrer})  # sets the cookie
                            self.referrer = SERVER_ADD_URL
                            self.csrftoken = self.client.cookies['csrftoken']

                            # update data to be send to the form accordingly
                            data_to_send.update({
                                'csrfmiddlewaretoken': self.csrftoken,
                                'submit': 'create',
                            })

                            # send data to the server
                            r = self.client.post(SERVER_ADD_URL, data=data_to_send,
                                            files=files, headers={'Referer': self.referrer})

                            print 'Adding HTTP result code: %d' % r.status_code
                            add_result = r

                            # check if the catalogue is realy updated
                            sleep(1)
                            # list device servers in the repository
                            r = self.client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'],
                                           headers={'Referer': self.referrer})
                            self.referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']
                            ds_on_server = r.json()

                            # if there is exactly one device server it seems the adding was successful
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

                        elif FORCE_UPDATE or xmi_need_update:
                            # case when the device server already exists
                            print 'Updating with XMI: %s' % xmi['name']

                            # connect to update form
                            self.client.get(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/',
                                       headers={'Referer': self.referrer})
                            self.referrer = SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/'
                            self.csrftoken = self.client.cookies['csrftoken']

                            # update data to be sent via form
                            data_to_send.update({
                                'csrfmiddlewaretoken': self.csrftoken,
                                'last_update_method': server_ds['last_update_method'],
                                'description': '',
                                'add_class': False,
                                'only_github': FORCE_ONLY_GITHUB
                                               and not date_parser.parse(server_ds['last_update']) < xmi['element'][
                                    'date'],
                                'submit': 'update',
                            })

                            # send update form
                            r = self.client.post(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/',
                                            data=data_to_send,
                                            files=files, headers={'Referer': self.referrer})

                            print 'Update HTTP result: %d' % r.status_code
                            update_result = r

                            # check if the update successfully updated database
                            r = self.client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'],
                                           headers={'Referer': self.referrer})
                            self.referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']
                            ds_on_server = r.json()
                            if len(ds_on_server) == 1:
                                u_server_ds_pk, u_server_ds = ds_on_server.popitem()
                                if date_parser.parse(server_ds['last_update']) < date_parser.parse(
                                        u_server_ds['last_update']):
                                    server_ds = u_server_ds
                                    print '.XMI has been successfully updated in the catalogue.'
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
                            print 'Skipping update with the XMI: %s. Seems the catalogue is up to date for it.' % xmi[
                                'name']

                    elif ds_adding or FORCE_UPDATE \
                                   or xmi_need_update:
                        # case of updating subsequent .XMIs for multiple class device servers
                        print 'Updating with XMI: %s' % xmi['name']

                        # load update form
                        self.client.get(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/',
                                   headers={'Referer': self.referrer})
                        self.referrer = SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/'
                        self.csrftoken = self.client.cookies['csrftoken']

                        # updated data to be sent to the form
                        data_to_send.update({
                            'csrfmiddlewaretoken': self.csrftoken,
                            'ds_info_copy': False,
                            'last_update_method': server_ds['last_update_method'],
                            'add_class': True,
                            'upload_readme': False,
                            'submit': 'update',
                        })

                        r = self.client.post(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update/',
                                        data=data_to_send, headers={'Referer': self.referrer})
                        print 'Update result: %d' % r.status_code
                        xmi_updated += 1
                        sleep(1)
                    else:
                        xmi_not_changed += 1
                        print 'Skipping update with the XMI: %s. Seems the catalogue is up to date for it.' % xmi[
                            'name']

            except ZeroDivisionError as e:
                print e.message
                ds_problems.append(ds)

        print ''
        print '\nImport summary:'
        print '---------------------------'
        print 'Skippend %d device servers (no xmi files).' % len(ds_skipped)
        print 'Problems with %d device servers (errors in processing).' % len(ds_problems)
        print 'Count of updated or added XMI files: %d' % (xmi_added + xmi_updated)
        print 'Count of untouched (not changed) xmi files: %d ' % xmi_not_changed
        print '---------------------------'
        print ''
