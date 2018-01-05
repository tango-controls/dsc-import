FORCE_UPDATE = False  # when True no time stamps are checked and updates are performed for all valid device servers
USE_DOC_FOR_NON_XMI = False # when True, parse documentation to get xmi conntent for device servers without XMI
ADD_LINK_TO_DOCUMENTATION = True # when True it provides a link to documentation
FORCE_ONLY_GITHUB = False  # when true only force update of github (to initialy polpulate it with data)

TEST_SERVER_AUTH = False  # Set true if script is run against test server with additional  authentication (webu test)
VERIFY_CERT = False  # set this to false if running aginst test server without a valid certificate

# if credentials below are None the script will ask for it with termina
USER_LOGIN = None
USER_PASSWORD = None
# one can provide cred.py locally to run script automatically (please not add it to git)
# import cred
# USER_LOGIN = cred.T_USER
# USER_PASSWORD = cred.T_PASSWORD

# set the following variables to point to the repositories

LOCAL_REPO_PATH = '/home/ubuntu/dsc-import/tango-repo'  # local copy of the repository
LOG_PATH = '/home/ubuntu/dsc-import/log'  # where to log some information about import process, not used now.

REMOTE_REPO_HOST = 'svn.code.sf.net'  # host of a SVN repository
REMOTE_REPO_PATH = 'p/tango-ds/code'  # path within SVN server

# URLs for accessing SVN repositories
REMOTE_REPO_URL = 'http://%s/%s' % (REMOTE_REPO_HOST, REMOTE_REPO_PATH)
LOCAL_REPO_URL = 'file://%s' % LOCAL_REPO_PATH

# command used to synchronize local SVN repository with the remote one
REPO_SYNC_COMMAND = 'rsync -av %s::%s/* %s' % (REMOTE_REPO_HOST, REMOTE_REPO_PATH, LOCAL_REPO_PATH)

# if one would like to limit searched treee (useful for one device server update and or tests)
# do not provide start nor end slashes
REPO_START_PATH = 'DeviceClasses'

# used for a diagnostic
FAMILY_FROM_PATH_PARSER = r'DeviceClasses/([A-Za-z]*)/.*'

# this is to provide links to documentation or to define an interface
DOCUMENTATION_BASE_URL = 'http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/'

# Tango Controls or test server address
# SERVER_BASE_URL = 'http://www.tango-controls.org/'
SERVER_BASE_URL = 'https://dsc-test.modelowanie.pl/'
# SERVER_BASE_URL = 'http://localhost:8080/'

# settings for catalogue configuration on the server
# SERVER_DSC_URL = SERVER_BASE_URL+'developers/dsc/'
#
# SERVER_ADD_URL = SERVER_BASE_URL+'developers/dsc/add/'
#
# SERVER_LIST_URL = SERVER_BASE_URL+'developers/dsc/list/?repository_url='
#
# SERVER_LOGIN_URL = SERVER_BASE_URL+'account/sign-in/?next=/developers/dsc/'

# old server layout settings (for testing on dsc-test.modelowanie.pl
SERVER_DSC_URL = SERVER_BASE_URL+'resources/dsc/'

SERVER_ADD_URL = SERVER_BASE_URL+'resources/dsc/add/'

SERVER_LIST_URL = SERVER_BASE_URL+'resources/dsc/list/?repository_url='

SERVER_LOGIN_URL = SERVER_BASE_URL+'account/sign-in/?next=/resources/dsc/'
