#include "Python.h"
#include "Numeric/arrayobject.h"
#include "pnpoly.c"

// this function does the real work


/*
 * Returns the index of the polygon that the x,y coordinate
 * is in. If the coordiante is in multiple polygons, then
 * the program will pick the one with the lowest index.
 * If the point is not in any of the polygons, then -1 is
 * returned
 */
int insideWhichPolygon(PyArrayObject * polygonsX,
        PyArrayObject * polygonsY,
        PyArrayObject * polygonBeginningsIndex, 
        PyArrayObject * polygonNumberOfItems,
        double x, double y) {

    int i;
    // the index in the inputted arrays of the beginning of
    // the current polygon
    int index; 
    int npol; // the number of points in the current polygon

    // a pointer to the beginning of the x values of the polygon
    double * xp; 

    // the same with the y values.
    double * yp;

    for (i=0;i<polygonBeginningsIndex->dimensions[0];i++) {
    // if inside poly, return true

        index = *(int *)(polygonBeginningsIndex->data +
            i*polygonBeginningsIndex->strides[0]);

        npol = *(int *)(polygonNumberOfItems->data +
            i*polygonNumberOfItems->strides[0]);

        xp = (double *)(polygonsX->data+
            index*polygonsX->strides[0]);

        yp = (double *)(polygonsY->data+
            index*polygonsY->strides[0]);

        // func returns 1 if x,y is in the current polygon
        if (pnpoly(npol,xp,yp,x,y)) {
            return i;
        }
    }
    // if not in any polygon, return 0
    return -1;
}


/*
 * Decides if a particular point is in any of the
 * pixel mask polygons that are given
 */
int isInPolygons(PyArrayObject * polygonsX,
        PyArrayObject * polygonsY,
        PyArrayObject * polygonBeginningsIndex,
        PyArrayObject * polygonNumberOfItems,
        double x, double y) {

    if (insideWhichPolygon(polygonsX,polygonsY,polygonBeginningsIndex,
            polygonNumberOfItems,x,y) != -1) {
        // polygon found
        return 1; 
    }
    // polygon not found
    return 0;
}

