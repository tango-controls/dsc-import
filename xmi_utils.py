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

# This module porvides some common staff fro parsing and generation of .xmi file

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
