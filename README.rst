
Tango Device Servers Catalogue import utility
=============================================

The utility imports information from a subversion repository into the Device Servers Catalogue. The repository should be
publicly available through http.

Requirements
------------

- Python2.7
- Subversion
- SVN python library :command:`pip install svn`
    - The library will not work if any of file in the SVN has no author defined which is the case for tango-ds repository
      on the Sourceforge. To avoid problems one can edit :file:`svn/common.py` around line 358 to have something like
      the following:

      .. code-block:: python

                author = ''
                if commit_node.find('author') is not None:
                    author = commit_node.find('author').text

- lxml library
- urllib2 library
- Requests library version >= 2.12, you may need to run pip with --upgrade option

How-to import multiple classes
------------------------------

#. Clone import utility with git:
    - :command:`git clone https://github.com/piogor/dsc-import.git`

#. Get into folder:
    - :command:`cd dsc-import`

#. Make your local branch to be sure your settings will not be overwritten by someone else.
    - :command:`git checkout -b my_local_branch`

#. Update variables in :file:`settings.py` to reflect your environment:

    .. code-block:: python

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
        SERVER_BASE_URL = 'http://www.tango-controls.org/'
        # SERVER_BASE_URL = 'https://dsc-test.modelowanie.pl/'
        # SERVER_BASE_URL = 'http://localhost:8080/'

        # settings for catalogue configuration on the server
        SERVER_DSC_URL = SERVER_BASE_URL+'developers/dsc/'

        SERVER_ADD_URL = SERVER_BASE_URL+'developers/dsc/add/'

        SERVER_LIST_URL = SERVER_BASE_URL+'developers/dsc/list/?repository_url='

        SERVER_LOGIN_URL = SERVER_BASE_URL+'account/sign-in/?next=/developers/dsc/'

#. run with a :command:`python dsc_import_utility.py`

    - It will ask you for your credentials for tango-controls.org

How the script works
--------------------

It does import in the following way:

- For an SVN repository
    - It makes a local copy  (in path defined by `LOCAL_REPO_PATH`) of a SVN repository to speed up a search
      for device servers procedure.
    - Then, it searches the local copy for folders containing .XMI files. It takes into account the
      standard *branches/tags/trunk* structure. The folders where it finds .xmi files or a proper structure are listed
      as candidates to be device servers.

- Then, the list of candidates then is processed and compared (by repository URL) with content in
  the Device Classes Catalogue.

    - If there are changes or `FORCE_UPDATE` is True the catalogue is updated
        - For device server without .XMI file it looks for documentation server and tries to parse html documentation
          generated by :program:`Pogo`.

    - If there ara no changes the device server is skipped