#!/usr/bin/env python3

# python3 wrapper around libsoundpipe.so shared object

import os
from ctypes import *

from modules.dr_wav import *

# for now, assume libsoundpipe.so found in "soundpipe" folder next to this project folder

sp_libpath = "../../../soundpipe"
sp_libname = os.path.abspath(os.path.join(sp_libpath, "libsoundpipe.so"))

#print('%s' % sp_libname)

libsoundpipe = CDLL(sp_libname)

# function to wrap a C function in a Python function

def sp_wrap_function(lib, funcname, restype, argtypes):
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

SP_CharArr200 = c_char * 200

class sp_data(Structure):
    _fields_ = [
        ("out", POINTER(SPFLOAT)),
        ("sr", c_int),
        ("nchan", c_int),
        ("len", c_ulong),
        ("pos", c_ulong),
        ("filename", SP_CharArr200),
        ("rand", c_uint32)
        ]

# int sp_create(sp_data **spp);
# int sp_destroy(sp_data **spp);

sp_create = sp_wrap_function(libsoundpipe, 'sp_create', c_int,
                             [POINTER(POINTER(sp_data))]);
sp_destroy = sp_wrap_function(libsoundpipe, 'sp_destroy', c_int,
                              [POINTER(POINTER(sp_data))]);

# NOTE: The wavin and wavout modules use the drwav package.  The structures include
# members for the drwav structure.  See dr_wav.py for more info.

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

SP_WAVIN_BUFSIZE = 1024
SP_SPFLOATArrWAVIN_BUFSIZE = SPFLOAT * SP_WAVIN_BUFSIZE

