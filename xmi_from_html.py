"""
    (c) by Piotr Goryl, 3Controls, 2016/17 for Tango Controls Community

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


from lxml import etree
from lxml.html import parse
import re

DS_COMMAND_DATATYPES = {
    'BooleanType': 'DevBoolean',
    'FloatType': 'DevFloat',
    'DoubleType': 'DevDouble',
    'IntType': 'DevLong',
    'LongType': 'DevLong64',
    'ShortType': 'DevShort',
    'StringType': 'DevString',
    'UIntType': 'DevULong',
    'ULongType': 'DevULong64',
    'UShortType': 'DevUShort',
    'UCharType': 'DevUChar',
    'CharType': 'DevChar',
    'CharArrayType': 'DevVarCharArray',
    'DoubleArrayType': 'DevVarDoubleArray',
    'DoubleStringArrayType': 'DevVarDoubleStringArray',
    'FloatArrayType': 'DevVarFloatArray',
    'LongArrayType': 'DevVarLong64Array',
    'IntArrayType': 'DevVarLongArray',
    'LongStringArrayType': 'DevVarLongStringArray',
    'ShortArrayType': 'DevVarShortArray',
    'StringArrayType': 'DevVarStringArray',
    'ULongArrayType': 'DevVarULong64Array',
    'UIntArrayType': 'DevVarULongArray',
    'UShortArrayType': 'DevVarUShortArray',
    'VoidType': 'DevVoid',
    'ConstStringType': 'ConstDevString',
    'StateType': 'State'
}
DS_COMMAND_DATATYPES_REVERS = {v: k for k, v in DS_COMMAND_DATATYPES.items() }
DS_COMMAND_DATATYPES_REVERS['DevState']='StateType'




DS_ATTRIBUTE_DATATYPES = {
    'BooleanType': 'DevBoolean',
    'FloatType': 'DevFloat',
    'DoubleType': 'DevDouble',
    'IntType': 'DevLong',
    'LongType': 'DevLong64',
    'ShortType': 'DevShort',
    'StringType': 'DevString',
    'UIntType': 'DevULong',
    'ULongType': 'DevULong64',
    'UShortType': 'DevUShort',
    'UCharType': 'DevUChar',
    'CharType': 'DevChar',
    'EncodedType': 'DevEncoded',
    'StateType': 'DevState'
}

DS_ATTRIBUTE_DATATYPES_REVERS = {v: k for k, v in DS_ATTRIBUTE_DATATYPES.items() }

DS_PROPERTIES_DATATYPES = {
    'BooleanType': 'DevBoolean',
    'FloatType': 'DevFloat',
    'DoubleType': 'DevDouble',
    'IntType': 'DevLong',
    'LongType': 'DevLong64',
    'ShortType': 'DevShort',
    'StringType': 'DevString',
    'UIntType': 'DevULong',
    'ULongType': 'DevULong64',
    'UShortType': 'DevUShort',
    'UCharType': 'DevUChar',
    'CharType': 'DevChar',
    'BooleanVectorType': 'Array of DevBoolean',
    'FloatVectorType': 'Array of DevFloat',
    'DoubleVectorType': 'Array of DevDouble',
    'IntVectorType': 'Array of DevLong',
    'LongVectorType': 'Array of DevLong64',
    'ShortVectorType': 'Array of DevShort',
    'StringVectorType': 'Array of DevString',
    'UIntVectorType': 'Array of DevULong',
    'ULongVectorType': 'Array of DevULong64',
    'UShortVectorType': 'Array of DevUShort',
    'UCharVectorType': 'Array of DevUChar',
    'CharVectorType': 'Array of DevChar',
}



def get_xmi_from_html(description_url, attributes_url="", commands_url="", pipes_url="", properties_url=""):
    """ This function parses device server documentation html texts for information about device class and then
    produce .xmi"""


    # base for xmi
    xmi_xml = etree.fromstring(
"""<?xml version="1.0" encoding="ASCII"?>
<pogoDsl:PogoSystem xmi:version="2.0"
xmlns:xmi="http://www.omg.org/XMI"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:pogoDsl="http://www.esrf.fr/tango/pogo/PogoDsl">
</pogoDsl:PogoSystem>"""
    )

    # find base information
    description_parser = parse(description_url)
    # build structure
    classes_xml = etree.SubElement(xmi_xml, 'classes')
    description_xml = etree.SubElement(classes_xml,'description')
    identification_xml = etree.SubElement(description_xml,'identification')

    # search for name, keywords and so
    for el in description_parser.iter('td'):
        # name
        if el.text is not None and el.text.strip().lower() == 'class':
            classes_xml.set('name', str(el.getnext().text).split(':')[1].strip())


        # family
        if el.text is not None and el.text.strip().lower() == 'family':
            identification_xml.set('classFamily', str(el.getnext().text).split(':')[1].strip())

        # key words
        if el.text is not None and el.text.strip().lower() == 'key word(s)':
            for kw in str(el.getnext().text).split(':'):
                if str(kw).strip()!='':
                    kw_el = etree.SubElement(identification_xml,'keyWords')
                    kw_el.text = str(kw).strip()

        # author
        if el.text is not None and el.text.strip().lower() == 'author':
            identification_xml.set('contact', str(el.getnext().text).split(':')[1].strip())

        # language
        if el.text is not None and el.text.strip().lower() == 'language':
            description_xml.set('language', str(el.getnext().text).split(':')[1].strip())

        # platform
        if el.text is not None and el.text.strip().lower() == 'platform':
            identification_xml.set('platform', str(el.getnext().text).split(':')[1].strip())

        # bus
        if el.text is not None and el.text.strip().lower() == 'bus':
            identification_xml.set('bus', str(el.getnext().text).split(':')[1].strip())

        # manufacturer
        if el.text is not None and el.text.strip().lower() == 'manufacturer':
            identification_xml.set('manufacturer', str(el.getnext().text).split(':')[1].strip())

        # Manufacturer ref
        if el.text is not None and el.text.strip().lower() == 'manufacturer ref.':
            identification_xml.set('reference', str(el.getnext().text).split(':')[1].strip())

    description_is_comming = False
    description_xml.set('description','')
    # serch for descritpion text itself
    for el in description_parser.iter():
        if el.text is not None and el.text.strip() == '%s Class Description :' % classes_xml.get('name'):
            description_is_comming = True
        if description_is_comming and el.tag=='ul' and el.text_content() is not None:
            description_xml.set('description', el.text_content().strip())

    # attributes
    headers = []

    if attributes_url!='':
        attributes_parser = parse(attributes_url)
        for tr in attributes_parser.iter('tr'):
            if tr.getprevious() is None:
                headers = []
            elif tr.getprevious() is not None and len(headers)==0:
                for td in tr.iter('td'):
                    head = td.text_content().strip().lower()
                    headers.append(head)
            elif tr.getprevious() is not None and len(headers)>0:
                i = 0
                attribute_xml = etree.SubElement(classes_xml,'attributes')
                for td in tr.iter('td'):

                    if headers[i] == 'name':
                        attribute_xml.set('name', td.text_content().strip())

                    if headers[i] == 'description':
                        attribute_xml.set('description', td.text_content().strip())

                    if headers[i] == 'attr. type':
                        attribute_xml.set('attType', td.text_content().strip())

                    if headers[i] == 'data type':
                        type_parsed = re.match('.*(DEV)_(U)*(.*)', td.text_content().strip())
                        if type_parsed is not None:
                            tango_type = ''
                            for g in [1,2,3]:
                                if type_parsed.group(g) is not None:
                                    tango_type += type_parsed.group(g).capitalize()
                            # print tango_type
                            etree.SubElement(attribute_xml, 'dataType',
                                             attrib={etree.QName('http://www.w3.org/2001/XMLSchema-instance','type'): 'pogoDsl:' +
                                                            DS_ATTRIBUTE_DATATYPES_REVERS.get(tango_type,'Unknown')})

                    i += 1

    # commands
    headers = []

    if commands_url != '':
        commands_parser = parse(commands_url)
        for tr in commands_parser.iter('tr'):
            if tr.getprevious() is None:
                headers = []
            elif tr.getprevious() is not None and len(headers) == 0:
                for td in tr.iter('td'):
                    head = td.text_content().strip().lower()
                    headers.append(head)

            elif tr.getprevious() is not None and len(headers) > 0:
                i = 0
                command_xml = etree.SubElement(classes_xml, 'commands')
                for td in tr.iter('td'):

                    if headers[i] == 'name':
                        command_xml.set('name', td.text_content().strip())
                        # print 'Command: %s' % command_xml.get('name')

                    if headers[i] == 'description':
                        command_xml.set('description', td.text_content().strip())

                    if headers[i] == 'input type':
                        # print 'input:'
                        type_parsed = re.match('.*(CONST)*_*(DEV)(VAR)*_(U)*((.*)(STRING)(ARRAY)*|(.*)(ARRAY)|(.*(?!ARRAY)))',
                                               td.text_content().strip())

                        if type_parsed is not None:
                            tango_type = ''
                            for g in [1,2,3,4,6,7,8,9,10,11]:
                                if type_parsed.group(g) is not None:
                                    tango_type += type_parsed.group(g).capitalize()

                            # print '%s: %s' % (tango_type, DS_COMMAND_DATATYPES_REVERS.get(tango_type, 'Unknown'))
                            argin_xml = etree.SubElement(command_xml,'argin')
                            etree.SubElement(argin_xml, 'type',
                                             attrib={etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'): 'pogoDsl:' +
                                                                DS_COMMAND_DATATYPES_REVERS.get(tango_type, 'Unknown')})
                    if headers[i] == 'output type':
                        # print 'output:'
                        type_parsed = re.match('.*(CONST)*_*(DEV)(VAR)*_(U)*((.*)(STRING)(ARRAY)*|(.*)(ARRAY)|(.*(?!ARRAY)))',
                                               td.text_content().strip())

                        if type_parsed is not None:
                            tango_type = ''
                            for g in [1,2,3,4,6,7,8,9,10,11]:
                                if type_parsed.group(g) is not None:
                                    tango_type += type_parsed.group(g).capitalize()

                            # print '%s: %s' % (tango_type, DS_COMMAND_DATATYPES_REVERS.get(tango_type, 'Unknown'))
                            argout_xml = etree.SubElement(command_xml,'argout')
                            etree.SubElement(argout_xml, 'type',
                                             attrib={etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'): 'pogoDsl:' +
                                                                DS_COMMAND_DATATYPES_REVERS.get(tango_type, 'Unknown')})

                    i += 1

    # properties
    headers = []

    if properties_url != '':
        properties_parser = parse(properties_url)
        for tr in properties_parser.iter('tr'):

            if tr.getprevious() is None:
                headers = []

            elif tr.getprevious() is not None and len(headers) == 0:
                for td in tr.iter('td'):
                    head = td.text_content().strip().lower()
                    headers.append(head)

            elif tr.getprevious() is not None and len(headers) > 0:
                i = 0
                property_xml = etree.SubElement(classes_xml,'deviceProperties')
                for td in tr.iter('td'):

                    if headers[i] == 'name':
                        property_xml.set('name', td.text_content().strip())

                    if headers[i] == 'description':
                        property_xml.set('description', td.text_content().strip())

                    if headers[i] == 'type':
                        property_type_xml = etree.SubElement(property_xml,'type')
                        property_type_xml.set(etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'),
                                         'pogoDsl:'+ td.text_content().strip().capitalize() + 'Type')

                    i += 1


    return '<?xml version="1.0" encoding="ASCII"?>'+etree.tostring(xmi_xml)

def test_xmi_from_html():

    URLs = [
        "http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/Motion/GalilDMCMotor",
        "http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/System/TangoTest",
        "http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/Vacuum/AxtranGaugeController",
    ]

    for url in URLs:
        print "-------------------------------"
        print "Testing for URL: " + url
        print "-------------------------------"
        xmi = get_xmi_from_html(description_url=url+'/ClassDescription.html',
                                attributes_url=url+'/Attributes.html',
                                commands_url=url + '/Commands.html',
                                properties_url= url + '/Properties.html')

        print "\nXMI content:"
        print xmi;
        f = open('/home/piotr/tmp/xmi_test.xmi','w')
        f.write(xmi)
        f.close()
        print "--------------------------------"
        print

# test_xmi_from_html()








