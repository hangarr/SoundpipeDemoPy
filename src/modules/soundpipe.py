#!/usr/bin/env python3

# python3 wrapper around libsoundpipe.so shared object

import os
from ctypes import *

from modules.dr_wav import *

# for now, assume libsound.so found in "soundpipe" folder next to this project folder

libpath = "../../../soundpipe"
libname = os.path.abspath(os.path.join(libpath, "libsoundpipe.so"))

#print('%s' % libname)

libsoundpipe = CDLL(libname)

# function to wrap a C function in a Python function

def wrap_function(lib, funcname, restype, argtypes):
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func

SP_BUFSIZE = 4096
SPFLOAT = c_float
SP_OK = 1
SP_NOT_OK = 0
SP_RANDMAX = 2147483648

# Add functions from soundpipe as needed

# -------------------
# base
# -------------------

# typedef struct sp_data {
#     SPFLOAT *out;
#     int sr;
#     int nchan;
#     unsigned long len;
#     unsigned long pos;
#     char filename[200];
#     uint32_t rand;
# } sp_data;

CharArr200 = c_char * 200

class sp_data(Structure):
    _fields_ = [
        ("out", POINTER(SPFLOAT)),
        ("sr", c_int),
        ("nchan", c_int),
        ("len", c_ulong),
        ("pos", c_ulong),
        ("filename", CharArr200),
        ("rand", c_uint32)
        ]

# int sp_create(sp_data **spp);
# int sp_destroy(sp_data **spp);

sp_create = wrap_function(libsoundpipe, 'sp_create', c_int, [POINTER(POINTER(sp_data))]);
sp_destroy = wrap_function(libsoundpipe, 'sp_destroy', c_int, [POINTER(POINTER(sp_data))]);

# NOTE: The wavin and wavout modules use the drwav package.  The structures include members
# for the drwav structure.  See dr_wav.py for more info.

# -------------------
# wavein
# -------------------
# NOTE: This includes an instance of drwav in sp_wavin

# #define WAVIN_BUFSIZE 1024
# typedef struct {
#     SPFLOAT buf[WAVIN_BUFSIZE];
#     int count;
#     drwav wav;
#     unsigned long pos;
#     unsigned long buf_start;
#     unsigned long buf_end;
# } sp_wavin;

WAVIN_BUFSIZE = 1024
SPFLOATArrWAVIN_BUFSIZE = SPFLOAT * WAVIN_BUFSIZE

class sp_wavin(Structure):
    _fields_ = [
        ("buf", SPFLOATArrWAVIN_BUFSIZE),
        ("count", c_int),
        ("wav", Drwav),
        ("pos", c_ulong),
        ("buf_start", c_ulong),
        ("buf_end", c_ulong)
        ]

# int sp_wavin_create(sp_wavin **p);
# int sp_wavin_destroy(sp_wavin **p);
# int sp_wavin_init(sp_data *sp, sp_wavin *p, const char *filename);
# int sp_wavin_compute(sp_data *sp, sp_wavin *p, SPFLOAT *in, SPFLOAT *out);

sp_wavin_create = wrap_function(libsoundpipe, 'sp_wavin_create', c_int, 
                                    [POINTER(POINTER(sp_wavin))])
sp_wavin_destroy = wrap_function(libsoundpipe, 'sp_wavin_destroy', c_int,
                                    [POINTER(POINTER(sp_wavin))])
sp_wavin_init = wrap_function(libsoundpipe, 'sp_wavin_init', c_int,
                                    [POINTER(sp_data), POINTER(sp_wavin), POINTER(c_char)])
sp_wavin_compute = wrap_function(libsoundpipe, 'sp_wavin_compute', c_int,
                                    [POINTER(sp_data), POINTER(sp_wavin), 
                                     POINTER(SPFLOAT), POINTER(SPFLOAT)])

# -------------------
# wavout
# -------------------
# NOTE: This includes a pointer to drwav in sp_wavout

# sp_wavout is found in wavout.c

# #define WAVOUT_BUFSIZE 1024
# struct sp_wavout {
#     drwav *wav;
#     drwav_data_format format;
#     SPFLOAT buf[WAVOUT_BUFSIZE];
#     int count;
# };

WAVOUT_BUFSIZE = 1024
SPFLOATArrWAVOUT_BUFSIZE = SPFLOAT * WAVOUT_BUFSIZE

class sp_wavout(Structure):
    _fields_ = [
        ("wav", POINTER(Drwav)),
        ("format", Drwav_data_format),
        ("buf", SPFLOATArrWAVOUT_BUFSIZE),
        ("count", c_int)
        ]

# int sp_wavout_create(sp_wavout **p);
# int sp_wavout_destroy(sp_wavout **p);
# int sp_wavout_init(sp_data *sp, sp_wavout *p, const char *filename);
# int sp_wavout_compute(sp_data *sp, sp_wavout *p, SPFLOAT *in, SPFLOAT *out);

sp_wavout_create = wrap_function(libsoundpipe, 'sp_wavout_create', c_int, 
                                     [POINTER(POINTER(sp_wavout))])
sp_wavout_destroy = wrap_function(libsoundpipe, 'sp_wavout_destroy', c_int,
                                     [POINTER(POINTER(sp_wavout))])
sp_wavout_init = wrap_function(libsoundpipe, 'sp_wavout_init', c_int,
                                     [POINTER(sp_data), POINTER(sp_wavout), POINTER(c_char)])
sp_wavout_compute = wrap_function(libsoundpipe, 'sp_wavout_compute', c_int,
                                     [POINTER(sp_data), POINTER(sp_wavout), 
                                      POINTER(SPFLOAT), POINTER(SPFLOAT)])