class sp_wavin(Structure):
    _fields_ = [
        ("buf", SP_SPFLOATArrWAVIN_BUFSIZE),
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

sp_wavin_create = sp_wrap_function(libsoundpipe, 'sp_wavin_create', c_int, 
                                   [POINTER(POINTER(sp_wavin))])
sp_wavin_destroy = sp_wrap_function(libsoundpipe, 'sp_wavin_destroy', c_int,
                                    [POINTER(POINTER(sp_wavin))])
sp_wavin_init = sp_wrap_function(libsoundpipe, 'sp_wavin_init', c_int,
                                 [POINTER(sp_data), POINTER(sp_wavin),
                                  POINTER(c_char)])
sp_wavin_compute = sp_wrap_function(libsoundpipe, 'sp_wavin_compute', c_int,
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

SP_WAVOUT_BUFSIZE = 1024
SP_SPFLOATArrWAVOUT_BUFSIZE = SPFLOAT * SP_WAVOUT_BUFSIZE

class sp_wavout(Structure):
    _fields_ = [
        ("wav", POINTER(Drwav)),
        ("format", Drwav_data_format),
        ("buf", SP_SPFLOATArrWAVOUT_BUFSIZE),
        ("count", c_int)
        ]

# int sp_wavout_create(sp_wavout **p);
# int sp_wavout_destroy(sp_wavout **p);
# int sp_wavout_init(sp_data *sp, sp_wavout *p, const char *filename);
# int sp_wavout_compute(sp_data *sp, sp_wavout *p, SPFLOAT *in, SPFLOAT *out);

sp_wavout_create = sp_wrap_function(libsoundpipe, 'sp_wavout_create', c_int, 
                                    [POINTER(POINTER(sp_wavout))])
sp_wavout_destroy = sp_wrap_function(libsoundpipe, 'sp_wavout_destroy', c_int,
                                     [POINTER(POINTER(sp_wavout))])
sp_wavout_init = sp_wrap_function(libsoundpipe, 'sp_wavout_init', c_int,
                                  [POINTER(sp_data), POINTER(sp_wavout),
                                   POINTER(c_char)])
sp_wavout_compute = sp_wrap_function(libsoundpipe, 'sp_wavout_compute', c_int,
                                     [POINTER(sp_data), POINTER(sp_wavout), 
                                      POINTER(SPFLOAT), POINTER(SPFLOAT)])


# -------------------
# butbp
# -------------------

# typedef struct {
#     SPFLOAT sr, freq, bw, istor;
#     SPFLOAT lkf, lkb;
#     SPFLOAT a[8];
#     SPFLOAT pidsr, tpidsr;
# } sp_butbp;

SP_SPFLOATArr8 = SPFLOAT * 8

class sp_butbp(Structure):
    _fields_ = [
        ("sr", SPFLOAT),
        ("freq", SPFLOAT),
        ("bw", SPFLOAT),
        ("istor", SPFLOAT),
        ("lkf", SPFLOAT),
        ("lkb", SPFLOAT),
        ("a", SP_SPFLOATArr8),
        ("pidsr", SPFLOAT),
        ("tpidsr", SPFLOAT)
        ]

# int sp_butbp_create(sp_butbp **p);
# int sp_butbp_destroy(sp_butbp **p);
# int sp_butbp_init(sp_data *sp, sp_butbp *p);
# int sp_butbp_compute(sp_data *sp, sp_butbp *p, SPFLOAT *in, SPFLOAT *out);

sp_butbp_create = sp_wrap_function(libsoundpipe, 'sp_butbp_create', c_int, 
                                   [POINTER(POINTER(sp_butbp))])
sp_butbp_destroy = sp_wrap_function(libsoundpipe, 'sp_butbp_destroy', c_int,
                                    [POINTER(POINTER(sp_butbp))])
sp_butbp_init = sp_wrap_function(libsoundpipe, 'sp_butbp_init', c_int,
                                 [POINTER(sp_data), POINTER(sp_butbp)])
sp_butbp_compute = sp_wrap_function(libsoundpipe, 'sp_butbp_compute', c_int,
                                    [POINTER(sp_data), POINTER(sp_butbp), 
                                     POINTER(SPFLOAT), POINTER(SPFLOAT)])


# -------------------
# butbr
# -------------------

# typedef struct {
#     SPFLOAT sr, freq, bw, istor;
#     SPFLOAT lkf, lkb;
#     SPFLOAT a[8];
#     SPFLOAT pidsr, tpidsr;
# } sp_butbr;

class sp_butbr(Structure):
    _fields_ = [
        ("sr", SPFLOAT),
        ("freq", SPFLOAT),
        ("bw", SPFLOAT),
        ("istor", SPFLOAT),
        ("lkf", SPFLOAT),
        ("lkb", SPFLOAT),
        ("a", SP_SPFLOATArr8),
        ("pidsr", SPFLOAT),
        ("tpidsr", SPFLOAT)
        ]

# int sp_butbr_create(sp_butbr **p);
# int sp_butbr_destroy(sp_butbr **p);
# int sp_butbr_init(sp_data *sp, sp_butbr *p);
# int sp_butbr_compute(sp_data *sp, sp_butbr *p, SPFLOAT *in, SPFLOAT *out);

sp_butbr_create = sp_wrap_function(libsoundpipe, 'sp_butbr_create', c_int, 
                                   [POINTER(POINTER(sp_butbr))])
sp_butbr_destroy = sp_wrap_function(libsoundpipe, 'sp_butbr_destroy', c_int,
                                    [POINTER(POINTER(sp_butbr))])
sp_butbr_init = sp_wrap_function(libsoundpipe, 'sp_butbr_init', c_int,
                                 [POINTER(sp_data), POINTER(sp_butbr)])
sp_butbr_compute = sp_wrap_function(libsoundpipe, 'sp_butbr_compute', c_int,
                                    [POINTER(sp_data), POINTER(sp_butbr), 
                                     POINTER(SPFLOAT), POINTER(SPFLOAT)])


# -------------------
# buthp
# -------------------

# typedef struct  {
#     SPFLOAT sr, freq, istor;
#     SPFLOAT lkf;
#     SPFLOAT a[8];
#     SPFLOAT pidsr;
# } sp_buthp;

class sp_buthp(Structure):
    _fields_ = [
        ("sr", SPFLOAT),
        ("freq", SPFLOAT),
        ("istor", SPFLOAT),
        ("lkf", SPFLOAT),
        ("a", SP_SPFLOATArr8),
        ("pidsr", SPFLOAT)
        ]


# int sp_buthp_create(sp_buthp **p);
# int sp_buthp_destroy(sp_buthp **p);
# int sp_buthp_init(sp_data *sp, sp_buthp *p);
# int sp_buthp_compute(sp_data *sp, sp_buthp *p, SPFLOAT *in, SPFLOAT *out);

sp_buthp_create = sp_wrap_function(libsoundpipe, 'sp_buthp_create', c_int, 
                                   [POINTER(POINTER(sp_buthp))])
sp_buthp_destroy = sp_wrap_function(libsoundpipe, 'sp_buthp_destroy', c_int,
                                    [POINTER(POINTER(sp_buthp))])
sp_buthp_init = sp_wrap_function(libsoundpipe, 'sp_buthp_init', c_int,
                                 [POINTER(sp_data), POINTER(sp_buthp)])
sp_buthp_compute = sp_wrap_function(libsoundpipe, 'sp_buthp_compute', c_int,
                                    [POINTER(sp_data), POINTER(sp_buthp), 
                                     POINTER(SPFLOAT), POINTER(SPFLOAT)])


# -------------------
# butlp
# -------------------

# typedef struct  {
#     SPFLOAT sr, freq, istor;
#     SPFLOAT lkf;
#     SPFLOAT a[8];
#     SPFLOAT pidsr;
# } sp_butlp;

class sp_butlp(Structure):
    _fields_ = [
        ("sr", SPFLOAT),
        ("freq", SPFLOAT),
        ("istor", SPFLOAT),
        ("lkf", SPFLOAT),
        ("a", SP_SPFLOATArr8),
        ("pidsr", SPFLOAT)
        ]

# int sp_butlp_create(sp_butlp **p);
# int sp_butlp_destroy(sp_butlp **p);
# int sp_butlp_init(sp_data *sp, sp_butlp *p);
# int sp_butlp_compute(sp_data *sp, sp_butlp *p, SPFLOAT *in, SPFLOAT *out);

sp_butlp_create = sp_wrap_function(libsoundpipe, 'sp_butlp_create', c_int, 
                                   [POINTER(POINTER(sp_butlp))])
sp_butlp_destroy = sp_wrap_function(libsoundpipe, 'sp_butlp_destroy', c_int,
                                    [POINTER(POINTER(sp_butlp))])
sp_butlp_init = sp_wrap_function(libsoundpipe, 'sp_butlp_init', c_int,
                                 [POINTER(sp_data), POINTER(sp_butlp)])
sp_butlp_compute = sp_wrap_function(libsoundpipe, 'sp_butlp_compute', c_int,
                                    [POINTER(sp_data), POINTER(sp_butlp), 
                                     POINTER(SPFLOAT), POINTER(SPFLOAT)])


# -------------------
# hilbert
# -------------------

# typedef struct {
#     SPFLOAT xnm1[12], ynm1[12], coef[12];
# } sp_hilbert;

SP_SPFLOATArr12 = SPFLOAT * 12

class sp_hilbert(Structure):
    _fields_ = [
        ("xnm1", SP_SPFLOATArr12),
        ("ynm1", SP_SPFLOATArr12),
        ("coef", SP_SPFLOATArr12)
        ]

# int sp_hilbert_create(sp_hilbert **p);
# int sp_hilbert_destroy(sp_hilbert **p);
# int sp_hilbert_init(sp_data *sp, sp_hilbert *p);
# int sp_hilbert_compute(sp_data *sp, sp_hilbert *p, SPFLOAT *in, SPFLOAT *out1,
#                        SPFLOAT *out2);

sp_hilbert_create = sp_wrap_function(libsoundpipe, 'sp_hilbert_create', c_int, 
                                     [POINTER(POINTER(sp_hilbert))])
sp_hilbert_destroy = sp_wrap_function(libsoundpipe, 'sp_hilbert_destroy', c_int,
                                      [POINTER(POINTER(sp_hilbert))])
sp_hilbert_init = sp_wrap_function(libsoundpipe, 'sp_hilbert_init', c_int,
                                   [POINTER(sp_data), POINTER(sp_hilbert)])
sp_hilbert_compute = sp_wrap_function(libsoundpipe, 'sp_hilbert_compute', c_int,
                                      [POINTER(sp_data), POINTER(sp_hilbert), 
                                       POINTER(SPFLOAT), POINTER(SPFLOAT),
                                       POINTER(SPFLOAT)])
