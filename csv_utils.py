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
import csv



def get_device_servers_list(csv_file_path):
    """
        This module is creating a device servers list from csv file and
        :param csv_file_path pathg to CSV file
        :returns a list of device servers compatible with the import script

        CSV file format:
        The first row defines columns' meaning and folowing rows provides content
        "name" - provides name of the device server
        "repository_url" - provides URL to repository (with path)
        "xmi_file" - provides url (http:// or https://) or path to an xmi file.
        "upload_xmi_file" - If False or empty, the upload form will be provided with the url and the catalogue will download
                         the file. If True, the file will be downloaded by the script, then uploaded to the catologue
                         form
        "tag" - release tag

    """

    ds_list = []

    with open(csv_file_path, 'rb') as csv_file:

        # treat the file as dictionary
        rows = csv.DictReader(csv_file)

        # iterate through rows
        for row in rows:

            ds = dict()

            ds['name'] = row.get('name','')
            ds['repository_url'] = row.get('repository_url', None)

            if len(row.get('tag','')) > 0:
                ds['tag'] = row.get('tag')




