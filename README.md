SoundpipeDemoPy
===============
This is a simple demonstration of how to use the static shared object [Soundpipe](https://github.com/AudioKit/AudioKit) library in Python with the `ctypes` module.

This demo is based on example code found in the documentation of old versions of Soundpipe found in Github before Soundpipe was absorbed into AudioKit, e.g. ["How to Create a Soundpipe Module"](https://github.com/narner/Soundpipe/blob/dev/util/module_howto.md).  It is a direct Python translation of [SoundPipeDemoC](https://github.com/hangarr/SoundpipeDemoC).

About Python `ctypes`
---------------------
The [`ctypes`](https://docs.python.org/3/library/ctypes.html) ([docs](https://docs.python.org/dev/library/ctypes.html)) module is the simplest, and actually quite impressive way to call C code from Python code.  

It's helpful to have a several things in mind using `ctypes`:

1. C identifiers signify storage locations (i.e. "variables").  Python identifiers are labels for objects.  All entities in Python are objects.
2. C pointers are variable which store addresses of other variables. Python doesn't have pointers because Python doesn't have variables. Arrays are the unifying approach between the two languages for implementing the pointer metaphor.  The first location in an array is the storage for a value "pointed to" by the array name.
3. C functions can be called from Python and C code can "callback" to Python functions. Python functions can be called from Python using `ctypes`.
4. `ctypes` implements a Python object (Python classes for C struts) and a C variable for every data entity.  When implementing a Python function called from Python that creates a Python class/C variable (ie. using `malloc`) one must manually persist the Python class backing a `malloc`ed C entity.  The C entity will be persisted if a pointer to it is persisted.  

The `straightpipe.py` and `multipipe.py` examples illustrate all these principles.

Setup
-----
This example assumes that the static shared object library `libsoundpipe.so` is found in a folder `./soundpipe` at the same level of the file system as the demo project folder `./SoundpipeDemoPy`.

The Python sources manually specify path information for loading modules beyond the default Python methods.  One can modify the Python sources to locate data files and Python modules elsewhere.


Running
-------
These are both run the same way:
```
> cd ./build
> ./singlepipe.py [-d] -o ./path/to/dest.wav ./path/to/src.wav
> ./multipipe.py [-d] -o ./path/to/dest.wav ./path/to/src.wav
```
The `straightpipe.py` executable should just copy `src.wav` to `dest.wav`.  The `multipipe.py` executable should create multiple copies `dest_0.wav ... dest_3.wav` of `src.wav`.

The `-d` option provides a minimal amount of debug information.  At this point this is just the specified `src.wav`, the specified `dest.wav`, and the copies actually created.