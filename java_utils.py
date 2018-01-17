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


def get_xmi_from_java(name, family, java_file_url, element=None):
    """
    Parse a java file and generates xmi based on its contents
    :param name: name of the device server
    :param family: family name
    :param java_file_url: URL of the java file
    :param element: SVN element related to this file (to get some additional information)
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
    url_response = urllib2.urlopen(java_file_url)
    size = int(url_response.info().get('Content-Length', 0))
    if size < 10 or size > 500000:
        print
        print "Java file size out of limits. "
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
        # capture comments to be used for description
        if line.strip().startswith("/*"):
            comment_buffer = ''
            in_comment = True

        if line.strip().endswith("*/"):
            in_comment = False

        if in_comment:
            comment_buffer += line.strip().lstrip('*') + '\n'

        # capture class definition
        if line.strip().startswith('@Device'):

            # clean comment buffer from html tags for class description
            class_description = re.sub('</p>', '\n\n', comment_buffer)
            class_description = re.sub('<br/>', '\n\n', class_description)
            class_description = re.sub('<br />', '\n\n', class_description)
            class_description = re.sub('<b>\s*', '*', class_description)
            class_description = re.sub('\s*</b>', '*', class_description)
            class_description = re.sub(r"<a\s+[^>]*href=['\"](?P<hhref>[^'\"]+)['\"][^>]*(?=>)>\s*</a>", " \g<hhref> ",
                                       class_description)
            class_description = re.sub('<[^<>a/]+?>', '', class_description)
            class_description = re.sub('</[^a<>]+?>', '', class_description)
            class_description = re.sub(
                r"<a\s+[^>]*href=['\"](?P<hhref>[^'\"]+)['\"][^>]*(?=>)>(?P<text>[\s[^<]]+(?=</a>))</a>",
                ' `\g<text> <\g<hhref>>`_ ', class_description)

            comment_buffer = ''

            # get class name
            index += 1
            line = source_lines[index]
            match_result = re.match(r".*(?=class)class\s+(?P<class_name>[^\s({:]+)", line)

            if match_result is None:
                continue

            else:
                class_name = match_result.group('class_name')

                # xml elements
                classes_xml = etree.SubElement(xmi_xml, 'classes')
                description_xml = etree.SubElement(classes_xml, 'description')
                identification_xml = etree.SubElement(description_xml, 'identification')

                # provides attributes
                classes_xml.set('name', class_name)

                identification_xml.set('classFamily', family)
                identification_xml.set('platform', 'All Platforms')
                identification_xml.set('reference', '')
                identification_xml.set('manufacturer', '')

                if author == '' and element is not None:
                    author = element.get('author', '')

                if author != '':
                    identification_xml.set('contact', author)

                description_xml.set('language', 'Java')
                description_xml.set('description', class_description)

        # capture attributes
        if classes_xml is not None and line.strip().startswith('@Attribute'):

            # attribute description
            attribute_description = comment_buffer
            comment_buffer = ''

            # pass through other decorations
            while source_lines[index].strip().startswith('@'):

                line = source_lines[index].strip()
                assert isinstance(line, str)

                # check if descritpion can be updated
                if line.startswith('@AttributeProperties'):
                    match_result = re.match(r'description\s*=\s*"(?P<desc>[^"]+)"', line)
                    if match_result is not None:
                        attribute_description = match_result.group('desc')

                index += 1

            # attribute name
            line = source_lines[index].strip()
            match_result = re.match(
                r'.*(?=\s[a-zA-Z]+[[]]*\s+[a-zA-Z0-9]+\s*[=;])'
                r'\s(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[=;]',
                ' ' + line
            )
            if match_result is None:
                continue
            else:

                attr_xml = etree.SubElement(classes_xml, 'attributes')

                # populate fields
                attr_xml.set('name', match_result.group('name'))

                etree.SubElement(
                    attr_xml,
                    'dataType',
                    attrib={
                        etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                            'pogoDsl:' + JAVA_DS_ATTRIBUTE_DATATYPES.get(
                                             match_result.group('type'),
                                             [match_result.group('type'), 'Scalar']
                                         )[0]
                    }
                )

                attr_xml.set(
                    'attType',
                    JAVA_DS_ATTRIBUTE_DATATYPES.get(match_result.group('type'), ['', 'Scalar'])[1]
                )

                attr_xml.set('rwType', 'READ_WRITE')

                attr_xml.set('description', attribute_description)

                etree.SubElement(
                    attr_xml, 'properties',
                    attrib={
                        'description': attribute_description,
                    }
                )

        # capture commands
        if classes_xml is not None and line.strip().startswith('@Command'):

            command_description = comment_buffer
            comment_buffer = ''

            # get description of argin and argout
            argin_description = ''
            argin_type = 'VoidType'
            argout_description = ''

            match_result = re.match(r'inTypeDesc\s*=\s*"(?P<desc>[^"]+)"', line)
            if match_result is not None:
                argin_description = match_result.group('desc')

            match_result = re.match(r'outTypeDesc\s*=\s*"(?P<desc>[^"]+)"', line)
            if match_result is not None:
                argout_description = match_result.group('desc')

            # walk through other decorations
            while source_lines[index].strip().startswith('@'):
                index += 1

            # command name and type
            line = ' ' + source_lines[index].strip()
            match_result = re.match(
                r'.*(?=\s[a-zA-Z]+[[]]*\s+[a-zA-Z0-9]+\s*[(])'
                r'\s(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[(]',
                ' ' + line
            )
            if match_result is None:
                continue
            else:
                command_name = match_result.group('name')
                argout_type = JAVA_DS_COMMAND_DATATYPES.get(match_result.group('type'), match_result.group('type'))

            # argin type
            match_result = re.match(r'(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[)]', line)
            if match_result is not None:
                argin_type = JAVA_DS_COMMAND_DATATYPES.get(match_result.group('type'), match_result.group('type'))

            # create xml entries
            cmd_xml = etree.SubElement(classes_xml, 'commands')

            # populate fields
            cmd_xml.set('name', command_name)
            cmd_xml.set('descritpion', command_description)

            # argin
            argin_xml = etree.SubElement(cmd_xml, 'argin')
            argin_xml.set('description', argin_description)

            argin_type_xml = etree.SubElement(argin_xml, 'type')
            argin_type_xml.set(
                etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'),
                'pogoDsl:' + argin_type
            )

            # argout
            argout_xml = etree.SubElement(cmd_xml, 'argout')
            argout_xml.set('description', argout_description)

            argout_type_xml = etree.SubElement(argout_xml, 'type')
            argout_type_xml.set(
                etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'),
                'pogoDsl:' + argout_type
            )

        # capture pipes
        if classes_xml is not None and line.strip().startswith('@Pipe'):

            pipe_description = comment_buffer
            comment_buffer = ''

            # walk through other decorations
            while source_lines[index].strip().startswith('@'):
                index += 1

            # pipe name and type
            line = ' ' + source_lines[index].strip()
            match_result = re.match(
                r'.*(?=\s[a-zA-Z]+[[]]*\s+[a-zA-Z0-9]+\s*[=;])'
                r'\s(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[=;]',
                ' ' + line
            )
            if match_result is None:
                continue
            else:
                pipe_name = match_result.group('name')                

            # create xml entries
            pipe_xml = etree.SubElement(classes_xml, 'pipes')

            # populate fields
            pipe_xml.set('name', pipe_name)
            pipe_xml.set('descritpion', pipe_description)            
        
        # capture device properties
        if classes_xml is not None and line.strip().startswith('@DeviceProperty'):

            property_description = comment_buffer
            comment_buffer = ''

            # walk through other decorations
            while source_lines[index].strip().startswith('@'):
                index += 1

            # property name and type
            line = ' ' + source_lines[index].strip()
            match_result = re.match(
                r'.*(?=\s[a-zA-Z]+[[]]*\s+[a-zA-Z0-9]+\s*[=;])'
                r'\s(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[=;]',
                ' ' + line
            )
            if match_result is None:
                continue
            else:
                property_name = match_result.group('name')
                property_type = JAVA_DS_ATTRIBUTE_DATATYPES.get(
                    match_result.group('type'),
                    [match_result.group('type'), '']
                )[0]

            # property xml element
            property_xml = etree.SubElement(classes_xml, 'deviceProperties')

            # fill attributes
            property_xml.set('name', property_name)
            property_xml.set('description', property_description)

            property_type_xml = etree.SubElement(property_xml, 'type')
            property_type_xml.set(etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'),
                                  'pogoDsl:' + property_type)

        # capture class properties
        if classes_xml is not None and line.strip().startswith('@ClassProperty'):

            property_description = comment_buffer
            comment_buffer = ''

            # walk through other decorations
            while source_lines[index].strip().startswith('@'):
                index += 1

            # property name and type
            line = ' ' + source_lines[index].strip()
            match_result = re.match(
                r'.*(?=\s[a-zA-Z]+[[]]*\s+[a-zA-Z0-9]+\s*[=;])'
                r'\s(?P<type>[a-zA-Z]+[[]]*)\s+(?P<name>[a-zA-Z0-9]+)\s*[=;]',
                ' ' + line
            )
            if match_result is None:
                continue
            else:
                property_name = match_result.group('name')
                property_type = JAVA_DS_ATTRIBUTE_DATATYPES.get(
                    match_result.group('type'),
                    [match_result.group('type'), '']
                )[0]

            # property xml element
            property_xml = etree.SubElement(classes_xml, 'deviceProperties')

            # fill attributes
            property_xml.set('name', property_name)
            property_xml.set('description', property_description)

            property_type_xml = etree.SubElement(property_xml, 'type')
            property_type_xml.set(etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'),
                                  'pogoDsl:' + property_type)

        index += 1

    # return generated xml
    return '<?xml version="1.0" encoding="ASCII"?>' + etree.tostring(xmi_xml)


if __name__ == "__main__":
    # main function perform tests
    java_file = 'test-assets/ControlSystemMonitor.java'
    print get_xmi_from_java('ControlSystemMonitor', 'SoftwareSystems', 'file:' + java_file)
