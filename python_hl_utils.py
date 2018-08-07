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
from s2i_utils import key_value_search

# regular experssions to detect various components
REGEX_DEVICE_CLASS = re.compile(r"class\s+(?P<class_name>\w+)\s*[(]\s*((tango.)|(PyTango.))*Device\s*[)]")

REGEX_ATTR_START = re.compile(r"\s*(?P<attr_name>\w+)\s*=\s*attribute\s*[(]")

REGEX_CMD_START = re.compile(r"\s*@command\s*[(]")

REGEX_METHOD_START = re.compile(r"\s*def\s*(?P<name>\w+)")

# matches of python hl datatypes to tango types
PYTHON_HL_DATATYPES = {
"None": "DevVoid",
"'None'": "DevVoid",
"DevVoid": "DevVoid",
"'DevVoid'": "DevVoid",
"DevState": "DevState",
"'DevState'": "DevState",
"bool": "DevBoolean",
"'bool'": "DevBoolean",
"'boolean'": "DevBoolean",
"DevBoolean": "DevBoolean",
"'DevBoolean'": "DevBoolean",
"numpy.bool_": "DevBoolean",
"'char'": "DevUChar",
"'chr'": "DevUChar",
"'byte'": "DevUChar",
"chr": "DevUChar",
"DevUChar": "DevUChar",
"'DevUChar'": "DevUChar",
"numpy.uint8": "DevUChar",
"'int16'": "DevShort",
"DevShort": "DevShort",
"'DevShort'": "DevShort",
"numpy.int16": "DevShort",
"'uint16'": "DevUShort",
"DevUShort": "DevUShort",
"'DevUShort'": "DevUShort",
"numpy.uint16": "DevUShort",
"int": "DevLong",
"'int'": "DevLong",
"'int32'": "DevLong",
"DevLong": "DevLong",
"'DevLong'": "DevLong",
"numpy.int32": "DevLong",
"'uint'": "DevULong",
"'uint32'": "DevULong",
"DevULong": "DevULong",
"'DevULong'": "DevULong",
"numpy.uint32": "DevULong",
"'int64'": "DevLong64",
"DevLong64": "DevLong64",
"'DevLong64'": "DevLong64",
"numpy.int64": "DevLong64",
"'uint64'": "DevULong64",
"DevULong64": "DevULong64",
"'DevULong64'": "DevULong64",
"numpy.uint64": "DevULong64",
"DevInt": "DevInt",
"'DevInt'": "DevInt",
"'float32'": "DevFloat",
"DevFloat": "DevFloat",
"'DevFloat'": "DevFloat",
"numpy.float32": "DevFloat",
"float": "DevDouble",
"'double'": "DevDouble",
"'float'": "DevDouble",
"'float64'": "DevDouble",
"DevDouble": "DevDouble",
"'DevDouble'": "DevDouble",
"numpy.float64": "DevDouble",
"str": "DevString",
"'str'": "DevString",
"'string'": "DevString",
"'text'": "DevString",
"DevString": "DevString",
"'DevString'": "DevString",
"bytearray": "DevEncoded",
"'bytearray'": "DevEncoded",
"'bytes'": "DevEncoded",
"DevEncoded": "DevEncoded",
"'DevEncoded'": "DevEncoded",
"DevVarBooleanArray": "DevVarBooleanArray",
"'DevVarBooleanArray'": "DevVarBooleanArray",
"DevVarCharArray": "DevVarCharArray",
"'DevVarCharArray'": "DevVarCharArray",
"DevVarShortArray": "DevVarShortArray",
"'DevVarShortArray'": "DevVarShortArray",
"DevVarLongArray": "DevVarLongArray",
"'DevVarLongArray'": "DevVarLongArray",
"DevVarLong64Array": "DevVarLong64Array",
"'DevVarLong64Array'": "DevVarLong64Array",
"DevVarULong64Array": "DevVarULong64Array",
"'DevVarULong64Array'": "DevVarULong64Array",
"DevVarFloatArray": "DevVarFloatArray",
"'DevVarFloatArray'": "DevVarFloatArray",
"DevVarDoubleArray": "DevVarDoubleArray",
"'DevVarDoubleArray'": "DevVarDoubleArray",
"DevVarUShortArray": "DevVarUShortArray",
"'DevVarUShortArray'": "DevVarUShortArray",
"DevVarULongArray": "DevVarULongArray",
"'DevVarULongArray'": "DevVarULongArray",
"DevVarStringArray": "DevVarStringArray",
"'DevVarStringArray'": "DevVarStringArray",
"DevVarLongStringArray": "DevVarLongStringArray",
"'DevVarLongStringArray'": "DevVarLongStringArray",
"DevVarDoubleStringArray": "DevVarDoubleStringArray",
"'DevVarDoubleStringArray'": "DevVarDoubleStringArray",
"DevPipeBlob": "DevPipeBlob",
"'DevPipeBlob'": "DevPipeBlob",
}


