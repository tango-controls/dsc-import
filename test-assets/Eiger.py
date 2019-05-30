from tango import AttrQuality, AttrWriteType, DispLevel
from tango.server import Device, attribute, command, server_run
from tango.server import class_property, device_property
from tango import DevLong, DevFloat, DevBoolean, DevString, DevVarStringArray
from eiger import EigerDetector

import tango

import os
import glob
import sys
#sys.path.append("grpc_utils")

from Eiger.filewriter_grpc.client import Client as FileWriterClient

class Eiger(Device):
    ### PROPERTIES

    host = device_property(dtype=str)
    port = device_property(dtype=int, default_value=80)
    data_host = device_property(dtype=str)
    data_port = device_property(dtype=int, default_value=80)
    filewriter_host = device_property(dtype=str)
    filewriter_port = device_property(dtype=int)
    api_version= device_property(dtype=str, default_value="1.6.0")
    beamline = device_property(dtype=str)
    path_prefix = device_property(dtype=str, default_value="/data")

    # Internal vars
    flag_arm = False
    must_flag_arm = False
    __NbImages_cache = 0
    __Temperature_cache = 0
    __Humidity_cache = 0
    __CountTime_cache = 0
    __FrameTime_cache =0
    __PhotonEnergy_cache = 0
    __Wavelength_cache = 0
    __EnergyThreshold_cache = 0
    __FlatfieldEnabled_cache = 0
    __AutoSummationEnabled_cache = False
    __TriggerMode_cache = None
    __RateCorrectionEnabled_cache = False
    __BitDepth_cache = 0
    __ReadoutTime_cache = 0
    __Description_cache = ''
    __NbTriggers_cache = 0
    __CountTimeInte_cache = 0
    __DownloadDirectory_cache = ''
    __DcuBufferFree_cache = 0
    __BeamCenterX_cache = 0
    __BeamCenterY_cache = 0
    __DetectorDistance_cache = 0
    __OmegaIncrement_cache = 0
    __OmegaStart_cache = 0
    __Compression_cache = ''
    __RoiMode_cache = ''
    __XPixelSize_cache = 0
    __XPixelSize_cache = 0

    # attributes from EigerFileWriter
    __FilewriterMode_cache = ''
    __TransferMode_cache = ''
    __ImagesPerFile_cache = 0
    __ImageNbStart_cache = 0
    __FilenamePattern_cache = ''
    __CompressionEnabled_cache = 0
    __FilewriterState_cache = ''
    __BufferFree_cache = 0
    __FilewriterError_cache = ['']

    # attributes from EigerMonitor
    __MonitorMode_cache = ''
    __BufferSize_cache = 0
    __MonitorState_cache = ''
    __MonitorError_cache = ['']

    ### ATTRIBUTES

    def is_request_value_allowed(self):
        rstate = self.eiger.get_state()
        # the following if clause resets the arm flag after an acquisition
        if self.flag_arm and ( rstate == "configure" or rstate == "idle"):
                self.debug_stream("In is_request_value_allowed()... flag gonna reset")
                self.flag_arm = False

        allowed = (not self.flag_arm and self.get_state() != tango.DevState.MOVING)
        self.debug_stream("Request is allowed: %s" %allowed)
        return allowed

    MustArmFlag = attribute(label="MustArmFlag", dtype=DevBoolean,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_MustArmFlag", fset="set_MustArmFlag",
                        doc="Tells if arming is necessary, ussually after a parameter change")

    def get_MustArmFlag(self):
        return self.must_flag_arm

    def set_MustArmFlag(self, value):
        self.must_flag_arm = value

    NbImages = attribute(label="NbImages", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_NbImages", fset="set_NbImages",
                        doc="Number of images per series")

    def get_NbImages(self):
        if self.is_request_value_allowed():
            self.__NbImages_cache = self.eiger.nimages
        return self.__NbImages_cache

    def set_NbImages(self, nbimages):
        self.eiger.nimages = nbimages
        self.MustArmFlag.set_value(True)

    Temperature = attribute(label="Temperature", dtype=DevFloat,
                        access=AttrWriteType.READ,
                        fget="get_temperature",
                        doc="Detector temperature")

    def get_temperature(self):
        if self.is_request_value_allowed():
            # Workaround: this might get fixed in api v1.8.x
            self.eiger.status_update()
            self.__Temperature_cache = self.eiger.temperature
        return self.__Temperature_cache

    Humidity = attribute(label="Humidity", dtype=DevFloat,
                        access=AttrWriteType.READ,
                        fget="get_humidity",
                        doc="Detector humidity")

    def get_humidity(self):
        if self.is_request_value_allowed():
            # Workaround: this might get fixed in api v1.8.x
            self.eiger.status_update()
            self.__Humidity_cache = self.eiger.humidity
        return self.__Humidity_cache

    CountTime = attribute(label="CountTime", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_CountTime", fset="set_CountTime",
                        doc="CountTime")

    def get_CountTime(self):
        if self.is_request_value_allowed():
            self.__CountTime_cache = self.eiger.count_time
        return self.__CountTime_cache

    def set_CountTime(self, count_time):
        self.eiger.count_time = count_time
        self.MustArmFlag.set_value(True)

    FrameTime = attribute(label="FrameTime", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_FrameTime", fset="set_FrameTime",
                        doc="FrameTime")

    def get_FrameTime(self):
        if self.is_request_value_allowed():
            self.__FrameTime_cache = self.eiger.frame_time
        return self.__FrameTime_cache

    def set_FrameTime(self, frame_time):
        self.eiger.frame_time = frame_time
        self.MustArmFlag.set_value(True)

    PhotonEnergy = attribute(label="PhotonEnergy", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_PhotonEnergy", fset="set_PhotonEnergy",
                        doc="PhotonEnergy")

    def get_PhotonEnergy(self):
        if self.is_request_value_allowed():
            self.__PhotonEnergy_cache = self.eiger.energy
        return self.__PhotonEnergy_cache

    def set_PhotonEnergy(self, energy):
        self.eiger.energy = energy
        self.MustArmFlag.set_value(True)

    Wavelength = attribute(label="Wavelength", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_Wavelength", fset="set_Wavelength",
                        doc="Wavelength")

    def get_Wavelength(self):
        if self.is_request_value_allowed():
            self.__Wavelength_cache = self.eiger.wavelength
        return self.__Wavelength_cache

    def set_Wavelength(self, wavelength):
        self.eiger.wavelength = wavelength
        self.MustArmFlag.set_value(True)

    EnergyThreshold = attribute(label="EnergyThreshold", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_EnergyThreshold", fset="set_EnergyThreshold",
                        doc="EnergyThreshold")

    def get_EnergyThreshold(self):
        if self.is_request_value_allowed():
            self.__EnergyThreshold_cache = self.eiger.threshold
        return self.__EnergyThreshold_cache

    def set_EnergyThreshold(self, threshold):
        self.eiger.threshold = threshold
        self.MustArmFlag.set_value(True)


    FlatfieldEnabled = attribute(label="FlatfieldEnabled", dtype=DevBoolean,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_FlatfieldEnabled", fset="set_FlatfieldEnabled",
                        doc="FlatfieldEnabled")

    def get_FlatfieldEnabled(self):
        if self.is_request_value_allowed():
            self.__FlatfieldEnabled_cache = self.eiger.flatfield_enabled
        return self.__FlatfieldEnabled_cache

    def set_FlatfieldEnabled(self, flatfield_enabled):
        self.eiger.flatfield_enabled = flatfield_enabled
        self.MustArmFlag.set_value(True)

    AutoSummationEnabled = attribute(label="AutoSummationEnabled", dtype=DevBoolean,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_AutoSummationEnabled", fset="set_AutoSummationEnabled",
                        doc="AutoSummationEnabled")

    def get_AutoSummationEnabled(self):
        if self.is_request_value_allowed():
            self.__AutoSummationEnabled_cache = self.eiger.auto_summation_enabled
        return self.__AutoSummationEnabled_cache

    def set_AutoSummationEnabled(self, auto_summation_enabled):
        self.eiger.auto_summation_enabled = auto_summation_enabled
        self.MustArmFlag.set_value(True)


    TriggerMode = attribute(label="TriggerMode", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_TriggerMode", fset="set_TriggerMode",
                        doc="TriggerMode")

    def get_TriggerMode(self):
        if self.is_request_value_allowed():
            self.__TriggerMode_cache = self.eiger.trigger_mode
        return self.__TriggerMode_cache

    def set_TriggerMode(self, trigger_mode):
        self.eiger.trigger_mode = trigger_mode
        self.MustArmFlag.set_value(True)

    RateCorrectionEnabled = attribute(label="RateCorrectionEnabled", dtype=DevBoolean,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_RateCorrectionEnabled", fset="set_RateCorrectionEnabled",
                        doc="RateCorrectionEnabled")

    def get_RateCorrectionEnabled(self):
        if self.is_request_value_allowed():
            self.__RateCorrectionEnabled_cache = self.eiger.rate_correction_enabled
        return self.__RateCorrectionEnabled_cache

    def set_RateCorrectionEnabled(self, rate_correction_enabled):
        self.eiger.rate_correction_enabled = rate_correction_enabled
        self.MustArmFlag.set_value(True)

    BitDepth = attribute(label="BitDepth", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_BitDepth",
                        doc="BitDepth")

    def get_BitDepth(self):
        if self.is_request_value_allowed():
            self.__BitDepth_cache = self.eiger.bit_depth
        return self.__BitDepth_cache

    ReadoutTime = attribute(label="ReadoutTime", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_ReadoutTime",
                        doc="ReadoutTime")

    def get_ReadoutTime(self):
        if self.is_request_value_allowed():
            self.__ReadoutTime_cache = self.eiger.readout_time
        return self.__ReadoutTime_cache

    Description = attribute(label="Description", dtype=DevString,
                        access=AttrWriteType.READ,
                        fget="get_Description",
                        doc="Description")

    def get_Description(self):
        if self.is_request_value_allowed():
            self.__Description_cache = self.eiger.description
        return self.__Description_cache

    Time = attribute(label="Time", dtype=DevString,
                        access=AttrWriteType.READ,
                        fget="get_Time",
                        doc="Detector Time")

    def get_Time(self):
        return self.eiger.detector_time


    NbTriggers = attribute(label="NbTriggers", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_NbTriggers", fset="set_NbTriggers",
                        doc="NbTriggers")

    def get_NbTriggers(self):
        if self.is_request_value_allowed():
            self.__NbTriggers_cache = self.eiger.ntrigger
        return self.__NbTriggers_cache

    def set_NbTriggers(self, ntrigger):
        self.eiger.ntrigger = ntrigger
        self.MustArmFlag.set_value(True)


    CountTimeInte = attribute(label="CountTimeInte", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_CountTimeInte", fset="set_CountTimeInte",
                        doc="CountTimeInte")

    def get_CountTimeInte(self):
        return self.__CountTimeInte_cache

    def set_CountTimeInte(self, CountTimeInte):
        self.__CountTimeInte_cache = CountTimeInte

    DownloadDirectory = attribute(label="DownloadDirectory", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_DownloadDirectory", fset="set_DownloadDirectory",
                        doc="DownloadDirectory")

    def get_DownloadDirectory(self):
        return self.__DownloadDirectory_cache

    def set_DownloadDirectory(self, DownloadDirectory):
        self.__DownloadDirectory_cache = DownloadDirectory


    DcuBufferFree = attribute(label="DcuBufferFree", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_DcuBufferFree",
                        doc="DcuBufferFree Time")

    def get_DcuBufferFree(self):
        if self.is_request_value_allowed():
            self.__DcuBufferFree_cache = self.eiger.dcu_buffer_free
        return self.__DcuBufferFree_cache

    BeamCenterX = attribute(label="BeamCenterX", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_BeamCenterX", fset="set_BeamCenterX",
                        doc="BeamCenterX")

    def get_BeamCenterX(self):
        if self.is_request_value_allowed():
            self.__BeamCenterX_cache = self.eiger.beam_center_x
        return self.__BeamCenterX_cache

    def set_BeamCenterX(self, beam_center_x):
        self.eiger.beam_center_x = beam_center_x
        self.MustArmFlag.set_value(True)

    BeamCenterY = attribute(label="BeamCenterY", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_BeamCenterY", fset="set_BeamCenterY",
                        doc="BeamCenterY")

    def get_BeamCenterY(self):
        if self.is_request_value_allowed():
            self.__BeamCenterY_cache = self.eiger.beam_center_y
        return self.__BeamCenterY_cache

    def set_BeamCenterY(self, beam_center_y):
        self.eiger.beam_center_y = beam_center_y
        self.MustArmFlag.set_value(True)


    DetectorDistance = attribute(label="DetectorDistance", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_BeamCenterY", fset="set_BeamCenterY",
                        doc="DetectorDistance")

    def get_DetectorDistance(self):
        if self.is_request_value_allowed():
            self.__DetectorDistance_cache = self.eiger.detector_distance
        return self.__DetectorDistance_cache

    def set_DetectorDistance(self, detector_distance):
        self.eiger.detector_distance = detector_distance
        self.MustArmFlag.set_value(True)

    OmegaIncrement = attribute(label="OmegaIncrement", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_OmegaIncrement", fset="set_OmegaIncrement",
                        doc="OmegaIncrement")

    def get_OmegaIncrement(self):
        if self.is_request_value_allowed():
            self.__OmegaIncrement_cache = self.eiger.omega_increment
        return self.__OmegaIncrement_cache

    def set_OmegaIncrement(self, omega_increment):
        self.eiger.omega_increment = omega_increment
        self.MustArmFlag.set_value(True)

    OmegaStart = attribute(label="OmegaStart", dtype=DevFloat,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_OmegaStart", fset="set_OmegaStart",
                        doc="OmegaStart")

    def get_OmegaStart(self):
        if self.is_request_value_allowed():
            self.__OmegaStart_cache = self.eiger.omega_start
        return self.__OmegaStart_cache

    def set_OmegaStart(self, omega_start):
        self.eiger.omega_start = omega_start
        self.MustArmFlag.set_value(True)


    Compression = attribute(label="Compression", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_Compression", fset="set_Compression",
                        doc="Compression")

    def get_Compression(self):
        if self.is_request_value_allowed():
            self.__Compression_cache = self.eiger.compression
        return self.__Compression_cache

    def set_Compression(self, compression):
        self.eiger.compression = compression
        self.MustArmFlag.set_value(True)

    RoiMode = attribute(label="RoiMode", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_RoiMode", fset="set_RoiMode",
                        doc="RoiMode")

    def get_RoiMode(self):
        if self.is_request_value_allowed():
            self.__RoiMode_cache = self.eiger.roi_mode
        return self.__RoiMode_cache

    def set_RoiMode(self, roi_mode):
        self.eiger.roi_mode = roi_mode
        # self.__XPixelsDetector_cache = self.eiger.x_pixels_detector
        # self.__YPixelsDetector_cache = self.eiger.y_pixels_detector

        self.MustArmFlag.set_value(True)

    XPixelSize = attribute(label="XPixelSize", dtype=DevFloat,
                        access=AttrWriteType.READ,
                        fget="get_XPixelSize",
                        doc="XPixelSize")

    def get_XPixelSize(self):
        return self.__XPixelSize_cache

    YPixelSize = attribute(label="YPixelSize", dtype=DevFloat,
                        access=AttrWriteType.READ,
                        fget="get_YPixelSize",
                        doc="YPixelSize")

    def get_YPixelSize(self):
        return self.__YPixelSize_cache

    XPixelsDetector = attribute(label="XPixelsDetector", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_XPixelsDetector",
                        doc="XPixelsDetector")

    def get_XPixelsDetector(self):
        return self.eiger.x_pixels_detector

    YPixelsDetector = attribute(label="YPixelsDetector", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_YPixelsDetector",
                        doc="YPixelsDetector")

    def get_YPixelsDetector(self):
        return self.eiger.y_pixels_detector

    FilesInBuffer = attribute(label="FilesInBuffer", dtype=(str,),
                        max_dim_x=1000, # important limit for the number of files
                        access=AttrWriteType.READ,
                        fget="get_FilesInBuffer",
                        doc="FilesInBuffer")

    def get_FilesInBuffer(self):
        return self.eiger.buffer.files

    Error = attribute(label="Error", dtype=(str,),
                        access=AttrWriteType.READ,
                        fget="get_Error",
                        doc="Error")

    def get_Error(self):
        error = []
        for line in self.eiger.error:
            error.append(line)
        return error


    CollectionUUID = attribute(label="CollectionUUID", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_CollectionUUID", fset="set_CollectionUUID",
                        doc="CollectionUUID")

    def get_CollectionUUID(self):
        return self.eiger.buffer.CollectionUUID

    def set_CollectionUUID(self, CollectionUUID):
        self.eiger.buffer.CollectionUUID = CollectionUUID

    HeaderDetail = attribute(label="HeaderDetail", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_HeaderDetail", fset="set_HeaderDetail",
                        doc="HeaderDetail")

    def get_HeaderDetail(self):
        return self.eiger.stream.header_detail

    def set_HeaderDetail(self, header_detail):
        self.eiger.stream.header_detail = header_detail

    HeaderAppendix = attribute(label="HeaderAppendix", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_HeaderAppendix", fset="set_HeaderAppendix",
                        doc="HeaderAppendix")

    def get_HeaderAppendix(self):
        return self.eiger.stream.header_appendix

    def set_HeaderAppendix(self, header_appendix):
        self.eiger.stream.header_appendix = header_appendix

    ImageAppendix = attribute(label="ImageAppendix", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_ImageAppendix", fset="set_ImageAppendix",
                        doc="ImageAppendix")

    def get_ImageAppendix(self):
        return self.eiger.stream.image_appendix

    def set_ImageAppendix(self, image_appendix):
        self.eiger.stream.image_appendix = image_appendix

    StreamState = attribute(label="StreamState", dtype=DevString,
                        access=AttrWriteType.READ,
                        fget="get_StreamState",
                        doc="StreamState")

    def get_StreamState(self):
        return self.eiger.stream.stream_state

    StreamError = attribute(label="StreamError", dtype=(str,),
                        max_dim_x=20, # important limit for the string array
                        access=AttrWriteType.READ,
                        fget="get_StreamError",
                        doc="StreamError")

    def get_StreamError(self):
        return self.eiger.stream.stream_error

    StreamDropped = attribute(label="StreamDropped", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_StreamDropped",
                        doc="StreamDropped")

    def get_StreamDropped(self):
        return self.eiger.stream.stream_dropped

    ### ATTRIBUTES from FileWriter
    FilewriterMode = attribute(label="FilewriterMode", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_FilewriterMode", fset="set_FilewriterMode",
                        doc="Operation mode, can be enabled or disabled.")

    def get_FilewriterMode(self):
        if self.is_request_value_allowed():
            self.__FilewriterMode_cache = self.eiger.filewriter.mode
        return self.__FilewriterMode_cache

    def set_FilewriterMode(self, mode):
        self.eiger.filewriter.mode = mode

    TransferMode = attribute(label="TransferMode", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_TransferMode", fset="set_TransferMode",
                        doc="Transfer mode. Currently only http is supported.")

    def get_TransferMode(self):
        if self.is_request_value_allowed():
            self.__TransferMode_cache = self.eiger.filewriter.transfer_mode
        return self.__TransferMode_cache

    def set_TransferMode(self, transfer_mode):
        self.eiger.filewriter.transfer_mode = transfer_mode

    ImagesPerFile = attribute(label="ImagesPerFile", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_ImagesPerFile", fset="set_ImagesPerFile",
##                        min_value=1,
                        doc="Number of images stored in a single data file.")

    def get_ImagesPerFile(self):
        if self.is_request_value_allowed():
            self.__ImagesPerFile_cache = self.eiger.filewriter.images_per_file
        return self.__ImagesPerFile_cache

    def set_ImagesPerFile(self, images_per_file):
        self.eiger.filewriter.images_per_file = images_per_file

    ImageNbStart = attribute(label="ImageNbStart", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_ImageNbStart", fset="set_ImageNbStart",
                        doc="image_nr_low metadata parameter in the first HDF5 data file.")

    def get_ImageNbStart(self):
        if self.is_request_value_allowed():
            self.__ImageNbStart_cache = self.eiger.filewriter.image_nr_start
        return self.__ImageNbStart_cache

    def set_ImageNbStart(self, image_nb_start):
        self.eiger.image_nb_start = image_nb_start

    FilenamePattern = attribute(label="FilenamePattern", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_FilenamePattern", fset="set_FilenamePattern",
                        doc="The file naming pattern.")

    def get_FilenamePattern(self):
        if self.is_request_value_allowed():
            self.__FilenamePattern_cache = self.eiger.filewriter.filename_pattern
        return self.__FilenamePattern_cache

    def set_FilenamePattern(self, filename_pattern):
        e = Exception("Invalid path. Must be /data/<user-type>/" + self.beamline + "/<proposal-id>/...")
        if not filename_pattern.startswith("/"):
            raise e

        parts = filename_pattern.split("/")
        if not parts[1] == "data":
            raise e

        if not parts[3] == self.beamline:
            raise e

        self.eiger.filewriter.filename_pattern = filename_pattern
        self.MustArmFlag.set_value(True)

    CompressionEnabled = attribute(label="CompressionEnabled", dtype=DevLong,  ## check type: bool?
                        access=AttrWriteType.READ_WRITE,
                        fget="get_CompressionEnabled", fset="set_CompressionEnabled",
                        doc="True if the LZ4 data compression is enabled, False otherwise.")

    def get_CompressionEnabled(self):
        if self.is_request_value_allowed():
            self.__CompressionEnabled_cache = self.eiger.filewriter.compression_enabled
        return self.__CompressionEnabled_cache

    def set_CompressionEnabled(self, compression_enabled):
        self.eiger.filewriter.compression_enabled = compression_enabled

    FilewriterState = attribute(label="FilewriterState", dtype=DevString,
                        access=AttrWriteType.READ,
                        fget="get_FilewriterState",
                        doc="The filewriter`s status. The status can be one of disabled,\nready, acquire, and error.")

    def get_FilewriterState(self):
        return self.eiger.filewriter.status

    BufferFree = attribute(label="BufferFree", dtype=DevLong,
                        access=AttrWriteType.READ,
                        fget="get_BufferFree",
                        doc="Remaining buffer space in KB.", unit="kB")

    def get_BufferFree(self):
        return self.eiger.filewriter.buffer_free

    FilewriterError = attribute(label="FilewriterError", dtype=(str,),
                        max_dim_x=20, # important limit for the string array
                        access=AttrWriteType.READ,
                        fget="get_FilewriterError",
                        doc="List of status parameters causing error state.")

    def get_FilewriterError(self):
        return self.eiger.filewriter.error

    ### ATTRIBUTES from Monitor
    MonitorMode = attribute(label="MonitorMode", dtype=DevString,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_MonitorMode", fset="set_MonitorMode",
                        doc="Monitor operation mode.")

    def get_MonitorMode(self):
        if self.is_request_value_allowed():
            self.__MonitorMode_cache = self.eiger.monitor.mode
        return self.__MonitorMode_cache

    def set_MonitorMode(self, monitor_mode):
        self.eiger.monitor.mode = monitor_mode

    BufferSize = attribute(label="BufferSize", dtype=DevLong,
                        access=AttrWriteType.READ_WRITE,
                        fget="get_BufferSize", fset="set_BufferSize",
                        doc="Number of images that can be buffered in the monitor interface.")

    def get_BufferSize(self):
        if self.is_request_value_allowed():
            self.__BufferSize_cache = self.eiger.monitor.buffer_size
        return self.__BufferSize_cache

    def set_BufferSize(self, buffer_size):
        self.eiger.monitor.buffer_size = buffer_size

    MonitorState = attribute(label="MonitorState", dtype=DevString,
                        access=AttrWriteType.READ,
                        fget="get_MonitorState",
                        doc="Monitor state, can be normal or overflow.")

    def get_MonitorState(self):
        return self.eiger.monitor.status

    MonitorError = attribute(label="MonitorError", dtype=(str,),
                        max_dim_x=20, # important limit for the string array
                        access=AttrWriteType.READ,
                        fget="get_MonitorError",
                        doc="List of status parameters causing error condition.")

    def get_MonitorError(self):
        return self.eiger.monitor.error


    ### COMMANDS

    def check_path_collision(self):
        """helper method for checking collision. The full path does not contains '_data_0001.h5' etc."""
        full_data_path = os.path.join(self.path_prefix, (self.get_FilenamePattern()).lstrip(os.sep))
        files = [fn for fn in glob.glob(full_data_path + '*') if not os.path.basename(fn).endswith(('jpeg', 'jpg'))]
        if len(files) > 0:
            self.debug_stream("Path collision detected in Data path.")
            return True

        return False

    @command
    def Initialize(self):
        """
        """
        self.debug_stream("In Initialize()")
        self.eiger.initialize()

    @command()
    def Arm(self):
        rstate = self.eiger.get_state()

        if self.check_path_collision():
            raise Exception("Path collision detected")

        if rstate != "ready":
            self.flag_arm = True
            self.eiger.arm()
            self.MustArmFlag.set_value(True)
            # Prepare trigger detection (undocumented)
            if not self.__TriggerMode_cache:
                self.__TriggerMode_cache = self.eiger.trigger_mode
            if "ext" in self.__TriggerMode_cache.lower():
                try:
                    self.eiger.wait(timeout=0.1)
                except Exception as exc:
                    # Ignore timeout error (wait is a blocking command)
                    pass

    @command
    def Trigger(self):
        """ Trigger the detector.
        """
        rstate = self.eiger.get_state()

        if rstate != "ready":
            raise Exception(
                "Detector in %s state, not 'ready',  try the arm command first" % str(rstate))

        try:
            if self.eiger.trigger_mode == "inte":
                self.eiger.trigger(timeout=1.5, input_value=self.__CountTimeInte_cache)
            else:
                self.eiger.trigger(timeout=1.5)
        except:
            pass
    @command
    def Abort(self):
        """ Abort all operations and reset the detector system.
        """
        self.eiger.abort()
        self.dev_status()
    @command
    def Cancel(self):
        """ Stop data acquisition after the current image.
        """
        self.eiger.cancel()
        self.dev_status()
    @command
    def ClearBuffer(self):
        """ Delete all files from buffer
        """
        self.eiger.buffer.clear_buffer()
    @command(dtype_in=str)
    def DeleteFileFromBuffer(self, file):
        """ Delete the file give the argument name from the buffer
        :param argin: Name of the file to delete
        :type argin: PyTango.DevString
        """
        self.eiger.buffer.delete_file(file)

    @command
    def Disarm(self):
        """ Disarm detector
        """
        rstate = self.eiger.get_state()
        if rstate != "idle":
            self.flag_arm = False
            self.eiger.disarm()
    @command(dtype_in=str)
    def DownloadFilesFromBuffer(self, file):
        """ Download the file with the given name or the files matching the given
        pattern (with * for glob expansion).
        :param argin: Filename or pattern
        :type argin: PyTango.DevString
        """
        self.eiger.buffer.download(file, self.__DownloadDirectory_cache)
    @command
    def EnableStream(self):
        """
        """
        self.eiger.stream.stream_mode = 'enabled'
    @command
    def DisableStream(self):
        """
        """
        self.eiger.stream.stream_mode = 'disabled'
    @command
    def FileWriterStart(self):
        """
        """
        self.filewriter_client.start()
    @command
    def FileWriterStop(self):
        """
        """
        self.filewriter_client.stop()
    @command(dtype_out=str)
    def FileWriterStatus(self):
        """
        """
        return self.filewriter_client.status()

    ### COMMANDS from FileWriter
    @command
    def ClearFilewriter(self):
        """ Drops all data (image data and directories) on the DCU.
        """
        self.debug_stream('In ClearFilewriter()')
        self.eiger.filewriter.clear()

    @command
    def InitializeFilewriter(self):
        """ Resets the filewriter to its original state.
        """
        self.debug_stream("In InitializeFilewriter()")
        self.eiger.filewriter.initialize()

    ### COMMANDS from Monitor
    @command
    def ClearMonitor(self):
        """ Drops all buffered images and resets status/dropped to zero.
        """
        self.debug_stream('In ClearMonitor()')
        self.eiger.monitor.clear()

    @command
    def InitializeMonitor(self):
        """ Resets the monitor o its original state.
        """
        self.debug_stream("In InitializeMonitor()")
        self.eiger.monitor.initialize()

    def update_limit_values(self):
        try:
            self.__XPixelSize_cache = self.eiger.x_pixel_size
            self.__YPixelSize_cache = self.eiger.y_pixel_size

            CountTimeMax = self.eiger.get_param_lim("count_time", "max")
            CountTimeMin = self.eiger.get_param_lim("count_time", "min")
            self.CountTime.set_min_value(CountTimeMin)
            self.CountTime.set_max_value(CountTimeMax)

            FrameTimeMax= self.eiger.get_param_lim("frame_time", "max")
            FrameTimeMin= self.eiger.get_param_lim("frame_time", "min")
            self.FrameTime.set_min_value(FrameTimeMin)
            self.FrameTime.set_max_value(FrameTimeMax)

            NbImagesMax = self.eiger.get_param_lim("nimages", "max")
            NbImagesMin = self.eiger.get_param_lim("nimages", "min")
            self.NbImages.set_min_value(int(NbImagesMin))
            self.NbImages.set_max_value(int(NbImagesMax))

            NbTriggersMax = self.eiger.get_param_lim("ntrigger", "max")
            NbTriggersMin = self.eiger.get_param_lim("ntrigger", "min")
            self.NbTriggers.set_min_value(int(NbTriggersMin))
            self.NbTriggers.set_max_value(int(NbTriggersMax))

            PhotonEnergyMax = self.eiger.get_param_lim("photon_energy", "max")
            PhotonEnergyMin = self.eiger.get_param_lim("photon_energy", "min")
            self.PhotonEnergy.set_min_value(PhotonEnergyMin)
            self.PhotonEnergy.set_max_value(PhotonEnergyMax)

            EnergyThresholdMax = self.eiger.get_param_lim("threshold_energy", "max")
            EnergyThresholdMin = self.eiger.get_param_lim("threshold_energy", "min")
            self.EnergyThreshold.set_min_value(EnergyThresholdMin)
            self.EnergyThreshold.set_max_value(EnergyThresholdMax)

            XPixelSize = self.eiger.x_pixel_size
            YPixelSize = self.eiger.y_pixel_size
            XPixelsDetector = self.eiger.x_pixels_detector
            YPixelsDetector = self.eiger.y_pixels_detector

        except Exception as ex:
            print(ex)
            print("Error reading parameter limit from detector")

    def init_device(self):
        self.set_state(tango.DevState.INIT)
        self.get_device_properties() # necessary before use the properties
        try:
            self.eiger = EigerDetector(self.host, self.data_host, self.port, self.api_version, self.data_port)
            self.filewriter_client = FileWriterClient(self.filewriter_host, self.filewriter_port)
            self.update_limit_values()
            self.set_state(tango.DevState.ON)

        except Exception as e:
            self.set_state(tango.DevState.FAULT)
            self.set_status("Device failed in init setting power save mode: " + str(e))

    def dev_state(self):
        """ This command gets the device state (stored in its device_state data member) and returns it to the caller.
        :return: Device state
        :rtype: tango.CmdArgType.DevState
        """
        self.debug_stream("In dev_state()")
        argout = tango.DevState.UNKNOWN

        rstate = self.eiger.get_state()
        self.debug_stream("In dev_state() state: %s, flag: %s",
                          rstate, self.flag_arm)

        if self.flag_arm:
            if rstate == "configure" or rstate == "idle":
                self.debug_stream("In dev_state()... flag gonna reset")
                self.flag_arm = False
        if rstate == "error":
            self.set_state(tango.DevState.FAULT)
        elif (rstate == "na"):
            self.set_state(tango.DevState.OFF)
        elif self.check_path_collision():
            self.set_state(tango.DevState.ALARM)
        elif (rstate != "idle" and rstate != "ready"):
            self.set_state(tango.DevState.MOVING)
        elif rstate == 'acquire':
            self.set_state(tango.DevState.MOVING)
        else:
            self.set_state(tango.DevState.ON)

        argout = self.get_state()
        print (argout)

        return argout

    def dev_status(self):
        """ This command gets the device status (stored in its device_status data member) and returns it to the caller.
        :return: Device status
        :rtype: tango.ConstDevString
        """
        self.debug_stream("In dev_status()")
        argout = ""
        msg = ""

        rstate = self.eiger.get_state()

        if rstate == "na":
            rstate = rstate + "\nThe detector was rebooted and \n has to be initialized\n"
        argout = str(rstate + "\n")

        try:
            if self.check_path_collision():
                msg += '\nWARNING: current filename configuration will lead to a data path collision for the next data collection.\n'
                msg += 'If a data collection is in progress you can ignore this message.\n\n'
        except Exception as ex:
            print(ex)

        if self.filewriter_client.status().startswith("Running"):
            msg += 'Cluster based data backup is running.\n'
        else:
            msg += 'Cluster based data backup is NOT running.\n'

        argout += msg

        stream_msg = 'Stream interface is ' + self.eiger.stream.stream_state + '\n'
        argout += stream_msg
        self.set_status(argout)
        return argout

def main():
    server_run((Eiger,))

if __name__ == "__main__":
    main()
