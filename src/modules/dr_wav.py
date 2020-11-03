#!/usr/bin/env python3

# python3 wrapper to declare complicated drwav type

import os
from ctypes import *

# NOTE: these are only used so soundpipe called from Python will
# create sp_wavin and sp_wavout structures of the right size
# This includes only partially declared function pointers and enum
# types.  These may have to be more fully elaborated if dr_wav is
# updated or wavin/wavout are updated in soundpipe.

# basic types

drwav_int8 = c_int8
drwav_uint8 = c_uint8
drwav_int16 = c_int16
drwav_uint16 = c_uint16
drwav_int32 = c_int32
drwav_uint32 = c_uint32
drwav_int64 = c_int64
drwav_uint64 = c_uint64
drwav_bool8 = drwav_uint8
drwav_bool32 = drwav_uint32

# pointer to function defaulted to pointer to void since this won't be called from Python
# typedef size_t (* drwav_read_proc)(void* pUserData, void* pBufferOut, size_t bytesToRead)

drwav_read_proc = c_void_p

# pointer to function defaulted to pointer to void since this won't be called from Python
# typedef size_t (* drwav_write_proc)(void* pUserData, const void* pData, size_t bytesToWrite)

drwav_write_proc = c_void_p

# pointer to function defaulted to pointer to void since this won't be called from Python
# typedef drwav_bool32 (* drwav_seek_proc)(void* pUserData, int offset, drwav_seek_origin origin);

drwav_seek_proc = c_void_p

# this creates dummy space in the structure declaration since we won't be using it

drwav_enum = c_int

# typedef enum
# {
#     drwav_seek_origin_start,
#     drwav_seek_origin_current
# } drwav_seek_origin;

drwav_seek_origin = drwav_enum


# typedef enum
# {
#     drwav_container_riff,
#     drwav_container_w64
# } drwav_container;

drwav_container = drwav_enum


# typedef struct
# {
#     const drwav_uint8* data;
#     size_t dataSize;
#     size_t currentReadPos;
# } drwav__memory_stream;

class Drwav__memory_stream(Structure):
    _fields_ = [
        ("data", POINTER(drwav_uint8)),
        ("dataSize", c_size_t),
        ("currentReadPos", c_size_t)
        ]


# typedef struct
# {
#     void** ppData;
#     size_t* pDataSize;
#     size_t dataSize;
#     size_t dataCapacity;
#     size_t currentWritePos;
# } drwav__memory_stream_write;

class Drwav__memory_stream_write(Structure):
    _fields_ = [
        ("ppData", POINTER(c_void_p)),
        ("pDataSize", c_size_t),
        ("dataSize", c_size_t),
        ("dataCapacity", c_size_t),
        ("currentWritePos", c_size_t)
        ]


# typedef struct
# {
#     drwav_container container;  // RIFF, W64.
#     drwav_uint32 format;        // DR_WAVE_FORMAT_*
#     drwav_uint32 channels;
#     drwav_uint32 sampleRate;
#     drwav_uint32 bitsPerSample;
# } drwav_data_format;

class Drwav_data_format(Structure):
    _fields_ = [
        ("container", drwav_container),
        ("format", drwav_uint32),
        ("channels", drwav_uint32),
        ("sampleRate", drwav_uint32),
        ("bitsPerSample", drwav_uint32)
        ]


# typedef struct
# {
#     // The format tag exactly as specified in the wave file's "fmt" chunk. This can be used by applications
#     // that require support for data formats not natively supported by dr_wav.
#     drwav_uint16 formatTag;
#
#     // The number of channels making up the audio data. When this is set to 1 it is mono, 2 is stereo, etc.
#     drwav_uint16 channels;
#
#     // The sample rate. Usually set to something like 44100.
#     drwav_uint32 sampleRate;
#
#     // Average bytes per second. You probably don't need this, but it's left here for informational purposes.
#     drwav_uint32 avgBytesPerSec;
#
#     // Block align. This is equal to the number of channels * bytes per sample.
#     drwav_uint16 blockAlign;
#
#     // Bit's per sample.
#     drwav_uint16 bitsPerSample;
#
#     // The size of the extended data. Only used internally for validation, but left here for informational purposes.
#     drwav_uint16 extendedSize;
#
#     // The number of valid bits per sample. When <formatTag> is equal to WAVE_FORMAT_EXTENSIBLE, <bitsPerSample>
#     // is always rounded up to the nearest multiple of 8. This variable contains information about exactly how
#     // many bits a valid per sample. Mainly used for informational purposes.
#     drwav_uint16 validBitsPerSample;
# 
#     // The channel mask. Not used at the moment.
#     drwav_uint32 channelMask;
#
#     // The sub-format, exactly as specified by the wave file.
#     drwav_uint8 subFormat[16];
# } drwav_fmt;

Drwav_uint8Arr16 = drwav_uint8 * 16

class Drwav_fmt(Structure):
    _fields_ = [
        ("formatTag", drwav_uint16),
        ("channels", drwav_uint16),
        ("sampleRate", drwav_uint32),
        ("avgBytesPerSec", drwav_uint32),
        ("blockAlign", drwav_uint16),
        ("bitsPerSample", drwav_uint16),
        ("extendedSize", drwav_uint16),
        ("validBitsPerSample", drwav_uint16),
        ("channelMask", drwav_uint32),
        ("subFormat", Drwav_uint8Arr16)
    ]


