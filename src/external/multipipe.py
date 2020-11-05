#!/usr/bin/env python3

# fix module search path for this project layout
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from ctypes import *

import getopt

from modules.soundpipe import *

#====================================================
# some utility functions
#----------------------------------------------------
#---------------------
# splitpath
#---------------------
# function to split a filepath into parts
#
# Pythonic because C version had to avoid creating heap objects
# Everything is an object in Python!

def splitpath(fname):
    (fdname, fbname) = os.path.split(fname)
    if(len(fbname) <= 0):
        fbname = "dummy"

    (fpname, fsname) = os.path.splitext(fbname)

    return([fdname, fpname, fsname[1:], ""])

#---------------------
# joinpath
#---------------------
# function to join file parts into a single filepath
#
# Pythonic because C version had to avoid creating heap objects
# Everything is an object in Python!

def joinpath(fparts):
    return("".join(fparts))

#====================================================
# dummy module
#----------------------------------------------------

#typedef struct {
#    SPFLOAT prm;
#} sp_dmod;

class sp_dmod(Structure):
    _fields_ = [
        ("prm", SPFLOAT)
        ]

#int sp_dmod_create(sp_dmod **p) {
#    *p = malloc(sizeof(sp_dmod));
#
#    return SP_OK;
#}

# NOTE: p passed in byref() rather than as pointer.

def sp_dmod_create(p):
    pp = cast(p, POINTER(POINTER(sp_dmod)))
    pp[0] = pointer(sp_dmod())

    return(SP_OK)


#int sp_dmod_destroy(sp_dmod **p) {
#    free(*p);
#
#    return SP_OK;
#}

# NOTE: p passed in byref() rather than as pointer.

def sp_dmod_destroy(p):
    pp = cast(p, POINTER(POINTER(sp_dmod)))
    pp[0] = POINTER(sp_dmod)()

    return(SP_OK)

#int sp_dmod_init(sp_data *sp, sp_dmod *p) {
#    p->prm = 0.0;
#
#    return SP_OK;
#}

def sp_dmod_init(sp, p):
    p[0].prm = 0.0 

    return(SP_OK)

#int sp_dmod_compute(sp_data *sp, sp_dmod *p, SPFLOAT *in, SPFLOAT *out) {
#    *out = *in;
# 
#    return SP_OK;
#}

# NOTE: inr and outr passed in byref() rather than as pointers.

def sp_dmod_compute(sp, p, inr, outr):
     inp = cast(inr, POINTER(SPFLOAT))
     outp = cast(outr, POINTER(SPFLOAT))
     
     outp[0] = inp[0]

     return(SP_OK)

#====================================================

#====================================================
# dummy application
#----------------------------------------------------

# Notes:
# 1) an ftable is a canned waveform table
# 2) not sure what the sp_ftbl members are
# 3) not sure sp->len is but appears to be total samples

CHANS = 4

sp_wavoutArrCHANS = POINTER(sp_wavout) * CHANS

class UserData(Structure):
    _fields_ = [
        ("wavin", POINTER(sp_wavin)),
        ("wavout", sp_wavoutArrCHANS),
        ("dmod", POINTER(sp_dmod))
#        ("ft", POINTER(sp_ftbl))
        ]

def callback(sp, udata, spin):
    ud = cast(udata, POINTER(UserData))
    spinp = cast(spin, POINTER(SPFLOAT))
    outv = SPFLOAT(0)

    inv = SPFLOAT(spinp[0])

    for chan in range(CHANS):
        sp_dmod_compute(sp, ud.contents.dmod, byref(inv), byref(outv))
        sp[0].out[chan] = outv

#====================================================

#====================================================
# example main
#----------------------------------------------------
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

    ofpartsb = splitpath(ofname)
    ofparts = [ofpartsb[0]+"/", ofpartsb[1]+"_", "", "."+ofpartsb[2]]

    # Create empty soundpipe

    sp_create(byref(sp))


    # Add I/O to soundpipe

    sp_wavin_create(byref(ud.wavin))

    c_ifname = ifname.encode('utf-8')
    sp_wavin_init(sp, ud.wavin, c_ifname)

    ofnamec = []
    for chan in range(CHANS):
        sp_wavout_create(byref(ud.wavout[chan]))
        ofnamec.append(joinpath([ofparts[0], ofparts[1], str(chan), ofparts[3]]))
        c_ofnamec = ofnamec[chan].encode('utf-8')
        if debug:
            print("%s"%ofnamec[chan])
        sp_wavout_init(sp, ud.wavout[chan], c_ofnamec)


    # build and configure soundpipe

    sp_dmod_create(byref(ud.dmod))
    sp_dmod_init(sp, ud.dmod)


    # adjust soundpipe length based on file to have best control

    sp[0].len = ud.wavin[0].wav.totalSampleCount


    # data buffer just to structure design

    din = SPFLOAT(0.0)
    dout = (SPFLOAT * CHANS)(*range(CHANS))


    # have to create actual storage here
    # oarr is actually a pointer to the first SPFLOAT in the array

    oarr = (SPFLOAT * CHANS)(*range(CHANS))   
    sp[0].out = cast(oarr, POINTER(SPFLOAT))
    sp[0].nchan = c_int(CHANS)


    # the processing

    dv2 = SPFLOAT(0.0)
    while sp[0].len > 0:
        sp_wavin_compute(sp, ud.wavin, POINTER(SPFLOAT)(), byref(din))
        callback(sp, byref(ud), byref(din))
        for chan in range(CHANS):
            sp_wavout_compute(sp, ud.wavout[chan], byref(SPFLOAT(sp[0].out[chan])),
                              byref(SPFLOAT(dout[chan])))

#            sp_wavout_compute(sp, ud.wavout[chan], byref(sp[0].out[chan]),
#                              byref(dout[chan]))
#
#            dv1 = SPFLOAT(sp[0].out[chan])
#            sp_wavout_compute(sp, ud.wavout[chan], byref(dv1),
#                              byref(dv2))
#            dout[chan] = dv2
            
        sp[0].len -= 1
        sp[0].pos += 1

    sp[0].out = POINTER(SPFLOAT)()


    # Dismantle soundpipe
 
    sp_dmod_destroy(byref(ud.dmod))


    # Shutdown I/O

    for chan in range(CHANS):
        sp_wavout_destroy(byref(ud.wavout[chan]))

    sp_wavin_destroy(byref(ud.wavin))


    # Clean up on completion

    sp_destroy(byref(sp))

    return 0


if __name__ == "__main__":
    ret = main()

    sys.exit(ret)
