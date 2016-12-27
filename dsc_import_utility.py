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
from time import sleep

FORCE_UPDATE = False  # when True no time stamp are checked and updates are performed
TEST_SERVER_AUTH = False  # Set true if script is run against test server with additional authentication (webu test)
VERIFY_CERT = False  # set this to false if running aginst test server without a valid certificate

# set the following variables to point to the repositories

LOCAL_REPO_PATH = '/home/piotr/tmp/tango-ds-repo/'  # local copy of the repository
LOG_PATH = '/home/piotr/tmp'  # where to log some information about import process

REMOTE_REPO_HOST = 'svn.code.sf.net'  # host of a SVN repository
REMOTE_REPO_PATH = 'p/tango-ds/code'  # path within SVN server

# Tango Controls or test server address
SERVER_BASE_URL = 'https://dsc-test.modelowanie.pl/'

# command used to synchronize local repository with the remote one
REPO_SYNC_COMMAND = 'rsync -av %s::%s/* %s' % (REMOTE_REPO_HOST, REMOTE_REPO_PATH, LOCAL_REPO_PATH)

# URLs for accessing repositories
REMOTE_REPO_URL = 'http://%s/%s' % (REMOTE_REPO_HOST, REMOTE_REPO_PATH)
LOCAL_REPO_URL = 'file://%s' % LOCAL_REPO_PATH

# if one would like to limit searched treee (useful for one device server update and or tests)
# do not provide start nor end slashes
REPO_START_PATH = 'DeviceClasses'


# settings for catalogue configuration on the server
SERVER_DSC_URL = SERVER_BASE_URL+'resources/dsc/'

SERVER_ADD_URL = SERVER_BASE_URL+'resources/dsc/add/'

SERVER_LIST_URL = SERVER_BASE_URL+'resources/dsc/list/?repository_url='

SERVER_LOGIN_URL = SERVER_BASE_URL+'account/sign-in/?next=/resources/dsc/'

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
    login = raw_input('Basic auth login: ')
    password = getpass('Basic aoth password: ')
    client.get(SERVER_LOGIN_URL, auth=requests.auth.HTTPBasicAuth('user', 'pass'))  # sets the cookie