# typedef struct
# {
#     // A pointer to the function to call when more data is needed.
#     drwav_read_proc onRead;
#
#     // A pointer to the function to call when data needs to be written. Only used when the drwav object is opened in write mode.
#     drwav_write_proc onWrite;
#
#     // A pointer to the function to call when the wav file needs to be seeked.
#     drwav_seek_proc onSeek;
#
#     // The user data to pass to callbacks.
#     void* pUserData;
# 
#     // Whether or not the WAV file is formatted as a standard RIFF file or W64.
#     drwav_container container;
#
#     // Structure containing format information exactly as specified by the wav file.
#     drwav_fmt fmt;
#
#     // The sample rate. Will be set to something like 44100.
#     drwav_uint32 sampleRate;
# 
#     // The number of channels. This will be set to 1 for monaural streams, 2 for stereo, etc.
#     drwav_uint16 channels;
# 
#     // The bits per sample. Will be set to somthing like 16, 24, etc.
#     drwav_uint16 bitsPerSample;
#
#     // The number of bytes per sample.
#     drwav_uint16 bytesPerSample;
#
#     // Equal to fmt.formatTag, or the value specified by fmt.subFormat if fmt.formatTag is equal to 65534 (WAVE_FORMAT_EXTENSIBLE).
#     drwav_uint16 translatedFormatTag;
#
#     // The total number of samples making up the audio data. Use <totalSampleCount> * <bytesPerSample> to calculate
#     // the required size of a buffer to hold the entire audio data.
#     drwav_uint64 totalSampleCount;
#
#     // The size in bytes of the data chunk.
#     drwav_uint64 dataChunkDataSize;
#    
#     // The position in the stream of the first byte of the data chunk. This is used for seeking.
#     drwav_uint64 dataChunkDataPos;
#
#     // The number of bytes remaining in the data chunk.
#     drwav_uint64 bytesRemaining;
#
#     // A hack to avoid a DRWAV_MALLOC() when opening a decoder with drwav_open_memory().
#     drwav__memory_stream memoryStream;
#     drwav__memory_stream_write memoryStreamWrite;
#
#     // Generic data for compressed formats. This data is shared across all block-compressed formats.
#     struct
#     {
#         drwav_uint64 iCurrentSample;    // The index of the next sample that will be read by
#                                         // drwav_read_*(). 
#                                         // This is used with "totalSampleCount" to ensure we
#                                         // don't read excess samples at the end of the last block.
#     } compressed;
#    
#     // Microsoft ADPCM specific data.
#     struct
#     {
#         drwav_uint32 bytesRemainingInBlock;
#         drwav_uint16 predictor[2];
#         drwav_int32  delta[2];
#         drwav_int32  cachedSamples[4];  // Samples are stored in this cache during decoding.
#         drwav_uint32 cachedSampleCount;
#         drwav_int32  prevSamples[2][2]; // The previous 2 samples for each channel (2 channels at most).
#     } msadpcm;
#
#     // IMA ADPCM specific data.
#     struct
#     {
#         drwav_uint32 bytesRemainingInBlock;
#         drwav_int32  predictor[2];
#         drwav_int32  stepIndex[2];
#         drwav_int32  cachedSamples[16]; // Samples are stored in this cache during decoding.
#         drwav_uint32 cachedSampleCount;
#     } ima;
# } drwav;

class Compressed(Structure):
    _fields_ = [
        ("iCurrentSample", drwav_uint64)
        ]

Drwav_uint16Arr2 = drwav_uint16 * 2
Drwav_int32Arr2 = drwav_int32 * 2
Drwav_int32Arr4 = drwav_int32 * 4
Drwav_int32Arr2x2 = drwav_int32 * 2 * 2

class Msadpcm(Structure):
    _fields_ = [
        ("bytesRemainingInBlock", drwav_uint32),
        ("predictor", Drwav_uint16Arr2),
        ("delta", Drwav_int32Arr2),
        ("cachedSamples", Drwav_int32Arr4),
        ("cachedSampleCount", drwav_uint32),
        ("prevSamples", Drwav_int32Arr2x2)
        ]

Drwav_int32Arr16 = drwav_int32 * 16

class Ima(Structure):
    _fields_ = [
        ("bytesRemainingInBlock", drwav_uint32),
        ("predictor", Drwav_int32Arr2),
        ("stepIndex", Drwav_int32Arr2),
        ("cachedSamples", Drwav_int32Arr16),
        ("cachedSampleCount", drwav_uint32)
        ]

class Drwav(Structure):
    _fields_ = [
        ("onRead", drwav_read_proc),
        ("onWrite", drwav_write_proc),
        ("onSeek", drwav_seek_proc),
        ("pUserData", c_void_p),
        ("container", drwav_container),
        ("fmt", Drwav_fmt),
        ("sampleRate", drwav_uint32),
        ("channels", drwav_uint16),
        ("bitsPerSample", drwav_uint16),
        ("bytesPerSample", drwav_uint16),
        ("translatedFormatTag", drwav_uint16),
        ("totalSampleCount", drwav_uint64),
        ("dataChunkDataSize", drwav_uint64),
        ("dataChunkDataPos", drwav_uint64),
        ("bytesRemaining", drwav_uint64),
        ("memoryStream", Drwav__memory_stream),
        ("memoryStreamWrite", Drwav__memory_stream_write),
        ("compressed", Compressed),
        ("msadpcm", Msadpcm),
        ("ima", Ima)
        ]

testdrwav = Drwav()
