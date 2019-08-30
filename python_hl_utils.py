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

# regular expressions to detect various components
REGEX_DEVICE_CLASS = re.compile(r"class\s+(?P<class_name>\w+)\s*[(]\s*((tango.)|(PyTango.))*Device\s*[)]")

REGEX_ATTR_START = re.compile(r"\s*(?P<attr_name>\w+)\s*=\s*attribute\s*[(]")

REGEX_CMD_START = re.compile(r"\s*@command\s*[(]?")

REGEX_METHOD_START = re.compile(r"\s*def\s*(?P<name>\w+)")

REGEX_PIPE_START = re.compile(r"\s*(?P<pipe_name>\w+)\s*=\s*pipe\s*[(]?")

REGEX_CLASS_PROPERTY_START = re.compile(r"\s*(?P<property_name>\w+)\s*=\s*class_property\s*[(]")

REGEX_DEVICE_PROPERTY_START = re.compile(r"\s*(?P<property_name>\w+)\s*=\s*device_property\s*[(]")

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
    no_brackets_open = 0  # this will count 'internal' brackets (one which belongs to attributes properties)

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
        access_match = re.search(r"""access\s*=\s*(PyTango.)?(tango.)?(AttrWriteType.)?(?P<access>\w+)""", line)
        if access_match is not None:
            attribute_xml.set('rwType', access_match.group('access'))
            
        # check for display level        
        visibility_match = re.search(r"""display_level\s*=\s*(PyTango.)?(tango.)?(DispLevel.)?(?P<display_level>\w+)""",
                                     line)
        if visibility_match is not None:
            attribute_xml.set(
                'displayLevel',
                visibility_match.group('display_level')
            )
            
        # check for dimensions
        max_x_match = re.search(r"""max_dim_x\s*=\s*(?P<max_dim_x>\d+)""", line)        
        if max_x_match is not None:
            attribute_xml.set('maxX', max_x_match.group('max_dim_x'))

        max_y_match = re.search(r"""max_dim_y\s*=\s*(?P<max_dim_y>\d+)""", line)
        if max_y_match is not None:
            attribute_xml.set('maxY', max_y_match.group('max_dim_y'))
            
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
            if line.strip() == '@command':
                # if there is no command attrib available there is no point to parse them
                etree.SubElement(
                    argin_xml,
                    'type',
                    attrib={
                        etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                            'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                                'DevVoid'
                            )
                    }
                )

                etree.SubElement(
                    argout_xml,
                    'type',
                    attrib={
                        etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                            'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                                'DevVoid'
                            )
                    }
                )
                break

            line = line.replace("@command(", "")

        # look for input argument data type
        dtype_in_spectrum_match = re.search(r"""\s*dtype_in\s*=\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]""", line)

        dtype_in_scalar_match = re.search(r"""\s*dtype_in\s*=\s*['"]?(?P<dtype>\w+)['"]?""", line)

        if dtype_in_spectrum_match is not None:
            # vector/spectrum argument has 'DevVar' in the name
            etree.SubElement(
                argin_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(
                                PYTHON_HL_DATATYPES.get(dtype_in_spectrum_match.group('dtype'), 'DevString')
                            ).replace('Dev', 'DevVar'),
                            'DevVarString'
                        )
                }
            )
        elif dtype_in_scalar_match is not None:
            etree.SubElement(
                argin_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_in_scalar_match.group('dtype'), 'DevString')),
                            'DevVarString'
                        )
                }
            )
        else:
            etree.SubElement(
                argin_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            'DevVoid'
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
                argout_xml,
                'type',
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
                argout_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            str(PYTHON_HL_DATATYPES.get(dtype_out_scalar_match.group('dtype'), 'DevString')),
                            'DevVarString'
                        )
                }
            )
        else:
            etree.SubElement(
                argout_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_COMMAND_DATATYPES_REVERS.get(
                            'DevVoid'
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
                cmd_values['display_level'].replace('PyTango.', '').replace('DispLevel.', '').replace('tango.', '')
            )

        # check for command definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0:
            break

        index += 1

    return command_xml, index


def get_pipe_xml(source_lines, start_index, name, class_xml):
    """
    Generate pipe related xml element
    :param source_lines: lines to be parsed
    :param start_index: index of the line where parsing should start
    :param name: pipe name
    :param class_xml: parent xml node of the command
    :return: (pipe_xml, end_index) where pipe_xml is an xml node and end_index is line number where
             pipe definition ends
    """

    # prepare xml element
    pipe_xml = etree.SubElement(class_xml, 'commands')
    pipe_xml.set('name', name)

    # find content of the attrib definition (part between brackets)
    no_brackets_open = 0  # this will count 'internal' brackets (one which belongs to attributes properties)

    # loop over lines belonging to attribute definition
    index = start_index

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # for the first line remove '@pipe(' part
        if index == start_index:
            if line.strip() == '@pipe':
                # if there is no pipe attributes available there is no need to parse it
                break

            line = REGEX_PIPE_START.sub('', line)
            line = line.replace("@pipe(", "")

        # look keys' values
        pipe_values = key_value_search(
            ['name', 'doc', 'description', 'display_level', 'access', 'label'],
            line
        )

        # name
        if len(pipe_values.get('name', '')) > 0:
            pipe_xml.set('name', pipe_values['name'])

        # description
        if len(pipe_values.get('description', pipe_values.get('doc', ''))) > 0:
            pipe_xml.set('description', pipe_values.get('description', pipe_values.get('doc', '')))

        # label
        if len(pipe_values.get('label', '')) > 0:
            pipe_xml.set('label', pipe_values['label'])

        # display level
        if len(pipe_values.get('display_level', '')) > 0:
            pipe_xml.set(
                'displayLevel',
                pipe_values['display_level'].replace('PyTango.', '').replace('tango.', ' ').replace('DispLevel.', '')
            )

        # access
        if len(pipe_values.get('access', '')) > 0:
            pipe_xml.set(
                'rwType',
                pipe_values['access'].replace('PyTango.', '').replace('tango.', '').replace('AttrWriteType.', '')
            )

        # check for pipe definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0 or REGEX_METHOD_START:
            break

        index += 1

    return pipe_xml, index


def get_property_xml(source_lines, start_index, name, class_xml, subelement_type='deviceProperties'):
    """
    Generate property related xml element
    
    :param source_lines: lines to be parsed
    :param start_index: index of the line where parsing should start
    :param name: attribute name
    :param class_xml: parent xml node of the attribute
    :param subelement_type: type of element tyle (classProperties or deviceProperties)
    :return: (propertye_xml, end_index) where property_xml is an xml node and end_index is line number where
             property definition ends
    """

    # prepare xml element
    property_xml = etree.SubElement(class_xml, subelement_type)
    property_xml.set('name', name)

    # find content of the attrib definition (part between brackets)
    no_brackets_open = 0  # this will count 'internal' brackets (one which belongs to attributes properties)

    # loop over lines belonging to attribute definition
    index = start_index

    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # strip the first line from  '.. = class/device_property('
        if index == start_index:
            line = REGEX_CLASS_PROPERTY_START.sub('', line)
            line = REGEX_DEVICE_PROPERTY_START.sub('', line)

        # check for data type
        dtype_spectrum_match = re.search(r"""\s*dtype\s*=\s*[([]\s*['"]?(?P<dtype>\w+)['"]?\s*,?\s*[)\]]""", line)

        dtype_scalar_match = re.search(r"""\s*dtype\s*=\s*['"]?(?P<dtype>\w+)['"]?""", line)

        if dtype_spectrum_match is not None:
            etree.SubElement(
                property_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_ATTRIBUTE_DATATYPES_REVERS.get(
                            PYTHON_HL_DATATYPES.get(dtype_spectrum_match.group('dtype'), 'DevString')
                        )
                }
            )

            property_xml.set('attType', 'Spectrum')

        if dtype_scalar_match is not None:
            etree.SubElement(
                property_xml,
                'type',
                attrib={
                    etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'):
                        'pogoDsl:' + DS_ATTRIBUTE_DATATYPES_REVERS.get(
                            PYTHON_HL_DATATYPES.get(dtype_scalar_match.group('dtype'), 'DevEnum'),
                            'EnumType'
                        )
                }
            )

            property_xml.set('attType', 'Scalar')

        # check for access type
        access_match = re.search(r"""access\s*=\s*(PyTango.)?(tango.)?(AttrWriteType.)?(?P<access>\w+)""", line)
        if access_match is not None:
            property_xml.set('rwType', access_match.group('access'))

        # check for display level        
        visibility_match = re.search(r"""display_level\s*=\s*(PyTango.)?(tango.)?(DispLevel.)?(?P<display_level>\w+)""",
                                     line)
        if visibility_match is not None:
            property_xml.set(
                'displayLevel',
                visibility_match.group('display_level')
            )

        # check for dimensions
        max_x_match = re.search(r"""max_dim_x\s*=\s*(?P<max_dim_x>\d+)""", line)
        if max_x_match is not None:
            property_xml.set('maxX', max_x_match.group('max_dim_x'))

        max_y_match = re.search(r"""max_dim_y\s*=\s*(?P<max_dim_y>\d+)""", line)
        if max_y_match is not None:
            property_xml.set('maxY', max_y_match.group('max_dim_y'))

        # check for description
        description_match = re.search(r"""((doc)|(description))\s*=\s*["](?P<description>.+?)["]""", line)

        # try different possible patterns
        if description_match is None:
            description_match = re.search(r"""((doc)|(description))\s*=\s*['](?P<description>.+?)[']""", line)

        if description_match is None:
            description_match = re.search(r"""((doc)|(description))\s*=\s*["]["]["](?P<description>.+?)["]["]["]""",
                                          line)

        if description_match is not None:
            property_xml.set('description', description_match.group('description'))
        else:
            property_xml.set('description', '')

        # check for attribute definition end
        no_brackets_open += line.count('(') - line.count(')')
        # definition ends when there is not matched close bracket
        if no_brackets_open < 0:
            break

        index += 1

    return property_xml, index