else:
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
        if len(ds['xmi_files'])==0:
            print 'No .xmi files found in this path. Skipping.'
            ds_skipped.append(ds)
            continue

        print 'Check if device server already exists in the catalogue...'

        r = client.get(SERVER_LIST_URL+REMOTE_REPO_URL+'/'+ds['path'], headers={'Referer':referrer})
        referrer = SERVER_LIST_URL+REMOTE_REPO_URL+'/'+ds['path']
        ds_on_server = r.json()
        print "Devcie servers in the catalogu: "
        print  ds_on_server
        if len(ds_on_server)>1:
            print 'There are %d device servers registered with this repository path. ' \
                  'Import utility does not handle such case. Skipping.  '
            ds_skipped.append(ds)
            continue

        files = {}

        if len(ds_on_server)==1:
            print 'This device server already exists in catalogue. Will do update if necessary.'
            server_ds_pk, server_ds = ds_on_server.popitem()
            ds_adding = False
        else:
            ds_adding = True
            print 'This is a new device server. Will add to catalogue.'

        ds_repo_url = REMOTE_REPO_URL + '/' + ds['path']

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
                print 'Will skip file of unknown extension.'
            else:

                if ds_adding or FORCE_UPDATE or \
                        date_parser.parse(server_ds['last_update']) < readme_file['element']['date']:
                    print "README date on SVN: %s" % readme_file['element']['date']
                    print "README date in the catalogue: %s" % date_parser.parse(server_ds['last_update'])
                    # get file from the server
                    readme_url_response = urllib2.urlopen(REMOTE_REPO_URL+'/'+readme_file['path'])
                    readme_file_size = int(readme_url_response.info().get('Content-Length',0))
                    if readme_file_size < 5 or readme_file_size > 2000000:
                        print 'Readme file sieze %d is out of limits. Skipping.' % readme_file_size
                    else:
                        print 'It will be uploaded.'
                        read_file_content=readme_url_response.read()
                        files = {'readme_file': (readme_name, read_file_content)}
                        upload_readme = 1
                else:
                    print 'Will skip the readme upload since it is elder than the last update of device server.'


        # xmis
        first_xmi=True
        ds_name = os.path.basename(ds['path'])
        if len(ds_name)>0:
            auto_ds_name = False
        else:
            auto_ds_name = True

        for xmi in ds['xmi_files']:
            print "XMI file: %s" % xmi['name']
            xmi_url = REMOTE_REPO_URL + '/' + xmi['path'] + '/' + xmi['name']

            if first_xmi:
                if ds_adding:
                    client.get(SERVER_ADD_URL, headers={'Referer':referrer})  # sets the cookie
                    referrer = SERVER_ADD_URL
                    csrftoken = client.cookies['csrftoken']
                    r = client.post(SERVER_ADD_URL,
                                data={
                                    'csrfmiddlewaretoken': csrftoken,
                                    'ds_info_copy': auto_ds_name,
                                    'name': ds_name,
                                    'description': '',
                                    'xmi_file_url':xmi_url,
                                    'use_url_xmi_file': 1,
                                    'use_manual_info': False,
                                    'use_uploaded_xmi_file': False,
                                    'repository_url': ds_repo_url,
                                    'repository_type': 'SVN',
                                    'upload_readme': upload_readme,
                                    'submit': 'create',
                                    'available_in_repository': True
                                },
                                files=files,  headers={'Referer':referrer})
                    first_xmi = False
                    xmi_added += 1
                    print 'Adding result: %d' % r.status_code

                    sleep(1)
                    r = client.get(SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path'],  headers={'Referer':referrer})
                    referrer = SERVER_LIST_URL + REMOTE_REPO_URL + '/' + ds['path']
                    ds_on_server = r.json()
                    if len(ds_on_server) == 1:

                        server_ds_pk, server_ds = ds_on_server.popitem()
                    else:
                        print 'It seems the device server has not been added to the catalogue...'
                        ds_problems.append(ds)
                        continue
                elif upload_readme or FORCE_UPDATE or date_parser.parse(server_ds['last_update'])<xmi['element']['date']:
                    print 'Updating with XMI: %s' % xmi['name']
                    client.get(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update', headers={'Referer':referrer})
                    referrer = SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update'
                    csrftoken = client.cookies['csrftoken']
                    r = client.post(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update',
                                data={
                                    'csrfmiddlewaretoken': csrftoken,
                                    'ds_info_copy': auto_ds_name,
                                    'name': ds_name,
                                    'description': '',
                                    'add_class': False,
                                    'xmi_file_url':xmi_url,
                                    'use_url_xmi_file': 1,
                                    'use_manual_info': False,
                                    'use_uploaded_xmi_file': False,
                                    'repository_url': ds_repo_url,
                                    'repository_type': 'SVN',
                                    'upload_readme': upload_readme,
                                    'submit': 'update',
                                    'available_in_repository': True
                                },
                                files=files, headers={'Referer':referrer})
                    print 'Update result: %d' % r.status_code
                    xmi_updated += 1
                    first_xmi = False
                    sleep(1)
                else:
                    xmi_not_changed += 1
                    print 'Skipping update with the XMI: %s. Seems the catalogue is up to date for it.' % xmi['name']

            elif ds_adding or FORCE_UPDATE or date_parser.parse(server_ds['last_update']) < xmi['element']['date']:
                print 'Updating with XMI: %s' % xmi['name']
                client.get(SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update', headers={'Referer':referrer})
                referrer = SERVER_DSC_URL + 'ds/' + str(server_ds_pk) + '/update'
                csrftoken = client.cookies['csrftoken']
                r = client.post(SERVER_DSC_URL+'ds/'+str(server_ds_pk)+'/update',
                            data={
                                'csrfmiddlewaretoken': csrftoken,
                                'ds_info_copy': False,
                                'name': ds_name,
                                'description': '',
                                'add_class': True,
                                'xmi_file_url':xmi_url,
                                    'use_url_xmi_file': True,
                                    'use_manual_info': False,
                                    'use_uploaded_xmi_file': False,
                                    'repository_url': ds_repo_url,
                                    'repository_type': 'SVN',
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

print 'Skippend %d device servers (no xmi files).' % len(ds_skipped)
print 'Problems with %d device servers (errors in processing).' % len(ds_problems)

print 'Count of updated or added XMI files: %d' % (xmi_added+xmi_updated)
print 'Count of untouched (not changed) xmi files: %d ' % (xmi_not_changed)






