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
from pytz import utc
from datetime import datetime
import urlparse
import urllib2
import sys


def get_device_servers_list():
    """
        This function is creating a device servers list based on environment variables

        :returns a list of device servers compatible with the import script

        Environment variables in use:

        * `DSC_XMI_URL` or `DSC_PYTHON_URL` or `DSC_JAVA_URL` defines where to find information
          to get or build and .xmi file. One of these shall be provided,
        * `DSC_DEVICE_SERVER_NAME` - to specify device server name,
        * `DSC_REPOSITORY_URL` to specify URL of the repository,
        * `DSC_REPOSITORY_TYPE` should be one of: `GIT`, `SVN`, `Mercurial`, `FTP`, `Other`,
        * Optional `DSC_RELEASE_TAG` to specify device server release,
        * Optional `DSC_README_URL` - to specify where to find a README file for this device class,
        * Optional `DSC_DOC_URL` - to specify additional documentation for this DS,
        * Optional `DSC_DOC_TITLE` - to specify title of additional documentation,
        * Optional `DSC_DOC_TYPE` - to specify title of additional documentation,
        * Optional `DSC_DEVICE_SERVER_DESCRIPTION` - to specify/override device server description,
        * Optional `DSC_REPOSITORY_CONTACT` - to provide or override contact info in .xmi file,
        * Optional `DSC_FAMILY` - to provide or override family info in.xmi file,
        * Optional `DSC_LICENSE` - to provide or override license info in .xmi file,
        * Optional `DSC_AUTHOR` - to provide or override author info in .xmi file,
        * Optional `DSC_CLASS_DESCRIPTION` - to provide or override class description info in .xmi file,
        * Optional `DSC_URL_IS_LOCAL` - if True, an XMI file is provided to the server with its content read locally.

    """

    # this is the list to be returned
    ds_list = []

    # this is a dict of a device server
    ds = {
        'name': os.environ.get('DSC_DEVICE_SERVER_NAME'),
        'description': os.environ.get('DSC_DEVICE_SERVER_DESCRIPTION'),
        'xmi_files': [],
        'py_files': [],
        'java_files': [],
        'readme_files': [],
        'repository_url': os.environ.get('DSC_REPOSITORY_URL'),
        'repository_type': os.environ.get('DSC_REPOSITORY_TYPE'),
        'repository_contact': os.environ.get('DSC_REPOSITORY_CONTACT'),
        'tag': os.environ.get('DSC_RELEASE_TAG', os.environ.get('DSC_REPOSITORY_TAG', '')),
        'meta_data': {
            'family': os.environ.get('DSC_FAMILY'),
            'class_description': os.environ.get('DSC_CLASS_DESCRIPTION'),
            'license': os.environ.get('DSC_LICENSE'),
            'author': os.environ.get('DSC_AUTHOR'),
        },
    }

    # get the URL
    url = ''
    file_key = None

    if os.environ.get('DSC_XMI_URL') not in [None, '']:
        url = os.environ.get('DSC_XMI_URL')
        file_key = 'xmi'

    elif os.environ.get('DSC_PYTHON_URL') not in [None, '']:
        url = os.environ.get('DSC_PYTHON_URL')
        file_key = 'py'

    elif os.environ.get('DSC_JAVA_URL') not in [None, '']:
        url = os.environ.get('DSC_JAVA_URL')
        file_key = 'java'

    # retrieve information from the URL
    url_parts = urlparse.urlsplit(url)

    ds['{0}_files'.format(file_key)].append({
        'name': url_parts.path.split('/')[-1],
        '{0}_url'.format(file_key): url,
        'element': {'date': datetime.now(utc)},
    })

    # to allow import from non-public repositories, xmi file content will be loaded locally
    if file_key == 'xmi' and \
            (eval(os.environ.get('DSC_URL_IS_LOCAL', "False")) or os.environ.get('DSC_XMI_URL').startswith('file://')):

        print 'Reading a .XMI file locally...'
        url_response = urllib2.urlopen(os.environ.get('DSC_XMI_URL'))
        size = int(url_response.info().get('Content-Length', 0))
        if size < 10 or size > 50000:
            sys.exit("XMI file size out of limits. ")
        # read the file
        xmi_source = url_response.read()
        ds['xmi_files'][0]['content'] = xmi_source

    # add a readme if available
    if os.environ.get('DSC_README_URL') not in [None, '']:
        url_parts = urlparse.urlsplit('DSC_README_URL')
        ds['readme_files'].append({
            'name': url_parts.path.split('/')[-1],
            'path': '',
            'readme_url': os.environ.get('DSC_README_URL'),
            'element': {'date': datetime.now(utc)},
        })

    # process other documentation
    if os.environ.get('DSC_DOC_URL') not in [None, '']:
        ds['documentation_url'] = os.environ.get('DSC_DOC_URL')
        ds['documentation_title'] = os.environ.get('DSC_DOC_TITLE', 'Generated by Pogo')
        ds['documentation_type'] = os.environ.get('DSC_DOC_TYPE', 'Generated')

    # remove None from metadata
    clean_mata = dict((k, v) for (k, v) in list(ds['meta_data'].iteritems()) if v is not None)
    ds['meta_data'] = clean_mata

    ds_list.append(ds)

    return ds_list
