
Tango Device Servers Catalogue import utiltiy
=============================================

The utility imports information from a subversion repository into the Device Servers Catalogue. The repository should be
publicly available through http. It does it in the following way:

- Make local copy of the repository to speed up a search for device servers procedure
- Search the local copy for folders containing .XMI files. It takes into account the standard branches/tags/trunk
  structure. The folders where it findes .xmi files or a proper structure are listed as candidates to be device servers.
- The list then is processed and compared (by repository URL) with content in the Catalogue.
- If there are changes the catalogue is updated



Requirements
------------

* Python2.7
* Subversion
* SVN python library :command "pip install svn"
* urllib2 library
* Requests library

Run
---

* Make your local branch to be sure your settings will not be overwritten by someone else...
* Update variables in `dsc_import_utility.py` to reflect your environment
* run with :command: python dsc_import_utility.py
    - It will ask you for login and password for tango-controls.org


