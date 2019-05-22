"""
    (c) by Piotr Goryl, S2Innoavation, 2018

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

import re
from pprint import pprint


def key_value_search(keys, text, assignment_patterns=[':=', ':', "="], quote_styles = ["'",  '"', '']):
    """
    Search for key-value pairs in the text definiend as key = value

    :param keys: iterable of keys to look for
    :param text: text to parse
    :param assignment_patterns: list of patterns of assignment sign
    :param quote_styles: styles of quotes around value
    :return: a dictionary of key-value pairs
    """

    # dictionary of values
    values_dict = {}

    assignment_group = '((' + (')|('.join(assignment_patterns)) + '))'

    # iterate through keys
    for key in keys:

        # check different possible matches
        mo = None
        value = None

        # iterate over quote styles
        for quote in quote_styles:
            # only if it has not found matching object
            if value is None:
                # quote part of a regular expression
                if len(quote) > 0:
                    quote_group = "(" + quote + ")"
                else:
                    quote_group = ''

                re_string = r"""((^)|(\s)|(,))""" + key + r"""\s*""" + assignment_group + r"""\s*""" + \
                               quote_group + r"""(?P<value>.+?)""" + quote_group + r"""((\s)|(,)|($))"""

                mo = re.search(re_string, text)

                if mo is not None:
                    value = mo.group('value')

        # if we have found a pattern
        if value is not None:
            print re_string
            values_dict[key] = value

    return values_dict


if __name__ == "__main__":
    # when modules is run it performs a manual tests
    # key_value_search_test
    key_value_search_texts =  [
        r"""( key1 := "key1 value", key2 = 'value of key2' m )""",
        r"""key3 := "key4 and key_5 values should be 3452.123" """,
        r"""  key4 := "3452.123", key_x = value_x""",
        r"""key5 =3452.123 ala ma kota key6:key6_is_that,"""
    ]

    for text in key_value_search_texts:
        pprint(key_value_search(['key', 'key1', 'key2', 'key3', '3', 'key4', 'key5', 'key6'], text))