def get_class_xml(source_lines, start_index, name, xmi_xml, element=None, meta_data={}):
    """
    Generates class relate xml element from selected lines

    :param source_lines:
    :param start_index:
    :param name:
    :param xmi_xml:
    :param element:
    :param meta_data:
    :return: (class_xml, end_index)
    """

    classes_xml = etree.SubElement(xmi_xml, 'classes')
    classes_xml.set('name', name)
    description_xml = etree.SubElement(classes_xml, 'description')
    identification_xml = etree.SubElement(description_xml, 'identification')

    # find description part (comment)
    description_started = False
    class_description = ''
    for line in source_lines:
        if re.match(r'#\s+' + name + r'\s+Class Description', line) is not None:
            description_started = True

        if description_started:
            if line.startswith('#===========================') or line.startswith(' ') or line == '':
                # end of description
                break

            class_description += line[2:].strip() + '\n\n'

    # remove html
    class_description = re.sub('</p>', '\n\n', class_description)
    class_description = re.sub('<br/>', '\n\n', class_description)
    class_description = re.sub('<br />', '\n\n', class_description)
    class_description = re.sub('<b>\s*', '*', class_description)
    class_description = re.sub('\s*</b>', '*', class_description)
    class_description = re.sub(r"<a\s+[^>]*href=['\"](?P<hhref>[^'\"]+)['\"][^>]*(?=>)>\s*</a>", " \g<hhref> ",
                               class_description)
    class_description = re.sub('<[^<>a/]+?>', '', class_description)
    class_description = re.sub('</[^a<>]+?>', '', class_description)
    class_description = re.sub(r"<a\s+[^>]*href=['\"](?P<hhref>[^'\"]+)['\"][^>]*(?=>)>(?P<text>[\s[^<]]+(?=</a>))</a>",
                               ' `\g<text> <\g<hhref>>`_ ', class_description)

    # find author
    author = ''

    for line in source_lines:
        if line.startswith("# $Author: "):
            author = line[10:].replace('$', '').strip()
            break

    if author == '' and element is not None:
        author = element.get('author', '')

    author = meta_data.get('author', author)

    # find copyright
    copyleft = ''
    copyleft_started = False

    for line in source_lines:

        if not copyleft_started:
            # find the first line of the copyleft
            match_result = re.match(r'#\s+copyleft\s*:\s*(?P<copyleft>.+)', line)
            if match_result is not None:
                copyleft_started = True
                copyleft = match_result.group('copyleft').strip()

        else:
            # check if we are still in the copyleft section
            match_result = re.match(r'#\s+(?P<copyleft>.+)', line)

            if match_result is None:
                # if not, stop processing
                break
            # build the string
            copyleft += '\n' + match_result.group('copyleft').strip()

    identification_xml.set('classFamily', meta_data.get('family'))

    identification_xml.set('platform', meta_data.get('platform', 'All Platforms'))

    identification_xml.set('reference', meta_data.get('reference', ''))

    identification_xml.set('manufacturer', meta_data.get('manufacturer', ''))

    identification_xml.set('bus', meta_data.get('bus', ''))

    if author != '':
        identification_xml.set('contact', author)

    description_xml.set('language', 'PythonHL')

    description_xml.set('description', meta_data.get('class_description', class_description))

    description_xml.set('license', meta_data.get('license', ''))

    # iteration over lines
    index = start_index  # use indexing instead of iterator
    while index < len(source_lines):

        line = source_lines[index]
        assert isinstance(line, str)

        # look for attribute declarations
        attr_mo = REGEX_ATTR_START.search(line)
        if attr_mo is not None:
            (attr_xml, end_index) = get_attribute_xml(source_lines, index, attr_mo.group('attr_name'), classes_xml)
            index = end_index

        elif line.strip().startswith('@attribute('):
            # search for name
            tmp_index = index + 1
            attr_name_match = None
            while tmp_index < len(source_lines) and attr_name_match is None:
                attr_name_match = REGEX_METHOD_START.search(source_lines[tmp_index])
                if attr_name_match is not None:
                    (attr_xml, end_index) = get_attribute_xml(source_lines, index, attr_name_match.group('name'),
                                                              classes_xml)
                    index = end_index

        # look for command declarations
        if line.strip().startswith('@command'):
            tmp_index = index + 1
            cmd_name_match = None
            while tmp_index < len(source_lines) and cmd_name_match is None:
                cmd_name_match = REGEX_METHOD_START.search(source_lines[tmp_index])
                if cmd_name_match is not None:
                    # TODO: implement parsing methods' comments as descriptions for commands
                    # if source_lines[tmp_index+1].strip().startswith('"""'):
                    #     cmd_description = source_lines[tmp_index+1].strip()[]
                    #     while

                    (cmd_xml, end_index) = get_command_xml(source_lines, index, cmd_name_match.group('name'),
                                                              classes_xml)
                    index = end_index

                tmp_index += 1

        # look for pipes declarations
        pipe_mo = REGEX_PIPE_START.search(line)
        if pipe_mo is not None:
            (pipe_xml, end_index) = get_pipe_xml(source_lines, index, attr_mo.gropup('pipe_name'), classes_xml)
            index = end_index

        elif line.strip().startswith('@pipe'):
            tmp_index = index + 1
            pipe_name_match = None
            while tmp_index < len(source_lines) and pipe_name_match is None:
                pipe_name_match = REGEX_METHOD_START.search(source_lines[tmp_index])
                if pipe_name_match is not None:
                    (pipe, end_index) = get_pipe_xml(source_lines, index, attr_name_match.group('name'),
                                                              classes_xml)
                    index = end_index

        # TODO: class and device properties
        device_property_mo = REGEX_DEVICE_PROPERTY_START.search(line)
        if device_property_mo is not None:
            (property_xml, end_index) = get_property_xml(
                source_lines,
                index,
                device_property_mo.group('property_name'),
                classes_xml,
                subelement_type='deviceProperties'
            )
            index = end_index

        class_property_mo = REGEX_CLASS_PROPERTY_START.search(line)
        if class_property_mo is not None:
            (property_xml, end_index) = get_property_xml(
                source_lines,
                index,
                class_property_mo.group('property_name'),
                classes_xml,
                subelement_type='classProperties'
            )
            index = end_index

        # increment index
        index += 1

    return classes_xml, index


