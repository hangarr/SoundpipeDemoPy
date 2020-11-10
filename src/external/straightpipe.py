#!/usr/bin/env python3

# fix module search path for this project layout
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from ctypes import *

import getopt

from modules.soundpipe import *


#====================================================
# Python persistence dictionary
#====================================================

# Applications using any of the Python versions of soundpipe-style
# modules must declare this dictionary for persisting 
# the Python classes corresonding to the underlying ctypes module 
# data structures IN EACH PYTHON ODULE declaring soundpipe-style
# modules.  ("Globals" like this are only global to the module.)

o1p_ud_py = {}

#====================================================
# Modules
#====================================================

#----------------------------------------------------
# dummy module
#----------------------------------------------------

#typedef struct {
#    SPFLOAT prm;
#} o1p_dmod;

class o1p_dmod(Structure):
    _fields_ = [
        ("prm", SPFLOAT)
        ]

#int o1p_dmod_create(o1p_dmod **p) {
#    *p = malloc(sizeof(o1p_dmod));
#
#    return SP_OK;
#}

# NOTE: p passed in byref() rather than as pointer.

def o1p_dmod_create(p):
    pp = cast(p, POINTER(POINTER(o1p_dmod)))

    # the ctypes part
    cs = o1p_dmod()
    pp[0] = POINTER(o1p_dmod)(cs)

    # the Python part - persist
    ids = byref(cs)
    cskey = "dmod_" + str(ids)
    o1p_ud_py[cskey] = cs

    return(SP_OK)


#int o1p_dmod_destroy(o1p_dmod **p) {
#    free(*p);
#
#    return SP_OK;
#}

# NOTE: p passed in byref() rather than as pointer.

def o1p_dmod_destroy(p):
    pp = cast(p, POINTER(POINTER(o1p_dmod)))

    # the python part - unpersist
    ids = byref(pp[0][0])
    cskey = "dmod_" + str(ids)
    del o1p_ud_py[cskey]

    # the ctypes part
    pp[0] = POINTER(o1p_dmod)()    

    return(SP_OK)

#int o1p_dmod_init(sp_data *sp, o1p_dmod *p) {
#    p->prm = 0.0;
#
#    return SP_OK;
#}

def o1p_dmod_init(sp, p):
    p[0].prm = 0.0 

    return(SP_OK)

#int o1p_dmod_compute(sp_data *sp, o1p_dmod *p, SPFLOAT *in, SPFLOAT *out) {
#    *out = *in;
# 
#    return SP_OK;
#}

# NOTE: inr and outr passed in byref() rather than as pointers.

def o1p_dmod_compute(sp, p, inr, outr):
     inp = cast(inr, POINTER(SPFLOAT))
     outp = cast(outr, POINTER(SPFLOAT))
     
     outp[0] = inp[0]

     return(SP_OK)


#====================================================
# dummy application
#====================================================

# Notes:
# 1) an ftable is a canned waveform table
# 2) not sure what the sp_ftbl members are
# 3) not sure sp->len is but appears to be total samples

class UserData(Structure):
    _fields_ = [
        ("wavin", POINTER(sp_wavin)),
        ("wavout", POINTER(sp_wavout)),
        ("dmod", POINTER(o1p_dmod))
#        ("ft", POINTER(sp_ftbl))
    ]

def callback(sp, udata, spin):
    ud = cast(udata, POINTER(UserData))
    spinp = cast(spin, POINTER(SPFLOAT))
    outv = SPFLOAT(0)

    inv = SPFLOAT(spinp[0])

    o1p_dmod_compute(sp, ud[0].dmod, byref(inv), byref(outv))

    sp[0].out[0] = outv


#====================================================
# example main
#====================================================
def usage():
    print("usage: %s [-ds] [-o name] [name ...]" % sys.argv[0])

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dso:?", 
                                   ["[-d]", "[-o name]", "[name ...]"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    debug = False
    oflag = False
    iflag = False
    sflag = False
    err = False
    for o, a in opts:
        if o == "-d":
            debug = True
        elif o == "-o":
            oflag = True
            ofname = a
        elif o == "-s":
            sflag = True
        elif o == "?":
            err = True

    if err:
        usage()
        sys.exit()

    # Check for input file (in args)
    if len(args) > 0:
        ifname = args[0]
        iflag = True
    if len(args) > 1:
        print("ignored additional arguments", file=sys.stderr)
        usage()

    # Re-assign stdin and stdout if specified (ignored in this case)

    if iflag and sflag:
        sys.stdin = open(ifname, 'r')

    if oflag and sflag:
        sys.stdout = open(ofname, 'w')

    # Verify file names supplied

    if not iflag and not sflag:
        print("missing required input file", file=sys.stderr)
        usage()
        sys.exit(1)

    if not oflag and not sflag:
        print("missing required output file", file=sys.stderr)
        usage()
        sys.exit(1)

    # Display debug info
    
    if debug:
        if iflag:
            print("ifname: \"%s\"" % ifname, file=sys.stderr)
        else:
            print("ifname: stdin", file=sys.stderr)

        if oflag:
            print("ofname: \"%s\"" % ofname, file=sys.stderr)
        else:
            print("ofname: stdout", file = sys.stderr)

    #-------------------------------------------------------------

    # Minimum data storage required

    ud = UserData()
    sp = POINTER(sp_data)()


    # Create empty soundpipe

    sp_create(byref(sp))


    # Add I/O to soundpipe

    sp_wavin_create(byref(ud.wavin))

    c_ifname = ifname.encode('utf-8')
    sp_wavin_init(sp, ud.wavin, c_ifname)

    sp_wavout_create(byref(ud.wavout))

    c_ofname = ofname.encode('utf-8')
    sp_wavout_init(sp, ud.wavout, c_ofname)


    # build and configure soundpipe

    o1p_dmod_create(byref(ud.dmod))
    o1p_dmod_init(sp, ud.dmod)


    # adjust soundpipe length based on file to have best control

    sp[0].len = ud.wavin[0].wav.totalSampleCount


    # data buffer just to structure design

    din = SPFLOAT(0.0)
    dout = SPFLOAT(0.0)

    # have to create actual storage here
    sp[0].out = POINTER(SPFLOAT)(pointer(SPFLOAT()))
    sp[0].nchan = c_int(1)

    # the processing

    while sp[0].len > 0:
        sp_wavin_compute(sp, ud.wavin, POINTER(SPFLOAT)(), byref(din))
        callback(sp, byref(ud), byref(din))
        sp_wavout_compute(sp, ud.wavout, sp[0].out, byref(dout))
        sp[0].len -= 1
        sp[0].pos += 1

    sp[0].out = POINTER(SPFLOAT)()


    # Dismantle soundpipe
 
    o1p_dmod_destroy(byref(ud.dmod))


    # Shutdown I/O

    sp_wavout_destroy(byref(ud.wavout))
    sp_wavin_destroy(byref(ud.wavin))


    # Clean up on completion

    sp_destroy(byref(sp))

    return 0


if __name__ == "__main__":
    ret = main()

    sys.exit(ret)