def get_attribute_xml(source_lines, start_index, name, class_xml):
    """
    Generate attribute related xml element
    :param source_lines: lines to be parsed
    :param start_index: index of the line where parsing should start
    :param name: attribute name
    :param class_xml: parent xml node of the attribute
    :return: (attribute_xml, end_index) where attribute_xml is an xml node and end_index is line number where
             attribute definition ends
    """
    # prepare xml element
    attribute_xml = etree.SubElement(class_xml, 'attributes')
    attribute_xml.set('name', name)
    
    attribute_properties_xml = etree.SubElement(attribute_xml, 'properties')

    # find content of the attrib definition (part between brackets)
    no_brackets_open = 0 # this will count 'internal' brackets (one which belongs to attributes properties)

    # loop over lines belonging to attribute definition
    index = start_index

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # strip the first line from  '.. = attribute('
        if index == start_index:
            line = REGEX_ATTR_START.sub('', line)
            line = line.replace('@attribute(', '')

        # check for data type
        dtype_image_match = re.search(
            r"""\s*dtype\s*=\s*[[(]\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]\s*,?\s*[)\]]""",
            line
        )

        dtype_spectrum_match = re.search(r"""\s*dtype\s*=\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]""", line)

        dtype_scalar_match = re.search(r"""\s*dtype\s*=\s*['"]?(?P<dtype>\w+)['"]?""", line)

        if dtype_image_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_ATTRIBUTE_DATATYPES_REVERS.get(
                            PYTHON_HL_DATATYPES.get(dtype_image_match.group('dtype'), 'DevEnum'),
                            'EnumType'
                        )
                }
            )

            attribute_xml.set('attType', 'Image')

        if dtype_spectrum_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_ATTRIBUTE_DATATYPES_REVERS.get(
                            PYTHON_HL_DATATYPES.get(dtype_spectrum_match.group('dtype'), 'DevEnum'),
                            'EnumType'
                        )
                }
            )

            attribute_xml.set('attType', 'Spectrum')

        if dtype_scalar_match is not None:
            etree.SubElement(
                attribute_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_ATTRIBUTE_DATATYPES_REVERS.get(
                            PYTHON_HL_DATATYPES.get(dtype_scalar_match.group('dtype'), 'DevEnum'),
                            'EnumType'
                        )
                }
            )

            attribute_xml.set('attType', 'Scalar')

        # check for access type
        access_match = re.search(r"""access\s*=\s*(AttrWriteType.)?(?P<access>\w+)""", line)        
        if access_match is not None:
            attribute_xml.set('rwType', access_match.group('access'))
            
        # check for display level        
        visibility_match = re.search(r"""display_level\s*=\s*(DispLevel.)?(?P<display_level>\w+)""", line)        
        if visibility_match is not None:
            attribute_xml.set('displayLevel', visibility_match.group('display_level'))
            
        # check for dimensions
        max_x_match = re.search(r"""max_dim_x\s*=\s*(?P<max_dim_x>\d+)""", line)        
        if max_x_match is not None:
            attribute_xml.set('maxX'. max_x_match.group('max_dim_x'))

        max_y_match = re.search(r"""max_dim_y\s*=\s*(?P<max_dim_y>\d+)""", line)
        if max_y_match is not None:
            attribute_xml.set('maxY'.max_y_match.group('max_dim_y'))
            
        # check for descritpion
        description_match = re.search(r"""((doc)|(description))\s*=\s*["](?P<description>.+?)["]""", line)
        
        # try different possible patterns
        if description_match is None:
            description_match = re.search(r"""((doc)|(description))\s*=\s*['](?P<description>.+?)[']""", line)
        
        if description_match is None:
            description_match = re.search(r"""((doc)|(description))\s*=\s*["]["]["](?P<description>.+?)["]["]["]""",
                                          line)
            
        if description_match is not None:
            attribute_xml.set('description', description_match.group('description'))
            attribute_properties_xml.set('description', description_match.group('description'))
            
        # check for label
        label_match = re.search(r"""label\s*=\s*['"](?P<label>\w+)['"]""", line)
        if label_match is not None:
            attribute_properties_xml.set('label', label_match.group('label'))
            
        # TODO: pars for other attribute properties    
            
        # check for attribute definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0:
            break

        index += 1

    return attribute_xml, index


