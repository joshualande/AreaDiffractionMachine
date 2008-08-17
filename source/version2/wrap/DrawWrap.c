#include "Python.h"
#include "Numeric/arrayobject.h"
#include "polygon.c"


void getAlmostMinMax(PyArrayObject * data,int * almostMin,int * almostMax) {
    int i,j; 
    int val;
    int min,max;
    int secondMin,secondMax;

    min = INT_MAX;
    secondMin = INT_MAX;
    
    max = INT_MIN;
    secondMax = INT_MIN;

    for (i=0;i<data->dimensions[0];i=i+1) {
        for (j=0;j<data->dimensions[1];j=j+1) {
            val = *(int *)(data->data+i*data->strides[0]+j*data->strides[1]);
            if (val < min) {
                secondMin = min;
                min = val; 
            }
            if (val > max) {
                secondMax = max;
                max = val;
            }
        }
    }
    // if you immediately find the minimum or maximum value, then secondMin will never
    // be set to this value, so do so explicitly.
    if (secondMin == INT_MAX)
        secondMin = min;
    if (secondMax == INT_MIN)
        secondMax = max;

    *almostMin = secondMin;
    *almostMax = secondMax;
}


static PyObject * DrawWrap_getDiffractionImageString(PyObject *self, PyObject *args) {
    int temp1,temp2;
    double realMin,realMax;
    int x,y;
    double lowerBound,upperBound;
    double lowerPixel,upperPixel,logLowerPixel,logUpperPixel;
    double intensity;
    double scaledVal;
    int doLogScale;
    char * string;
    PyArrayObject * diffractionData;
    PyObject * returnString;
    PyArrayObject * palette;

    // these arrays are needed to do the threshold masking
    int doLessThanMask,doGreaterThanMask;
    double lessThanMask,greaterThanMask; 
    int lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB;
    int greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB;
 
    // these arrays are needed to do the pixel masking
    int doPolygonMask;
    PyArrayObject * polygonsX;
    PyArrayObject * polygonsY;
    PyArrayObject * polygonBeginningsIndex;
    PyArrayObject * polygonNumberOfItems;
    int polygonMaskColorR;
    int polygonMaskColorG;
    int polygonMaskColorB;

    logUpperPixel = logLowerPixel = scaledVal = 0; // to stop those annoying warnings

    int doScaleFactor = 0;
    double scaleFactor = 0;
    int setMinMax = 0;
    double minIntensity = 0;
    double maxIntensity = 0;

    PyArg_ParseTuple(args,"O!ddiO!idiiiidiiiiO!O!O!O!iiiididd",
            &PyArray_Type,&diffractionData,
            &lowerBound,&upperBound,&doLogScale,
            &PyArray_Type,&palette,
            &doLessThanMask,&lessThanMask,&lessThanMaskColorR,
            &lessThanMaskColorG,&lessThanMaskColorB,
            &doGreaterThanMask,&greaterThanMask,
            &greaterThanMaskColorR,
            &greaterThanMaskColorG,
            &greaterThanMaskColorB,
            &doPolygonMask,
            &PyArray_Type,&polygonsX,
            &PyArray_Type,&polygonsY,
            &PyArray_Type,&polygonBeginningsIndex,
            &PyArray_Type,&polygonNumberOfItems,
            &polygonMaskColorR,
            &polygonMaskColorG,
            &polygonMaskColorB,
            &doScaleFactor,
            &scaleFactor,
            &setMinMax,
            &minIntensity,
            &maxIntensity);

    getAlmostMinMax(diffractionData,&temp1,&temp2);
    realMin = (double)temp1;
    realMax = (double)temp2;

    if(doScaleFactor) {
        realMax /= scaleFactor;
    } else if (setMinMax) {
        realMin = minIntensity;
        realMax = maxIntensity;
    }

    lowerPixel = realMin + lowerBound*(realMax-realMin);
    upperPixel = realMin + upperBound*(realMax-realMin);

    if (doLogScale) {
        if (lowerPixel < 1) {
            logLowerPixel = 0;
        } else {
            logLowerPixel = log(lowerPixel);
        }

        if (upperPixel < 1) {
            logUpperPixel = 1;
        } else {
            logUpperPixel = log(upperPixel);
        }
    }

    // the whole point of doing this is so that the C code can write 
    // the data into the string in place. This is most efficient.
    returnString = PyString_FromStringAndSize(NULL,
            sizeof(char)*3*diffractionData->dimensions[0]*diffractionData->dimensions[1]);
    string = PyString_AsString(returnString);


    for (x=0;x<diffractionData->dimensions[0];x=x+1) {
        for (y=0;y<diffractionData->dimensions[1];y=y+1) {
            intensity = *(int *)(diffractionData->data+x*diffractionData->strides[0]+
                    y*diffractionData->strides[1]);

            // if we are doing polygon mask and the pixel is in one of the polygons,
            if (doPolygonMask && isInPolygons(polygonsX,polygonsY,
                    polygonBeginningsIndex,polygonNumberOfItems,(double)x,(double)y)) {

                // add in each of RGB from the color map separately
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+0) =
                        polygonMaskColorR;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+1) =
                        polygonMaskColorG;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+2) =
                        polygonMaskColorB;

            } else // try to color the pixels with the overloaded colors (if the pixel isn't good)
            if (doLessThanMask && intensity < lessThanMask) {

                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+0) = 
                            lessThanMaskColorR;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+1) = 
                            lessThanMaskColorG;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+2) = 
                            lessThanMaskColorB;

            } else if (doGreaterThanMask && intensity > greaterThanMask) {

                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+0) = 
                            greaterThanMaskColorR;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+1) = 
                            greaterThanMaskColorG;
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+2) = 
                            greaterThanMaskColorB;

            } else { // otherwise, give the pixel the regular color

                // possibly log scale the pixel
                if (doLogScale) {
                    // log(0) is undefined, so our graph will look perfectly fine if set to 1
                    if (intensity < 1) {
                        scaledVal = 0;
                    } else {
                        scaledVal = (log(scaledVal)-logLowerPixel)*255.0/(logUpperPixel-logLowerPixel);
                    }
                } else {
                    scaledVal = (intensity -lowerPixel)*255.0/(upperPixel-lowerPixel);
                }

                if (scaledVal < 0) scaledVal = 0;
                if (scaledVal > 255) scaledVal = 255;

                // add in each of RGB from the color map separately
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+0) = 
                        *(char *)(palette->data+(3*(int)scaledVal+0)*palette->strides[0]); // red
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+1) = 
                        *(char *)(palette->data+(3*(int)scaledVal+1)*palette->strides[0]); // green
                *(char *)(string+3*(x*diffractionData->dimensions[1]+y)+2) = 
                        *(char *)(palette->data+(3*(int)scaledVal+2)*palette->strides[0]); // blue
            }
        }
    }
    return returnString;
}


