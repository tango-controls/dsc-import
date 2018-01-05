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

import csv
from pytz import utc
from datetime import datetime
import urllib2


def get_device_servers_list(csv_file_path):
    """
        This function is creating a device servers list from a csv file

        :param csv_file_path pathg to CSV file
        :returns a list of device servers compatible with the import script

        CSV file format:
        The first row defines columns' meaning and folowing rows provides content
        "name" - provides name of the device server
        "repository_url" - provides URL to repository (with path)
        "repository_type" - provides type of repository
        "tag" - release tag
        "xmi_files_urls" - provides url (http://, https:// or file://) to an xmi file.
        "pogo_docs_url_base" - provides base url for pogo generated docs that may be parsed to get xmi file for non-xmi
                               devcice server
        "upload_xmi_file" - If False or empty, the upload form will be provided with the url and the catalogue will
                            download the file. If True, the file will be downloaded by the script, then uploaded
                            to the catalogue form
        "readme_url" - URL of a readme file
        "readme_name" - filename of the readme (with proper extension)
        "documentation_url" - URL of documentation
        "documentation_title" - title of the document
        "documentation_type" - type of documentation, one of the following
                               ['README', 'Manual', 'InstGuide','Generated', 'SourceDoc']


    """

    # this is the list to be returned
    ds_list = []

    # open the file
    with open(csv_file_path, 'rb') as csv_file:

        # treat the file as dictionary
        rows = csv.DictReader(csv_file)
        row_index = 0

        # iterate through rows
        for row in rows:
            # just for counting:
            row_index += 1

            try:

                ds = dict()

                ds['name'] = row.get('name', '')

                # process repository info
                ds['repository_url'] = row.get('repository_url', None)
                if ds['repository_url'] is None:
                    # device server shell be available in some repository
                    print 'Device server %s is not in any repository.' % ds['name']
                    continue

                ds['repository_type'] = row.get('repository_type', '')
                if len(ds['repository_type'].strip()) == 0:
                    ds['repository_type'] = 'SVN'

                if len(row.get('tag', '')) > 0:
                    ds['tag'] = row.get('tag', '')

                # process .xmi related columns
                xmi_urls_list = []
                xmi_files = []
                if row.get('xmi_files_urls', '').startswith('['):
                    xmi_urls_list = eval(row.get('xmi_files_urls'))
                elif len(row.get('xmi_files_urls', '')) > 0:
                    xmi_urls_list[0] = row.get('xmi_files_urls')

                index = 0
                for xmi_url in xmi_urls_list:

                    xmi = {
                        'name': ds['name']+str(index)+'.xmi',
                        'path': '',
                        'element': {'date': datetime.now(utc)},
                        'xmi_url': xmi_url,
                    }

                    if row.get('upload_xmi_file', '') in [1, '1', 'true', 'True']:
                        # download content of the xmi file then upload it to the catalogue
                        xmi['content'] = urllib2.urlopen(xmi_url).read()

                    xmi_files.append(xmi)

                    index += 1

                ds['xmi_files'] = xmi_files

                # for device servers featuring pogo documentation but no .xmi:
                if len(row.get("pogo_docs_url_base", '')) > 0:
                    ds['pogo_docs_url_base'] = row.get("pogo_docs_url_base")

                # process readme related columns
                ds['readme_files'] = []

                if len(row.get('readme_url', '')) > 0:

                    ds['readme_files'].append({
                        'name': row.get('readme_name', 'README.txt'),
                        'path': '',
                        'readme_url': row.get('readme_url'),
                        'element': {'date': datetime.now(utc)},
                    })

                # process other documentation related columns
                if len(row.get('documentation_url', '')) > 0:
                    ds['documentation_url'] = row.get('documentation_url')
                    ds['documentation_title'] = row.get('documentation_title', 'Generated by Pogo.')
                    ds['documentation_type'] = row.get('documentation_type', 'Generated')

                # append device servers list
                ds_list.append(ds)

            except Exception as e:
                print
                print 'Error in processing row %d: ' % row_index
                print e.message
                print
                print 'This device server will not be included in an update list.'

    return ds_list
