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


def get_class_content(source, start_point):
    """ Parse source from start_point (which sould be the first line of class
    :return: (name, content)
    """

    pass


def get_class_member(source, member_name):
    """
    Returns (eval) class memeber value. Useful for finding lists of attributes, commands and properties
    in device class definition
    :param source: source content
    :param member_name: name of a memebr to read from class definituin
    :return:
    """

    pass


def get_class_member_comment(source, member_name):
    """
    Get comment located just before a class member or its doc string.
    :param source: source content
    :param member_name: name of a member
    :return: (comment, docstring)
    """



def get_xmi_from_python(name, python_file_url):
    """

    :param name: name of the device server
    :param python_file: URL of the python file
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

    # read the file

    # find description part (comment)

    # find device server implementation (class deriving from Device_XImpl)

    # find Tango class definition

    # get list of attributes

    # get list of commands

    # get list of properties

    # generate xmi


    return '<?xml version="1.0" encoding="ASCII"?>' + etree.tostring(xmi_xml)
