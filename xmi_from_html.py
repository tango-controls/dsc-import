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

    for el in description_parser.iter('td'):
        # name
        if el.text is not None and el.text.strip().lower() == 'class':
            classes_xml.set('name', str(el.getnext().text).split(':')[1].strip())

        # family
        if el.text is not None and el.text.strip().lower == 'family':
            identification_xml.set('classFamily', str(el.getnext().text).split(':')[1].strip())

        # key words
        if el.text is not None and el.text.strip().lower == 'key word(s)':
            for kw in str(el.getnext().text).split(':'):
                kw_el = etree.SubElement(identification_xml,'keyWords')
                kw_el.text = str(kw).strip()

        # author
        if el.text is not None and el.text.strip().lower == 'author':
            identification_xml.set('contact', str(el.getnext().text).split(':')[1].strip())

        # language
        if el.text is not None and el.text.strip().lower == 'language':
            description_xml.set('language', str(el.getnext().text).split(':')[1].strip())

        # platform
        if el.text is not None and el.text.strip().lower == 'platform':
            identification_xml.set('platform', str(el.getnext().text).split(':')[1].strip())

        # bus
        if el.text is not None and el.text.strip().lower == 'bus':
            identification_xml.set('bus', str(el.getnext().text).split(':')[1].strip())

        # manufacturer
        if el.text is not None and el.text.strip().lower == 'manufacturer':
            identification_xml.set('manufacturer', str(el.getnext().text).split(':')[1].strip())

        # Manufacturer ref
        if el.text is not None and el.text.strip().lower == 'manufacturer ref.':
            identification_xml.set('reference', str(el.getnext().text).split(':')[1].strip())

    return etree.tostring(xmi_xml)

def test_xmi_from_html():

    URLs = [
        "http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/Motion/GalilDMCMotor/",
        "http://www.esrf.eu/computing/cs/tango/tango_doc/ds_doc/tango-ds/System/TangoTest"
    ]

    for url in URLs:
        print "-------------------------------"
        print "Testing for URL: " + url
        print "-------------------------------"
        xmi = get_xmi_from_html(description_url=url+'/ClassDescription.html')

        print "\nXMI content:"
        print xmi;
        print "--------------------------------"
        print

test_xmi_from_html()