def get_xmi_from_python_hl(name, family, python_file_url, element=None, meta_data={}):
    """
    Generates xmi file content from a parsed Python HL device server

    :param name: name of the device server
    :param family: family name
    :param python_file_url: URL of the python file
    :param element:
    :param meta_data: additional info to be included in class info
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
    if size < 10 or size > 2000000:
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

        meta_data['family'] = meta_data.get('family', family)

        # check if we start class
        if line.strip().startswith('class'):
            mo = REGEX_DEVICE_CLASS.match(line.strip())
            if mo is not None:
                (classes_xml, end_index) = get_class_xml(source_lines, index, mo.group('class_name'), xmi_xml,
                                                         element=element, meta_data=meta_data)
                index = end_index

        index += 1
                
    return '<?xml version="1.0" encoding="ASCII"?>' + etree.tostring(xmi_xml)


if __name__ == "__main__":
    # main function perform tests

    py_file1 = 'test-assets/RaspberryPiIO.py'

    xmi = get_xmi_from_python_hl(
        'RaspberryPiIO', 'Communication', 'file:' + py_file1,
        meta_data={'author': 'pg@pg.com'}
    )

    print xmi

    with open('RaspberryPiIO.xmi', 'w') as f:
        f.write(xmi)

    py_file2 = 'test-assets/Eiger.py'

    xmi = get_xmi_from_python_hl(
        'Eiger', 'Communication', 'file:' + py_file2,
        meta_data={'author': 'kits@maxiv.edu.se'}
    )

    print xmi

    with open('Eiger.xmi', 'w') as f:
        f.write(xmi)