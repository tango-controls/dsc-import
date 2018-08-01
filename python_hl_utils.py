"""
    (c) by Piotr Goryl, S2Innoavation, 2018 for Tango Controls Community

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

import urllib2
import re
from lxml import etree

from xmi_utils import *
from python_utils import get_class_content

# regular experssions to detect various components
REGEX_DEVICE_CLASS = re.compile(r"class\s+(?P<class_name>\w+)\s*[(]\s*((tango.)|(PyTango.))*Device\s*[)]")

REGEX_ATTR_START = re.compile(r"\s*(?P<attr_name>\w+)\s*=\s*attribute\s*[(]")

def get_attribute_xml(source_lines, start_index, name, class_xml):
    """
    Generate attri
    :param source_lines:
    :param start_index:
    :param class_xml:
    :return: (attribute_xml, end_index) where attribute_xml is a return node and end_index is line number where
             attribute definition ends
    """



    # prepare xml element
    attribute_xml = etree.SubElement(class_xml, 'attributes')
    attribute_xml.set('name', name)

    # TODO: implement parsing for attribute


    # find content of the attrib definition (part between brackets)
    no_brackets_open = 0 # this will count 'internal' brackets (one which belongs to attributes properties)

    # loop over lines belonging to attribute definition
    index = start_index

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # strip the first line from  '.. = attribute('
        if index == start_index:
            line = REGEX_ATTR_START.sub("", line)

        # check for data type
        dtype_image_match = re.match(r"""dtype\s*=\s*[[(]\s*[([]\s*['"](P<dtype>\w+)['"]\s*,?\s*[)\]]\s*,?\s*[)\]]""")

        dtype_spectrum_match = re.match(r"""dtype\s*=\s*[([]\s*['"](P<dtype>\w+)['"]\s*,?\s*[)\]]""")

        dtype_scalar_match = re.match(r"""dtype\s*=\s*['"](P<dtype>\w+)['"]""")

        if dtype_image_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + PYTHON_DS_ATTRIBUTE_DATATYPES.get(dtype_image_match.group('dtype'), "StringType")
                }
            )

            attribute_xml.set('attType', 'Image')

        if dtype_spectrum_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + PYTHON_DS_ATTRIBUTE_DATATYPES.get(dtype_spectrum_match.group('dtype'), "StringType")
                }
            )

            attribute_xml.set('attType', 'Spectrum')

        if dtype_scalar_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + PYTHON_DS_ATTRIBUTE_DATATYPES.get(dtype_scalar_match.group('dtype'), "StringType")
                }
            )

            attribute_xml.set('attType', 'Scalar')

        # check for

        # check for attribute definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0:
            break

        index += 1

    return attribute_xml, 0

def get_class_xml(source_lines, name, xmi_xml):
    """
    Generates class relate xml element form lines selected

    :param source_lines:
    :param name:
    :param xmi_xml:
    :return:
    """
    classes_xml = etree.SubElement(xmi_xml, 'classes')
    classes_xml.set('name', name)
    description_xml = etree.SubElement(classes_xml, 'description')
    identification_xml = etree.SubElement(description_xml, 'identification')

    # iteration over lines
    index = 0  # use indexing instead of iterator
    while index < len(source_lines):

        line = source_lines[index]

        # look for attribute definition
        attr_mo = REGEX_ATTR_START.match(line)
        if attr_mo is not None:
            (attr_xml, end_index) = get_attribute_xml(source_lines, index, attr_mo.gropup('attr_name'), classes_xml)
            index = end_index


        # TODO: commands, pipes, class and device properties


        # increment index
        index += 1

    return classes_xml


def get_xmi_from_python_hl(name, family, python_file_url, element = None):
    """
    Generates xmi file content from a parsed Python HL device server

    :param name: name of the device server
    :param family: family name
    :param python_file_url: URL of the python file
    :return: content of xmi file derived from the python source
    """

    # base for xmi
    xmi_xml = etree.fromstring(
        """<?xml version="1.0" encoding="ASCII"?>
        <pogoDsl:PogoSystem xmi:version="2.0"
        xmlns:xmi="http://www.omg.org/XMI"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:pogoDsl="http://www.esrf.fr/tango/pogo/PogoDsl">
        </pogoDsl:PogoSystem>"""
    )

    # open url
    url_response = urllib2.urlopen(python_file_url)
    size = int(url_response.info().get('Content-Length', 0))
    if size < 10 or size > 500000:
        print
        print "Python file size out of limits. "
        return None

    # read the file
    ds_source = url_response.read()
    assert isinstance(ds_source, str)
    source_lines = ds_source.splitlines()

    author = ''
    copyleft = ''
    comment_buffer = ''

    # generate xmi
    classes_xml = None
    description_xml = None
    identification_xml = None
    in_comment = False

    index = 0

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # check if we start class
        if line.strip().startswith('class'):
            mo = REGEX_DEVICE_CLASS.match(line.strip())
            if mo is not None:
                # if not device class
                classes_xml = get_class_content(source_lines, mo.group('class_name'), xmi_xml)