static PyObject * DrawWrap_getCakeImageString(PyObject *self, PyObject *args) {
    int temp1,temp2;
    double realMin,realMax;
    int i,j;
    double lowerBound,upperBound;
    double lowerPixel,upperPixel,logLowerPixel,logUpperPixel;
    double intensity; 
    double scaledVal;
    char * string;
    int doLogScale;
    PyArrayObject * cake;
    PyArrayObject * diffractionData;
    PyObject * returnString;
    PyArrayObject * palette;

    int doLessThanMask,doGreaterThanMask;
    double lessThanMask,greaterThanMask; 
    int lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB;
    int greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB;

    // these arrays are needed to do the pixel masking
    int doPolygonMask;
    int polygonMaskColorR;
    int polygonMaskColorG;
    int polygonMaskColorB;

    logUpperPixel = logLowerPixel = 0; // to stop those annoying warnings

    int doScaleFactor = 0;
    double scaleFactor = 0;
    int setMinMax = 0;
    double minIntensity = 0;
    double maxIntensity = 0;

    PyArg_ParseTuple(args,"O!O!ddiO!idiiiidiiiiiiiididd",
            &PyArray_Type,&cake,
            &PyArray_Type,&diffractionData,&lowerBound,&upperBound,
            &doLogScale,&PyArray_Type,&palette,
            &doLessThanMask,&lessThanMask,&lessThanMaskColorR,
            &lessThanMaskColorG,&lessThanMaskColorB,
            &doGreaterThanMask,&greaterThanMask,
            &greaterThanMaskColorR,&greaterThanMaskColorG,
            &greaterThanMaskColorB,
            &doPolygonMask,
            &polygonMaskColorR,
            &polygonMaskColorG,
            &polygonMaskColorB,
            &doScaleFactor,
            &scaleFactor,
            &setMinMax,
            &minIntensity,
            &maxIntensity);

    // get the minimum value from the diffractionData
    getAlmostMinMax(diffractionData,&temp1,&temp2);
    realMin = (double)temp1;
    realMax = (double)temp2;

    if(doScaleFactor) {
        realMax /= scaleFactor;
    } else if (setMinMax) {
        realMin = minIntensity;
        realMax = maxIntensity;
    }

    lowerPixel = realMin + lowerBound*(realMax-realMin);
    upperPixel = realMin + upperBound*(realMax-realMin);

    if (doLogScale) {
        if (lowerPixel < 1) {
            logLowerPixel = 0;
        } else {
            logLowerPixel = log(lowerPixel);
        }

        if (upperPixel < 1) {
            logUpperPixel = 1;
        } else {
            logUpperPixel = log(upperPixel);
        }
    }

    // the whole point of doing this is so that the C code can write 
    // the data into the string in place. This is most efficient.
    returnString = PyString_FromStringAndSize(NULL,
            sizeof(char)*3*cake->dimensions[0]*cake->dimensions[1]);
    string = PyString_AsString(returnString);

    for (i=0;i< cake->dimensions[0]; i=i+1) {
        for (j=0;j< cake->dimensions[1]; j=j+1) {

            intensity = *(double *)(cake->data+i*cake->strides[0]+j*cake->strides[1]);

            if (doPolygonMask & (intensity == -4)) {
            // masked pixels are coded in the cake data as -4

                // add in each of RGB from the color map separately
                *(char *)(string+3*(i*cake->dimensions[1]+j)+0) =  // red
                        polygonMaskColorR;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+1) = // green
                        polygonMaskColorG;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+2) = // blue
                        polygonMaskColorB;

            } else if (doLessThanMask && (intensity == -3)) {
            // try to color the pixels with the overloaded 
            // colors (if the pixel isn't good)
            // Too high pixels are coded in the cake data as -3

                // add in each of RGB from the color map separately
                *(char *)(string+3*(i*cake->dimensions[1]+j)+0) =  // red
                        lessThanMaskColorR;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+1) = // green
                        lessThanMaskColorG;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+2) = // blue
                        lessThanMaskColorB;

            } else if (doGreaterThanMask && (intensity == -2)) {
            // Too low pixels are coded in the cake data as -2

                *(char *)(string+3*(i*cake->dimensions[1]+j)+0) =  // red
                        greaterThanMaskColorR;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+1) = // green
                        greaterThanMaskColorG;
                *(char *)(string+3*(i*cake->dimensions[1]+j)+2) = // blue
                        greaterThanMaskColorB;

            } else { // otherwise, give the pixel the regular color

                if (doLogScale) {
                    // log(0) is undefined, so our graph will look perfectly fine if set to 1
                    if (intensity < 1) {
                        scaledVal = 0;
                    } else {
                        scaledVal = (log(intensity)-logLowerPixel)*255.0/
                                (logUpperPixel-logLowerPixel);
                    }
                } else {
                    scaledVal = (intensity-lowerPixel)*255.0/(upperPixel-lowerPixel);
                }

                if (scaledVal < 0) scaledVal = 0;
                if (scaledVal > 255) scaledVal = 255;

                // do the colormap

                *(char *)(string+3*(i*cake->dimensions[1]+j)+0) =  // red
                        *(char *)(palette->data+(3*(int)scaledVal+0)*palette->strides[0]);
                *(char *)(string+3*(i*cake->dimensions[1]+j)+1) = // green
                        *(char *)(palette->data+(3*(int)scaledVal+1)*palette->strides[0]);
                *(char *)(string+3*(i*cake->dimensions[1]+j)+2) = // blue
                        *(char *)(palette->data+(3*(int)scaledVal+2)*palette->strides[0]);
            }
        }
    }
    return returnString;
}


static PyMethodDef DrawWrap_methods[] = {
    {"getDiffractionImageString",  DrawWrap_getDiffractionImageString, METH_VARARGS, "test"},
    {"getCakeImageString",  DrawWrap_getCakeImageString, METH_VARARGS, "test"},
    {NULL,NULL}
};
    

void initDrawWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("DrawWrap", DrawWrap_methods); 
}

