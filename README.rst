
Tango Device Servers Catalogue import utiltiy
=============================================

The utility imports information from a subversion repository into the Device Servers Catalogue. The repository should be
publicly available through http. It does it in the following way:

# Make local copy of the repository to speed up a search for device servers procedure
# Search the local copy for folders containing .XMI files. It takes into account the standard _branches/tags/trunk_
  structure. The folders where it findes .xmi files or a proper structure are listed as candidates to be device servers.
# The list then is processed and compared (by repository URL) with content in the Catalogue.
    # If there are changes the catalogue is updated
    # If not the device server is skipped



Requirements
------------

- Python2.7
- Subversion
- SVN python library :command "pip install svn"
- urllib2 library
- Requests library version >= 2.12, you may need to run pip with --upgrade option

Run
---

- Make your local branch to be sure your settings will not be overwritten by someone else...
- Update variables in :file:`dsc_import_utility.py` to reflect your environment:

.. code-block:: python

    FORCE_UPDATE = False  # when True no timestamp are checked and updates are performed
    TEST_SERVER_AUTH = False  # Set true if script is run against test server with additional authentication (webu test)
    VERIFY_CERT = False  # set this to false if running aginst test server without a valid certificate

    # set the following variables to point to the repositories
    LOCAL_REPO_PATH = '/home/piotr/tmp/tango-ds-repo/'  # local copy of the repository will be synced there
    LOG_PATH = '/home/piotr/tmp'  # where to log some information about import process, not used now.

    REMOTE_REPO_HOST = 'svn.code.sf.net'  # host of the SVN repository
    REMOTE_REPO_PATH = 'p/tango-ds/code'  # path within the SVN server

    # if one would like to limit a search tree (useful for one device server update and/or tests)
    REPO_START_PATH = 'DeviceClasses'  # do not provide start nor end slashes

    # Tango Controls or test server address
    SERVER_BASE_URL = 'http://www.tango-controls.org/'

- run with :command:`python dsc_import_utility.py`
    - It will ask you for your credentials for tango-controls.org
