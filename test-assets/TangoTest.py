# -*- coding: utf-8 -*-
#
# This file is part of the TangoTest project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" TANGO Device Server for testing generic clients

A device to test generic clients. It offers a \``echo\`` like command for
each TANGO data type (i.e. each command returns an exact copy of <argin>).
"""

__all__ = ["TangoTest", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import class_property, device_property
from PyTango import AttrQuality, AttrWriteType, DispLevel, DevState
# Additional import
# PROTECTED REGION ID(TangoTest.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  TangoTest.additionnal_import


class TangoTest(Device):
    """
    A device to test generic clients. It offers a \``echo\`` like command for
    each TANGO data type (i.e. each command returns an exact copy of <argin>).
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(TangoTest.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  TangoTest.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    Mthreaded_impl = device_property(
        dtype='int16',
    )
    Sleep_period = device_property(
        dtype='int',
    )
    UShort_image_ro_size = device_property(
        dtype='int', default_value=251
    )
    # ----------
    # Attributes
    # ----------

    ampli = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )
    boolean_scalar = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
        label="boolean_scalar",
        doc="A boolean scalar attribute",
    )
    double_scalar = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
    )
    double_scalar_rww = attribute(
        dtype='double',
        access=AttrWriteType.READ_WITH_WRITE,
    )
    double_scalar_w = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )
    float_scalar = attribute(
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        label="float_scalar",
        doc="A float attribute",
    )
    long64_scalar = attribute(
        dtype='int64',
        access=AttrWriteType.READ_WRITE,
    )
    long_scalar = attribute(
        dtype='int',
        access=AttrWriteType.READ_WRITE,
    )
    long_scalar_rww = attribute(
        dtype='int',
        access=AttrWriteType.READ_WITH_WRITE,
    )
    long_scalar_w = attribute(
        dtype='int',
        access=AttrWriteType.WRITE,
    )
    no_value = attribute(
        dtype='int',
    )
    short_scalar = attribute(
        dtype='int16',
        access=AttrWriteType.READ_WRITE,
    )
    short_scalar_ro = attribute(
        dtype='int16',
    )
    short_scalar_rww = attribute(
        dtype='int16',
        access=AttrWriteType.READ_WITH_WRITE,
    )
    short_scalar_w = attribute(
        dtype='int16',
        access=AttrWriteType.WRITE,
    )
    string_scalar = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )
    throw_exception = attribute(
        dtype='int',
    )
    uchar_scalar = attribute(
        dtype='char',
        access=AttrWriteType.READ_WRITE,
        label="uchar_scalar",
    )
    ulong64_scalar = attribute(
        dtype='uint64',
        access=AttrWriteType.READ_WRITE,
    )
    ushort_scalar = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        label="ushort_scalar",
    )
    ulong_scalar = attribute(
        dtype='uint',
        access=AttrWriteType.READ_WRITE,
    )
    boolean_spectrum = attribute(
        dtype=('bool',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
        label="boolean_spectrum",
    )
    boolean_spectrum_ro = attribute(
        dtype=('bool',),
        max_dim_x=4096,
    )
    double_spectrum = attribute(
        dtype=('double',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
    )
    double_spectrum_ro = attribute(
        dtype=('double',),
        max_dim_x=4096,
    )
    float_spectrum = attribute(
        dtype=('float',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
        label="float_spectrum",
        doc="A float spectrum attribute",
    )
    float_spectrum_ro = attribute(
        dtype=('float',),
        max_dim_x=4096,
    )
    long64_spectrum_ro = attribute(
        dtype=('int64',),
        max_dim_x=4096,
    )
    long_spectrum = attribute(
        dtype=('int',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
    )
    long_spectrum_ro = attribute(
        dtype=('int',),
        max_dim_x=4096,
    )
    short_spectrum = attribute(
        dtype=('int16',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
    )
    short_spectrum_ro = attribute(
        dtype=('int16',),
        max_dim_x=4096,
    )
    string_spectrum = attribute(
        dtype=('str',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=256,
    )
    string_spectrum_ro = attribute(
        dtype=('str',),
        max_dim_x=256,
    )
    uchar_spectrum = attribute(
        dtype=('char',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
        label="uchar_spectrum",
        max_value=255,
        min_value=0,
        doc="An unsigned char spectrum attribute",
    )
    uchar_spectrum_ro = attribute(
        dtype=('char',),
        max_dim_x=4096,
    )
    ulong64_spectrum_ro = attribute(
        dtype=('uint64',),
        max_dim_x=4096,
    )
    ulong_spectrum_ro = attribute(
        dtype=('uint',),
        max_dim_x=4096,
    )
    ushort_spectrum = attribute(
        dtype=('uint16',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
        label="ushort_spectrum",
        doc="An unsigned short spectrum attribute",
    )
    ushort_spectrum_ro = attribute(
        dtype=('uint16',),
        max_dim_x=4096,
    )
    wave = attribute(
        dtype=('double',),
        max_dim_x=4096,
    )
    boolean_image = attribute(
        dtype=(('bool',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    boolean_image_ro = attribute(
        dtype=(('bool',),),
        max_dim_x=251, max_dim_y=251,
        label="boolean_image",
    )
    double_image = attribute(
        dtype=(('double',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    double_image_ro = attribute(
        dtype=(('double',),),
        max_dim_x=251, max_dim_y=251,
    )
    float_image = attribute(
        dtype=(('float',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    float_image_ro = attribute(
        dtype=(('float',),),
        max_dim_x=251, max_dim_y=251,
        label="float_image",
        max_value=255,
        min_value=0,
        doc="A float image attribute",
    )
    long64_image_ro = attribute(
        dtype=(('int64',),),
        max_dim_x=251, max_dim_y=251,
    )
    long_image = attribute(
        dtype=(('int',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    long_image_ro = attribute(
        dtype=(('int',),),
        max_dim_x=251, max_dim_y=251,
    )
    short_image = attribute(
        dtype=(('int16',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    short_image_ro = attribute(
        dtype=(('int16',),),
        max_dim_x=251, max_dim_y=251,
    )
    string_image = attribute(
        dtype=(('str',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=256, max_dim_y=256,
    )
    string_image_ro = attribute(
        dtype=(('str',),),
        max_dim_x=256, max_dim_y=256,
    )
    uchar_image = attribute(
        dtype=(('char',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    uchar_image_ro = attribute(
        dtype=(('char',),),
        max_dim_x=251, max_dim_y=251,
        label="uchar_image",
        max_value=255,
        min_value=0,
        doc="An unsigned char image attribute",
    )
    ulong64_image_ro = attribute(
        dtype=(('uint64',),),
        max_dim_x=251, max_dim_y=251,
    )
    ulong_image_ro = attribute(
        dtype=(('uint',),),
        max_dim_x=251, max_dim_y=251,
    )
    ushort_image = attribute(
        dtype=(('uint16',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=251, max_dim_y=251,
    )
    ushort_image_ro = attribute(
        dtype=(('uint16',),),
        max_dim_x=8192, max_dim_y=8192,
        label="ushort_image_ro",
        max_value=255,
        min_value=0,
        doc="An unsigned short image attribute",
    )
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(TangoTest.init_device) ENABLED START #
        # PROTECTED REGION END #    //  TangoTest.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(TangoTest.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(TangoTest.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def write_ampli(self, value):
        # PROTECTED REGION ID(TangoTest.ampli_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ampli_write

    def read_boolean_scalar(self):
        # PROTECTED REGION ID(TangoTest.boolean_scalar_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  TangoTest.boolean_scalar_read

    def write_boolean_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.boolean_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.boolean_scalar_write

    def read_double_scalar(self):
        # PROTECTED REGION ID(TangoTest.double_scalar_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  TangoTest.double_scalar_read

    def write_double_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.double_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.double_scalar_write

    def read_double_scalar_rww(self):
        # PROTECTED REGION ID(TangoTest.double_scalar_rww_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  TangoTest.double_scalar_rww_read

    def write_double_scalar_rww(self, value):
        # PROTECTED REGION ID(TangoTest.double_scalar_rww_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.double_scalar_rww_write

    def write_double_scalar_w(self, value):
        # PROTECTED REGION ID(TangoTest.double_scalar_w_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.double_scalar_w_write

    def read_float_scalar(self):
        # PROTECTED REGION ID(TangoTest.float_scalar_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  TangoTest.float_scalar_read

    def write_float_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.float_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.float_scalar_write

    def read_long64_scalar(self):
        # PROTECTED REGION ID(TangoTest.long64_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.long64_scalar_read

    def write_long64_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.long64_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long64_scalar_write

    def read_long_scalar(self):
        # PROTECTED REGION ID(TangoTest.long_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.long_scalar_read

    def write_long_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.long_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long_scalar_write

    def read_long_scalar_rww(self):
        # PROTECTED REGION ID(TangoTest.long_scalar_rww_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.long_scalar_rww_read

    def write_long_scalar_rww(self, value):
        # PROTECTED REGION ID(TangoTest.long_scalar_rww_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long_scalar_rww_write

    def write_long_scalar_w(self, value):
        # PROTECTED REGION ID(TangoTest.long_scalar_w_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long_scalar_w_write

    def read_no_value(self):
        # PROTECTED REGION ID(TangoTest.no_value_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.no_value_read

    def read_short_scalar(self):
        # PROTECTED REGION ID(TangoTest.short_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.short_scalar_read

    def write_short_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.short_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.short_scalar_write

    def read_short_scalar_ro(self):
        # PROTECTED REGION ID(TangoTest.short_scalar_ro_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.short_scalar_ro_read

    def read_short_scalar_rww(self):
        # PROTECTED REGION ID(TangoTest.short_scalar_rww_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.short_scalar_rww_read

    def write_short_scalar_rww(self, value):
        # PROTECTED REGION ID(TangoTest.short_scalar_rww_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.short_scalar_rww_write

    def write_short_scalar_w(self, value):
        # PROTECTED REGION ID(TangoTest.short_scalar_w_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.short_scalar_w_write

    def read_string_scalar(self):
        # PROTECTED REGION ID(TangoTest.string_scalar_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  TangoTest.string_scalar_read

    def write_string_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.string_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.string_scalar_write

    def read_throw_exception(self):
        # PROTECTED REGION ID(TangoTest.throw_exception_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.throw_exception_read

    def read_uchar_scalar(self):
        # PROTECTED REGION ID(TangoTest.uchar_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.uchar_scalar_read

    def write_uchar_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.uchar_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.uchar_scalar_write

    def read_ulong64_scalar(self):
        # PROTECTED REGION ID(TangoTest.ulong64_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.ulong64_scalar_read

    def write_ulong64_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.ulong64_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ulong64_scalar_write

    def read_ushort_scalar(self):
        # PROTECTED REGION ID(TangoTest.ushort_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.ushort_scalar_read

    def write_ushort_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.ushort_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ushort_scalar_write

    def read_ulong_scalar(self):
        # PROTECTED REGION ID(TangoTest.ulong_scalar_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.ulong_scalar_read

    def write_ulong_scalar(self, value):
        # PROTECTED REGION ID(TangoTest.ulong_scalar_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ulong_scalar_write

    def read_boolean_spectrum(self):
        # PROTECTED REGION ID(TangoTest.boolean_spectrum_read) ENABLED START #
        return [False]
        # PROTECTED REGION END #    //  TangoTest.boolean_spectrum_read

    def write_boolean_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.boolean_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.boolean_spectrum_write

    def read_boolean_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.boolean_spectrum_ro_read) ENABLED START #
        return [False]
        # PROTECTED REGION END #    //  TangoTest.boolean_spectrum_ro_read

    def read_double_spectrum(self):
        # PROTECTED REGION ID(TangoTest.double_spectrum_read) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.double_spectrum_read

    def write_double_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.double_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.double_spectrum_write

    def read_double_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.double_spectrum_ro_read) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.double_spectrum_ro_read

    def read_float_spectrum(self):
        # PROTECTED REGION ID(TangoTest.float_spectrum_read) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.float_spectrum_read

    def write_float_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.float_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.float_spectrum_write

    def read_float_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.float_spectrum_ro_read) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.float_spectrum_ro_read

    def read_long64_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.long64_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.long64_spectrum_ro_read

    def read_long_spectrum(self):
        # PROTECTED REGION ID(TangoTest.long_spectrum_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.long_spectrum_read

    def write_long_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.long_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long_spectrum_write

    def read_long_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.long_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.long_spectrum_ro_read

    def read_short_spectrum(self):
        # PROTECTED REGION ID(TangoTest.short_spectrum_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.short_spectrum_read

    def write_short_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.short_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.short_spectrum_write

    def read_short_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.short_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.short_spectrum_ro_read

    def read_string_spectrum(self):
        # PROTECTED REGION ID(TangoTest.string_spectrum_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  TangoTest.string_spectrum_read

    def write_string_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.string_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.string_spectrum_write

    def read_string_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.string_spectrum_ro_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  TangoTest.string_spectrum_ro_read

    def read_uchar_spectrum(self):
        # PROTECTED REGION ID(TangoTest.uchar_spectrum_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.uchar_spectrum_read

    def write_uchar_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.uchar_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.uchar_spectrum_write

    def read_uchar_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.uchar_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.uchar_spectrum_ro_read

    def read_ulong64_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.ulong64_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.ulong64_spectrum_ro_read

    def read_ulong_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.ulong_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.ulong_spectrum_ro_read

    def read_ushort_spectrum(self):
        # PROTECTED REGION ID(TangoTest.ushort_spectrum_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.ushort_spectrum_read

    def write_ushort_spectrum(self, value):
        # PROTECTED REGION ID(TangoTest.ushort_spectrum_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ushort_spectrum_write

    def read_ushort_spectrum_ro(self):
        # PROTECTED REGION ID(TangoTest.ushort_spectrum_ro_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.ushort_spectrum_ro_read

    def read_wave(self):
        # PROTECTED REGION ID(TangoTest.wave_read) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.wave_read

    def read_boolean_image(self):
        # PROTECTED REGION ID(TangoTest.boolean_image_read) ENABLED START #
        return [[False]]
        # PROTECTED REGION END #    //  TangoTest.boolean_image_read

    def write_boolean_image(self, value):
        # PROTECTED REGION ID(TangoTest.boolean_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.boolean_image_write

    def read_boolean_image_ro(self):
        # PROTECTED REGION ID(TangoTest.boolean_image_ro_read) ENABLED START #
        return [[False]]
        # PROTECTED REGION END #    //  TangoTest.boolean_image_ro_read

    def read_double_image(self):
        # PROTECTED REGION ID(TangoTest.double_image_read) ENABLED START #
        return [[0.0]]
        # PROTECTED REGION END #    //  TangoTest.double_image_read

    def write_double_image(self, value):
        # PROTECTED REGION ID(TangoTest.double_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.double_image_write

    def read_double_image_ro(self):
        # PROTECTED REGION ID(TangoTest.double_image_ro_read) ENABLED START #
        return [[0.0]]
        # PROTECTED REGION END #    //  TangoTest.double_image_ro_read

    def read_float_image(self):
        # PROTECTED REGION ID(TangoTest.float_image_read) ENABLED START #
        return [[0.0]]
        # PROTECTED REGION END #    //  TangoTest.float_image_read

    def write_float_image(self, value):
        # PROTECTED REGION ID(TangoTest.float_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.float_image_write

    def read_float_image_ro(self):
        # PROTECTED REGION ID(TangoTest.float_image_ro_read) ENABLED START #
        return [[0.0]]
        # PROTECTED REGION END #    //  TangoTest.float_image_ro_read

    def read_long64_image_ro(self):
        # PROTECTED REGION ID(TangoTest.long64_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.long64_image_ro_read

    def read_long_image(self):
        # PROTECTED REGION ID(TangoTest.long_image_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.long_image_read

    def write_long_image(self, value):
        # PROTECTED REGION ID(TangoTest.long_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.long_image_write

    def read_long_image_ro(self):
        # PROTECTED REGION ID(TangoTest.long_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.long_image_ro_read

    def read_short_image(self):
        # PROTECTED REGION ID(TangoTest.short_image_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.short_image_read

    def write_short_image(self, value):
        # PROTECTED REGION ID(TangoTest.short_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.short_image_write

    def read_short_image_ro(self):
        # PROTECTED REGION ID(TangoTest.short_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.short_image_ro_read

    def read_string_image(self):
        # PROTECTED REGION ID(TangoTest.string_image_read) ENABLED START #
        return [['']]
        # PROTECTED REGION END #    //  TangoTest.string_image_read

    def write_string_image(self, value):
        # PROTECTED REGION ID(TangoTest.string_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.string_image_write

    def read_string_image_ro(self):
        # PROTECTED REGION ID(TangoTest.string_image_ro_read) ENABLED START #
        return [['']]
        # PROTECTED REGION END #    //  TangoTest.string_image_ro_read

    def read_uchar_image(self):
        # PROTECTED REGION ID(TangoTest.uchar_image_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.uchar_image_read

    def write_uchar_image(self, value):
        # PROTECTED REGION ID(TangoTest.uchar_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.uchar_image_write

    def read_uchar_image_ro(self):
        # PROTECTED REGION ID(TangoTest.uchar_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.uchar_image_ro_read

    def read_ulong64_image_ro(self):
        # PROTECTED REGION ID(TangoTest.ulong64_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.ulong64_image_ro_read

    def read_ulong_image_ro(self):
        # PROTECTED REGION ID(TangoTest.ulong_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.ulong_image_ro_read

    def read_ushort_image(self):
        # PROTECTED REGION ID(TangoTest.ushort_image_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.ushort_image_read

    def write_ushort_image(self, value):
        # PROTECTED REGION ID(TangoTest.ushort_image_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.ushort_image_write

    def read_ushort_image_ro(self):
        # PROTECTED REGION ID(TangoTest.ushort_image_ro_read) ENABLED START #
        return [[0]]
        # PROTECTED REGION END #    //  TangoTest.ushort_image_ro_read

    # --------
    # Commands
    # --------

    @command
    @DebugIt()
    def CrashFromDevelopperThread(self):
        # PROTECTED REGION ID(TangoTest.CrashFromDevelopperThread) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.CrashFromDevelopperThread

    @command
    @DebugIt()
    def CrashFromOmniThread(self):
        # PROTECTED REGION ID(TangoTest.CrashFromOmniThread) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.CrashFromOmniThread

    @command(dtype_in='bool', 
    doc_in="Any boolean value", 
    dtype_out='bool', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevBoolean(self, argin):
        # PROTECTED REGION ID(TangoTest.DevBoolean) ENABLED START #
        return False
        # PROTECTED REGION END #    //  TangoTest.DevBoolean

    @command(dtype_in='double', 
    doc_in="Any DevDouble value", 
    dtype_out='double', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevDouble(self, argin):
        # PROTECTED REGION ID(TangoTest.DevDouble) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  TangoTest.DevDouble

    @command(dtype_in='float', 
    doc_in="Any DevFloat value", 
    dtype_out='float', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevFloat(self, argin):
        # PROTECTED REGION ID(TangoTest.DevFloat) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  TangoTest.DevFloat

    @command(dtype_in='int', 
    doc_in="Any DevLong value", 
    dtype_out='int', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevLong(self, argin):
        # PROTECTED REGION ID(TangoTest.DevLong) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevLong

    @command(dtype_in='int64', 
    doc_in="Any DevLong64 value", 
    dtype_out='int64', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevLong64(self, argin):
        # PROTECTED REGION ID(TangoTest.DevLong64) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevLong64

    @command(dtype_in='int16', 
    doc_in="Any DevShort value", 
    dtype_out='int16', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevShort(self, argin):
        # PROTECTED REGION ID(TangoTest.DevShort) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevShort

    @command(dtype_in='str', 
    doc_in="-", 
    dtype_out='str', 
    doc_out="-"
    )
    @DebugIt()
    def DevString(self, argin):
        # PROTECTED REGION ID(TangoTest.DevString) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  TangoTest.DevString

    @command(dtype_in='uint', 
    doc_in="Any DevULong", 
    dtype_out='uint', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevULong(self, argin):
        # PROTECTED REGION ID(TangoTest.DevULong) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevULong

    @command(dtype_in='uint64', 
    doc_in="Any DevULong64 value", 
    dtype_out='uint64', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevULong64(self, argin):
        # PROTECTED REGION ID(TangoTest.DevULong64) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevULong64

    @command(dtype_in='uint16', 
    doc_in="Any DevUShort value", 
    dtype_out='uint16', 
    doc_out="Echo of the argin value"
    )
    @DebugIt()
    def DevUShort(self, argin):
        # PROTECTED REGION ID(TangoTest.DevUShort) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  TangoTest.DevUShort

    @command(dtype_in=('char',), 
    doc_in="-", 
    dtype_out=('char',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarCharArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarCharArray) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarCharArray

    @command(dtype_in=('double',), 
    doc_in="-", 
    dtype_out=('double',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarDoubleArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarDoubleArray) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.DevVarDoubleArray

    @command(dtype_in='DevVarDoubleStringArray', 
    doc_in="-", 
    dtype_out='DevVarDoubleStringArray', 
    doc_out="-"
    )
    @DebugIt()
    def DevVarDoubleStringArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarDoubleStringArray) ENABLED START #
        return [[0.0], [""]]
        # PROTECTED REGION END #    //  TangoTest.DevVarDoubleStringArray

    @command(dtype_in=('float',), 
    doc_in="-", 
    dtype_out=('float',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarFloatArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarFloatArray) ENABLED START #
        return [0.0]
        # PROTECTED REGION END #    //  TangoTest.DevVarFloatArray

    @command(dtype_in=('int64',), 
    dtype_out=('int64',), 
    )
    @DebugIt()
    def DevVarLong64Array(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarLong64Array) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarLong64Array

    @command(dtype_in=('int',), 
    doc_in="-", 
    dtype_out=('int',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarLongArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarLongArray) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarLongArray

    @command(dtype_in='DevVarLongStringArray', 
    doc_in="-", 
    dtype_out='DevVarLongStringArray', 
    doc_out="-"
    )
    @DebugIt()
    def DevVarLongStringArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarLongStringArray) ENABLED START #
        return [[0], [""]]
        # PROTECTED REGION END #    //  TangoTest.DevVarLongStringArray

    @command(dtype_in=('int16',), 
    doc_in="-", 
    dtype_out=('int16',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarShortArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarShortArray) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarShortArray

    @command(dtype_in=('str',), 
    doc_in="-", 
    dtype_out=('str',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarStringArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarStringArray) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  TangoTest.DevVarStringArray

    @command(dtype_in=('uint64'), 
    dtype_out=('uint64'), 
    )
    @DebugIt()
    def DevVarULong64Array(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarULong64Array) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarULong64Array

    @command(dtype_in=('uint',), 
    doc_in="-", 
    dtype_out=('uint',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarULongArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarULongArray) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarULongArray

    @command(dtype_in=('uint16',), 
    doc_in="-", 
    dtype_out=('uint16',), 
    doc_out="-"
    )
    @DebugIt()
    def DevVarUShortArray(self, argin):
        # PROTECTED REGION ID(TangoTest.DevVarUShortArray) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  TangoTest.DevVarUShortArray

    @command
    @DebugIt()
    def DevVoid(self):
        # PROTECTED REGION ID(TangoTest.DevVoid) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.DevVoid

    @command
    @DebugIt()
    def DumpExecutionState(self):
        # PROTECTED REGION ID(TangoTest.DumpExecutionState) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.DumpExecutionState

    @command
    @DebugIt()
    def SwitchStates(self):
        # PROTECTED REGION ID(TangoTest.SwitchStates) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TangoTest.SwitchStates

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(TangoTest.main) ENABLED START #
    from PyTango.server import run
    return run((TangoTest,), args=args, **kwargs)
    # PROTECTED REGION END #    //  TangoTest.main

if __name__ == '__main__':
    main()
