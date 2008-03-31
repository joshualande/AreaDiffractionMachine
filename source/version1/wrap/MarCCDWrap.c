#include <stdio.h>
#include "Python.h"
#include "Numeric/arrayobject.h"
#include "marccd_header.h"


/******************************************************************
 * Function: swaplong = swaps bytes of 32 bit integers
 ******************************************************************/
void swaplong(data, nbytes)
    register char *data;
    int nbytes;
{
    register int i, t1, t2, t3, t4; for(i=nbytes/4;i--;) {
        t1 = data[i*4+3];
        t2 = data[i*4+2];
        t3 = data[i*4+1];
        t4 = data[i*4+0];
        data[i*4+0] = t1;
        data[i*4+1] = t2;
        data[i*4+2] = t3;
        data[i*4+3] = t4;
    }
}


static PyObject * MarCCDWrap_get_header(PyObject *self, PyObject *args) {
    MARCCD_HEADER hccd;

    char *filename;

    FILE *file;
    UINT32 width;
    UINT32 height;
    double distance;
    double pixelX;
    double pixelY;
    double wavelength;

    // take in a filename
    PyArg_ParseTuple(args,"s",&filename);

    // open file
    file = fopen(filename, "rb");
    // Ignore the tiff header
    fseek(file, 1024, SEEK_SET);

    // read the data directly into the data structure
    if (fread(&hccd, sizeof(MARCCD_HEADER), 1, file) < 1) {
        fclose(file);
        PyErr_SetString(PyExc_Exception,"Unable to read in the header.");
        return 0;
    }

    // I don't really get this byte swapping business.
    if (hccd.header_byte_order < 1234 || hccd.header_byte_order > 4321)
        swaplong((void *) &hccd, sizeof(MARCCD_HEADER));
    if (hccd.header_byte_order < 1234 || hccd.header_byte_order > 4321) {
        fclose(file);
        PyErr_SetString(PyExc_Exception,"Unable to get the little/big endian-ness of the file sorted properly.");
        return 0;
    }

    // get interesting stuff out of the header file. 
    width = hccd.nfast;
    height = hccd.nslow;
    if ((width < 1) || (height < 1)) {
        PyErr_SetString(PyExc_Exception,"MarCCD header file is no good because hte height and width of the image are unphysical.");
        return 0;
    }

    distance = 0.001 * hccd.xtal_to_detector;
    if(distance==0) {
        distance= 0.001*hccd.start_xtal_to_detector;
        if(distance==0)
            distance= 0.001*hccd.end_xtal_to_detector;
    }
	
    // pixel size in nanometers. We want pixel size in micron
    // Since 1 nanometer = .001 micro, multiply by .001 to get into micron
    pixelX = 0.001 * hccd.pixelsize_x;
    pixelY = 0.001 * hccd.pixelsize_y;
    wavelength = 0.00001 * hccd.source_wavelength;

    fclose(file);
    return Py_BuildValue("lldddd",width,height,distance,pixelX,pixelY,wavelength);

}


static PyMethodDef MarCCDWrap_methods[] = {
    {"get_header",  MarCCDWrap_get_header, METH_VARARGS, "test"},
    {NULL,NULL}
};
    

void initMarCCDWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("MarCCDWrap", MarCCDWrap_methods); 
}
