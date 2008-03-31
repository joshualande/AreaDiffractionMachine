#include "Python.h"
#include <stdio.h>

#include "Numeric/arrayobject.h"
#include "pck.c"

/*
 * Function must be passed a Numeric array of the right size and the file name
 */
static PyObject * UncompressWrap_get_pck(PyObject *self, PyObject *args) {
    char *filename;

    FILE *file;
    int size;
    unsigned short * image;
    int i,j; // loops

    int dimensions[2];
    PyArrayObject * diffractionData;

    PyArg_ParseTuple(args,"si",&filename,&size);

    // create a new Numeric data structure to hold the cake
    dimensions[0]=size;
    dimensions[1]=size;
    diffractionData = (PyArrayObject *)PyArray_FromDims(2,dimensions,PyArray_INT);

    // put the data into image
    image = malloc(size*size*sizeof(unsigned short));
    if (image == NULL) {
        PyErr_SetString(PyExc_MemoryError,"No memory to create temporary data structure.");
        return 0;
    }

    file = fopen(filename, "rb");
    get_pck(file,(short *)image);
    fclose(file);

    // put image into the actual data
    // Note that here you are also transposing the data! a[i][j] = b[j][i]
    for (i=0;i<size;i=i+1) {
        for (j=0;j<size;j=j+1) {
            *(int *)(diffractionData->data+i*diffractionData->strides[0]+j*diffractionData->strides[1]) = 
                    image[j*size+i];
        }
    }

    free(image);
    return PyArray_Return(diffractionData);
}


static PyMethodDef UncompressWrap_methods[] = {
    {"get_pck",  UncompressWrap_get_pck, METH_VARARGS, "test"},
    {NULL,NULL}
};
    

void initUncompressWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("UncompressWrap", UncompressWrap_methods); 
}

