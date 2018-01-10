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

import urllib2
import re
from lxml import etree

from xmi_utils import *


class DefaultCopyDict(dict):
    """ Just to provide a dictionary with default value for a missing keys """

    def __missing__(self, key):
        return key


class PyTangoClass:
    """ This is a mock class to allow eval on member lists"""

    def __init__(self):

        # build conversion table
        conversion_table = DefaultCopyDict()
        conversion_table.update(DS_ATTRIBUTE_DATATYPES_REVERS)
        conversion_table.update(DS_COMMAND_DATATYPES_REVERS)
        conversion_table.update({
            "READ": "READ",
            "READ_WRITE": "READ_WRITE",
            "WRITE": "WRITE",
            "READ_WITH_WRITE":  "READ_WITH_WRITE",
            "IMAGE": "Image",
            "SPECTRUM": "Spectrum",
            "SCALAR": "Scalar"
        })

        # do a trick to populate PyTango class with conversion members
        # self.__class__.__dict__ = conversion_table
        self.__dict__ = conversion_table

# PyTango mock
PyTango = PyTangoClass()


def get_line_indentation(line):
    """ Returns indentation of the line"""
    assert isinstance(line, str)
    return len(line)-len(line.lstrip())


def get_class_content(source_lines, class_name):
    """ Provides only lines defining class content
    :return: lines belonging to class
    """
    class_started = False
    class_indentation = 0
    class_lines = []

    # regular expression to detect class definition
    match_string = r'(\s*class\s+)(?P<class_name>'+class_name+r')(.+)'
    expr = re.compile(match_string)

    for line in source_lines:

        assert isinstance(line, str)

        if not class_started:
            # detect beginning of class
            match_result = expr.match(line)

            if match_result is None:
                continue

            # if match_result.group('class_name').strip() == class_name:
            else:
                class_started = True
                class_indentation = get_line_indentation(line)
                class_lines.append(line)

        elif get_line_indentation(line) > class_indentation \
                or line.lstrip().startswith('#') \
                or len(line.strip()) == 0:

            # add all lines indented properly and comments
            class_lines.append(line)

        else:
            # this is a case when the line is first one not belonging to the class
            break

    return class_lines


def get_class_dict_member(source_lines, member_name):
    """
    Returns (eval) dictionary class member value. Useful for finding lists of attributes, commands and properties
    in device class definition
    :param source_lines: source content
    :param member_name: name of a member to read from class definition
    :return:
    """

    match_string = r'\s*'+member_name+'\s*=\s*(?P<content>.*)'
    expr = re.compile(match_string)

    member_found = False
    brackets_count = 0
    to_eval = ''

    for line in source_lines:

        assert isinstance(line, str)

        if not member_found:
            # find beginning of member
            match_result = expr.match(line)

            if match_result is not None:
                # fund match, limit line to the content
                member_found = True
                line = match_result.group('content').strip()
            else:
                continue

        if member_found and not line.lstrip().startswith('#'):
            # updated bracket bilans
            brackets_count += line.count('{') - line.count('}')
            # add line to be evaluated
            to_eval += '\n' + line

            if brackets_count == 0:
                # the closing bracket found
                break

    # return evaluation of the member
    return eval(to_eval)


def get_class_member_comment(source_lines, member_name):
    """
    Get comment located just before a class member or its doc string.
    :param source_lines: source content
    :param member_name: name of a member
    :return: (comment, docstring)
    """
    pass


def get_xmi_from_python(name, family, python_file_url):
    """

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

    # find description part (comment)
    description_started = False
    class_description = ''
    for line in source_lines:
        if line.startswith("# %s Class Description" % name):
            description_started = True

        if description_started:
            if line.startswith('#==========================='):
                # end of description
                break

            class_description += line + '\n'

    # find Tango class definition
    class_source = get_class_content(source_lines, name + 'Class')

    # get list of attributes
    attr_list = get_class_dict_member(class_source, "attr_list" )

    # get list of commands
    cmd_list = get_class_dict_member(class_source, "cmd_list" )

    # get list of class properties
    class_property_list = get_class_dict_member(class_source, "class_property_list" )

    # get list of device properties
    device_property_list = get_class_dict_member(class_source, "device_property_list" )

    # generate xmi
    classes_xml = etree.SubElement(xmi_xml, 'classes')
    description_xml = etree.SubElement(classes_xml, 'description')
    identification_xml = etree.SubElement(description_xml, 'identification')

    return '<?xml version="1.0" encoding="ASCII"?>' + etree.tostring(xmi_xml)


if __name__ == "__main__":
    # main function perform tests

    py_file1 = 'test-assets/BakeOutControlDS.py'

    py_file2 = 'test-assets/LOCOSplitter.py'

    with open(py_file1) as f:
        source = f.read()

        class_content = get_class_content(source.splitlines(), 'BakeOutControlDSClass')

        print class_content

        print 'Device properties:'
        print get_class_dict_member(class_content, 'device_property_list')
        print 'Class properties:'
        print get_class_dict_member(class_content, 'class_property_list')
        print 'Attributes:'
        print get_class_dict_member(class_content, 'attr_list')
        print 'Commands:'
        print get_class_dict_member(class_content, 'cmd_list')
        print

    with open(py_file2) as f:
        source = f.read()

        class_content = get_class_content(source.splitlines(), 'LOCOSplitterClass')

        print class_content

        print 'Device properties:'
        print get_class_dict_member(class_content, 'device_property_list')
        print 'Class properties:'
        print get_class_dict_member(class_content, 'class_property_list')
        print 'Attributes:'
        print get_class_dict_member(class_content, 'attr_list')
        print 'Commands:'
        print get_class_dict_member(class_content, 'cmd_list')
        print