def get_command_xml(source_lines, start_index, name, class_xml):
    """
    Generate command related xml element
    :param source_lines: lines to be parsed
    :param start_index: index of the line where parsing should start
    :param name: command name
    :param class_xml: parent xml node of the command
    :return: (command_xml, end_index) where command_xml is an xml node and end_index is line number where
             command definition ends
    """

    # prepare xml element
    command_xml = etree.SubElement(class_xml, 'commands')
    command_xml.set('name', name)

    argin_xml = etree.SubElement(command_xml, 'argin')
    argout_xml = etree.SubElement(command_xml, 'argout')

    # find content of the attrib definition (part between brackets)
    no_brackets_open = 0  # this will count 'internal' brackets (one which belongs to attributes properties)

    # loop over lines belonging to attribute definition
    index = start_index

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # for the first line remove '@command' part
        if index == start_index:
            line = line.replace("@command(", "").replace("@command", "")

        # look for input argument data type
        dtype_in_spectrum_match = re.search(r"""\s*dtype_in\s*=\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]""", line)

        dtype_in_scalar_match = re.search(r"""\s*dtype_in\s*=\s*['"]?(?P<dtype>\w+)['"]?""", line)

        if dtype_in_spectrum_match is not None:
            # vector/spectrum argument has 'DevVar' in the name
            etree.SubElement(
                argin_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_in_spectrum_match.group('dtype'), 'DevString')).replace('Dev', 'DevVar'),
                            'DevVarString'
                        )
                }
            )
        elif dtype_in_scalar_match is not None:
            etree.SubElement(
                argin_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_in_spectrum_match.group('dtype'), 'DevString')),
                            'DevVarString'
                        )
                }
            )

        # look for output argument data type
        dtype_out_spectrum_match = re.search(r"""\s*dtype_out\s*=\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]""",
                                            line)

        dtype_out_scalar_match = re.search(r"""\s*dtype_out\s*=\s*['"]?(?P<dtype>\w+)['"]?""", line)

        if dtype_out_spectrum_match is not None:
            # vector/spectrum argument has 'DevVar' in the name
            etree.SubElement(
                argin_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_out_spectrum_match.group('dtype'),
                                                        'DevString')).replace('Dev', 'DevVar'),
                            'DevVarString'
                        )
                }
            )
        elif dtype_out_scalar_match is not None:
            etree.SubElement(
                argin_xml,
                'dataType',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_out_spectrum_match.group('dtype'), 'DevString')),
                            'DevVarString'
                        )
                }
            )
        
        # look for other keys
        cmd_values = key_value_search(
            ['doc_in', 'doc_out', 'display_level', 'polling_period', 'green_mode'],
            line
        )

        # input argument description
        if len(cmd_values.get('doc_in', '')) > 0:
            argin_xml.set('description', cmd_values['doc_in'])

        # output description
        if len(cmd_values.get('doc_out', '')) > 0:
            argout_xml.set('description', cmd_values['doc_out'])

        # polling period
        if len(cmd_values.get('polling_period', '')) > 0:
            argin_xml.set('polledPeriod', cmd_values['polling_period'])

        # display level
        if len(cmd_values.get('display_level', '')) > 0:
            argin_xml.set(
                'displayLevel',
                cmd_values['display_level'].replace('PyTango.', '').replace('DispLevel.', '').replace('tango', '')
            )

        # check for command definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0:
            break

        index += 1

    return command_xml, index


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
        assert isinstance(line, str)

        # look for attribute declarations
        attr_mo = REGEX_ATTR_START.search(line)
        if attr_mo is not None:
            (attr_xml, end_index) = get_attribute_xml(source_lines, index, attr_mo.gropup('attr_name'), classes_xml)
            index = end_index

        elif line.strip().startswith('@attribute('):
            # search for name
            tmp_index = index + 1
            attr_name_match = None
            while tmp_index < len(source_lines) and attr_name_match is None:
                attr_name_match = REGEX_METHOD_START.search(source_lines[tmp_index])
                if attr_name_match is not None:
                    (attr_xml, end_index) = get_attribute_xml(source_lines, index, attr_name_match.gropup('name'),
                                                              classes_xml)
                    index = end_index

        # look for command declarations
        if line.strip().startswith('@command'):
            tmp_index = index + 1
            cmd_name_match = None
            while tmp_index < len(source_lines) and cmd_name_match is None:
                cmd_name_match = REGEX_METHOD_START.search(source_lines[tmp_index])
                if cmd_name_match is not None:
                    (cmd_xml, end_index) = get_command_xml(source_lines, index, cmd_name_match.gropup('name'),
                                                              classes_xml)
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
                
    return xmi_xml


