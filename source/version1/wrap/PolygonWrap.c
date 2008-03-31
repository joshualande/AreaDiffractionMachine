#include "Python.h"
#include "Numeric/arrayobject.h"
#include "polygon.c"



static PyObject * PolygonWrap_insideWhichPolygon(PyObject *self, PyObject *args) {
    PyArrayObject * polygonsX;
    PyArrayObject * polygonsY;
    PyArrayObject * polygonBeginningsIndex;
    PyArrayObject * polygonNumberOfItems;

    double x,y;

    PyArg_ParseTuple(args,"O!O!O!O!dd",
            &PyArray_Type,&polygonsX,
            &PyArray_Type,&polygonsY,
            &PyArray_Type,&polygonBeginningsIndex,
            &PyArray_Type,&polygonNumberOfItems,&x,&y);

    return Py_BuildValue("i",insideWhichPolygon(polygonsX,polygonsY,
            polygonBeginningsIndex,polygonNumberOfItems,x,y));
}


static PyMethodDef PolygonWrap_methods[] = {
    {"insideWhichPolygon",PolygonWrap_insideWhichPolygon,METH_VARARGS,""},
    {NULL,NULL}
};


void initPolygonWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("PolygonWrap", PolygonWrap_methods); 
}

