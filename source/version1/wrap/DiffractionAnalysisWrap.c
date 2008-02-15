#include "Python.h"
#include "Numeric/arrayobject.h"
#include "polygon.c"

#include "Transform.c"
// pi constant
#define PI 3.14159265358979323846

double bilinearInterpolation(PyArrayObject *data, double x, double y) {
    int xLower, xUpper;
    int yLower, yUpper;
    double intensity;

    xLower = (int)(floor(x));
    xUpper = (int)(ceil(x));
    yLower = (int)(floor(y));
    yUpper = (int)(ceil(y));

    if (x > data->dimensions[0] || x < 0 ||
            y > data->dimensions[1] || y < 0) {
        // Cannot look outside the image
        // this could be ambiguous if negative data was stored in the array, 
        // so, well... don't look outside the array :)
        return -1; 
    } else if (xLower == xUpper && yLower == yUpper) {
        // if there is no interpolation to do...
        intensity = *(int *)(data->data + ((int)x)*data->strides[0] + 
                ((int)y)*data->strides[1]);
    } else if (xLower == xUpper) {
        // do a linear interpolation on y
        intensity = *(int *)(data->data + ((int)x)*data->strides[0] + 
                yLower*data->strides[1])*(1+yLower-y) + 
                *(int *)(data->data + ((int)x)*data->strides[0] + 
                yUpper*data->strides[1])*(y-yLower);
    } else if (yLower == yUpper) {
        // do a linear interpolation on x
        intensity = *(int *)(data->data + xLower*data->strides[0] + 
                ((int)y)*data->strides[1])*(1+xLower-x) + 
                *(int *)(data->data + xUpper*data->strides[0] + 
                ((int)y)*data->strides[1])*(x-xLower);
    } else {

        // bilinear interpolate for x and y
        intensity = *(int *)(data->data + xLower*data->strides[0] + 
                yLower*data->strides[1])*(xUpper-x)*(yUpper-y) +
                *(int *)(data->data + xUpper*data->strides[0] + 
                yLower*data->strides[1])*(x-xLower)*(yUpper-y) +
                *(int *)(data->data + xLower*data->strides[0] + 
                yUpper*data->strides[1])*(xUpper-x)*(y-yLower) +
                *(int *)(data->data + xUpper*data->strides[0] + 
                yUpper*data->strides[1])*(x-xLower)*(y-yLower);
    }
    return intensity;
}

static PyObject * DiffractionAnalysisWrap_BilinearInterpolation(PyObject *self, PyObject *args) {
    double x, y;
    PyArrayObject *data;

    PyArg_ParseTuple(args,"O!dd",&PyArray_Type,&data,&x,&y);
    return Py_BuildValue("d",bilinearInterpolation(data,x,y));
}


static PyObject * DiffractionAnalysisWrap_convertEnergyToWavelength(PyObject *self, PyObject *args) {
    double energy,wavelength;
    PyArg_ParseTuple(args,"d",&energy);
    wavelength = convertEnergyToWavelength(energy);
    return Py_BuildValue("d",wavelength);
}


static PyObject * DiffractionAnalysisWrap_convertWavelengthToEnergy(PyObject *self, PyObject *args) {
    double energy,wavelength;

    PyArg_ParseTuple(args,"d",&wavelength);

    energy = convertWavelengthToEnergy(wavelength);
    return Py_BuildValue("d",energy);
}

static PyObject * DiffractionAnalysisWrap_convertTwoThetaToQ(PyObject *self, PyObject *args) {
    double twoTheta, Q, wavelength;

    PyArg_ParseTuple(args,"dd",&twoTheta,&wavelength);

    Q = convertTwoThetaToQ(twoTheta,wavelength);
    return Py_BuildValue("d",Q);
}

static PyObject * DiffractionAnalysisWrap_convertQToTwoTheta(PyObject *self, PyObject *args) {
    double twoTheta, Q, wavelength;

    PyArg_ParseTuple(args,"dd",&Q,&wavelength); 
    
    twoTheta = convertQToTwoTheta(Q,wavelength);
    return Py_BuildValue("d",twoTheta);
}

/*
 * Wrap the getQChi function so that it can be called from python
 */
static PyObject * DiffractionAnalysisWrap_getQChi(PyObject *self, PyObject *args) {

    double centerX, centerY,distance,energy,alpha,beta,rotation;
    double xPixel,yPixel;
    double pixelLength,pixelHeight;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;

    double q,chi;

    cos_beta = sin_beta=-10;
    cos_alpha=sin_alpha = -10;
    cos_rotation=sin_rotation= -10;

    PyArg_ParseTuple(args,"ddddddddddd|dddddd",&centerX,
            &centerY,&distance,&energy,&alpha,&beta,&rotation,&xPixel,
            &yPixel,&pixelLength,&pixelHeight,&cos_beta,
            &sin_beta,&cos_alpha,&sin_alpha,&cos_rotation,&sin_rotation);

    if (cos_beta == -10) cos_beta  = cos(beta*PI/180.0);
    if (sin_beta == -10) sin_beta  = sin(beta*PI/180.0);
    if (cos_alpha == -10) cos_alpha = cos(alpha*PI/180.0);
    if (sin_alpha == -10) sin_alpha = sin(alpha*PI/180.0);
    if (cos_rotation == -10) cos_rotation = cos(rotation*PI/180.0);
    if (sin_rotation == -10) sin_rotation = sin(rotation*PI/180.0);

    getQChi(centerX,centerY,distance,energy,
        xPixel,yPixel,pixelLength,pixelHeight,rotation,
        cos_beta,sin_beta,cos_alpha,sin_alpha,
        cos_rotation,sin_rotation,&q,&chi);

    return Py_BuildValue("dd",q,chi);
}


/*
 * Wrap the getQChi function so that it can be called from python
 */
static PyObject * DiffractionAnalysisWrap_getXY(PyObject *self, PyObject *args) {
    double centerX, centerY,distance,energy,alpha,beta,rotation;
    double q,chi;
    double pixelLength,pixelHeight;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;
    double xPixel,yPixel;

    cos_beta = sin_beta=-10;
    cos_alpha=sin_alpha = -10;
    cos_rotation=sin_rotation= -10;

    PyArg_ParseTuple(args,"ddddddddddd|dddddd",&centerX,
            &centerY,&distance,&energy,&alpha,&beta,&rotation,&q,
            &chi,&pixelLength,&pixelHeight,&cos_beta,
            &sin_beta,&cos_alpha,&sin_alpha,&cos_rotation,&sin_rotation);

    if (cos_beta == -10) cos_beta  = cos(beta*PI/180.0);
    if (sin_beta == -10) sin_beta  = sin(beta*PI/180.0);
    if (cos_alpha == -10) cos_alpha = cos(alpha*PI/180.0);
    if (sin_alpha == -10) sin_alpha = sin(alpha*PI/180.0);
    if (cos_rotation == -10) cos_rotation = cos(rotation*PI/180.0);
    if (sin_rotation == -10) sin_rotation = sin(rotation*PI/180.0);
    
    getXY(centerX,centerY,distance,energy,q,chi,
            pixelLength,pixelHeight,rotation,cos_beta,sin_beta,
            cos_alpha,sin_alpha,cos_rotation,sin_rotation,
            &xPixel,&yPixel);

    return Py_BuildValue("dd",xPixel,yPixel);
}


/*
 * twotheta and chi are in degrees, so we must convert them to radiasn first
 */
double polarizationCorrection(double intensity, double P,double twotheta,double chi) {
    return intensity/(P*(1-pow(sin(twotheta*PI/180.0)*sin( (chi-90)*PI/180.0),2))+
            (1-P)*(1-pow(sin(twotheta*PI/180.0)*cos( (chi-90)*PI/180.0),2)));
}


/*
 * This function does the caking.
 * Function must be passed a Numeric array which is the diffraction data.
 * Function arguments are: data, centerX,centerY,distance,wavelength,
 * alpha,beta,qLower,qUpper,numQ, chiLower,chiUpper,numChi,pixelLength,pixelHeight
 */
static PyObject * DiffractionAnalysisWrap_cake(PyObject *self, PyObject *args) {
    PyArrayObject *diffractionData;
    PyArrayObject *cake;
    // the dimensions of the caked data
    int dimensions[2];

    double centerX,centerY,distance,energy,alpha,beta,rotation;
    double qLower,qUpper;
    int numQ;
    double chiLower,chiUpper;
    int numChi;
    double pixelLength,pixelHeight;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;
    double x,y;
    double q,chi; 
    int qBin,chiBin;
    double qStep,chiStep;
    double intensity;
    int doPolarizationCorrection;
    double P,twoTheta;
    int doGreaterThanMask;
    double greaterThanMask;
    int doLessThanMask;
    double lessThanMask;

    int doPolygonMask;
    PyArrayObject * polygonsX;
    PyArrayObject * polygonsY;
    PyArrayObject * polygonBeginningsIndex;
    PyArrayObject * polygonNumberOfItems;


    // get all of the parameters out of the python call
    PyArg_ParseTuple(args,"O!dddddddddiddiidididiO!O!O!O!dd",&PyArray_Type,&diffractionData,
        &centerX,&centerY,&distance,&energy,&alpha,&beta,&rotation,&qLower,
        &qUpper,&numQ,&chiLower,&chiUpper,&numChi,
        &doPolarizationCorrection,&P,
        &doGreaterThanMask,&greaterThanMask,&doLessThanMask,&lessThanMask,
        &doPolygonMask,
        &PyArray_Type,&polygonsX,
        &PyArray_Type,&polygonsY,
        &PyArray_Type,&polygonBeginningsIndex,
        &PyArray_Type,&polygonNumberOfItems,
        &pixelLength,&pixelHeight);

    // passed array has the diffraction data
    if (diffractionData->nd != 2 || diffractionData->descr->type_num != PyArray_INT) {
        PyErr_SetString(PyExc_ValueError,
            "diffractionData must be two-dimensional and of type integer");
        return 0;
    }

    // create a new Numeric data structure to hold the cake
    dimensions[0]=numChi;
    dimensions[1]=numQ;
    cake=(PyArrayObject *)PyArray_FromDims(2,dimensions,PyArray_DOUBLE);

    // calculate sin & cos for later use.
    cos_beta  = cos(beta*PI/180.0);
    sin_beta  = sin(beta*PI/180.0);
    cos_alpha = cos(alpha*PI/180.0);
    sin_alpha = sin(alpha*PI/180.0);
    cos_rotation = cos(rotation*PI/180.0);
    sin_rotation = sin(rotation*PI/180.0); 

    // calulate the step size between different bins
    qStep = (qUpper-qLower)/(numQ-1);
    chiStep = (chiUpper-chiLower)/(numChi-1);

    // for each bin
    for (qBin = 0; qBin < numQ; qBin += 1) {
        for (chiBin = 0; chiBin < numChi; chiBin += 1) {

            // get into the middle of the cell
            q = qLower + qBin*qStep + qStep/2.0;
            chi = chiLower + chiBin*chiStep + chiStep/2.0;

            // in the middle of the cell
            getXY(centerX,centerY,distance,energy,q,chi,pixelLength,pixelHeight,rotation,cos_beta,
                    sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation,&x,&y);

            // if the q,chi value is acutally in the diffraction image, then find the intensity
            // Note that there is only diffraction data up to (dimension-1)
            if (x >= 0 && x <= (diffractionData->dimensions[0]-1) &&
                    y >= 0 && y <= (diffractionData->dimensions[1]-1)) {


                intensity = bilinearInterpolation(diffractionData, x, y);

                // possibly do the polarization correction
                if (doPolarizationCorrection) {
                    twoTheta = convertQToTwoTheta(q,convertEnergyToWavelength(energy));
                    intensity = polarizationCorrection(intensity,P,twoTheta,chi);
                }
                
                    if (doPolygonMask && isInPolygons(polygonsX,polygonsY,
                            polygonBeginningsIndex,polygonNumberOfItems,x,y)) {

                    // if we are doing a polygon mask and our pixel is in one of the polygons,
                    // then we should assign its value to be -4 (by convention)
                    *(double *)(cake->data + chiBin*cake->strides[0] + qBin*cake->strides[1]) = -4;

                } else if (doGreaterThanMask && intensity > greaterThanMask) {
                    // if we are doing the greater than mask, if the current pixel is greater then 
                    // the threshold, then we should assign its value to be -2 (by convention).
                    *(double *)(cake->data + chiBin*cake->strides[0] + qBin*cake->strides[1]) = -2;
                } else if (doLessThanMask && intensity < lessThanMask) {
                    // if we are doing the lower than mask, if the current pixel is less then 
                    // the threshold, then we should assign its value to be -3 (by convention)
                    *(double *)(cake->data + chiBin*cake->strides[0] + qBin*cake->strides[1]) = -3;
                } else {
                    *(double *)(cake->data + chiBin*cake->strides[0] + qBin*cake->strides[1]) = intensity;
                }

            } else { // otherwise, define outside the image as -1 intensity.
                *(double *)(cake->data + chiBin*cake->strides[0] + qBin*cake->strides[1]) = -1;
            }
        }
    }
    return Py_BuildValue("N",cake);
}


static PyObject * DiffractionAnalysisWrap_integrate(PyObject *self, PyObject *args) {
    PyArrayObject *diffractionData;
    PyArrayObject *values;
    PyArrayObject *integratedIntensity;

    int dimensions[1]; // the dimensions of the integrated intensity

    double centerX,centerY,distance,energy,alpha,beta,rotation;
    double lower,upper;
    int num;

    double constraintLower,constraintUpper;

    double pixelLength,pixelHeight;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;
    unsigned int * total;
    int i; 
    double x,y; 
    double q,twoTheta,chi;
    int qBin,twoThetaBin,chiBin;
    double step;
    double intensity;
    char *type;
    char *constraintType;
    int doPolarizationCorrection;
    int doConstraint;
    double P;
    int verbose;

    int doGreaterThanMask;
    double greaterThanMask;
    int doLessThanMask;
    double lessThanMask;
   
    int doPolygonMask;
    PyArrayObject * polygonsX;
    PyArrayObject * polygonsY;
    PyArrayObject * polygonBeginningsIndex;
    PyArrayObject * polygonNumberOfItems;

    verbose = 0;

    // get the parameters out of the python call
    PyArg_ParseTuple(args,"O!dddddddddiddiidididiO!O!O!O!ddss",
            &PyArray_Type,&diffractionData,
            &centerX,&centerY,
            &distance,
            &energy,
            &alpha,&beta,&rotation,
            &lower,&upper,
            &num,
            &constraintLower,&constraintUpper,
            &doConstraint,
            &doPolarizationCorrection,&P,
            &doGreaterThanMask,&greaterThanMask,
            &doLessThanMask,&lessThanMask,
            &doPolygonMask,
            &PyArray_Type,&polygonsX,
            &PyArray_Type,&polygonsY,
            &PyArray_Type,&polygonBeginningsIndex,
            &PyArray_Type,&polygonNumberOfItems,
            &pixelLength,
            &pixelHeight,
            &type,
            &constraintType);

    // the types of integration
    // Remeber, strcmp returns 0 when they equal
    if (strcmp(type,"Q") != 0 && strcmp(type,"2theta") != 0 && strcmp(type,"chi") != 0) {
        PyErr_SetString( PyExc_Exception, "The type of integration must be Q, 2theta, or chi");
        return 0;
    }

    if (verbose) {
        printf("Doing Intensity Integration");
        printf("  The integration is over '%s'\n",type);
        printf("  Constrain the integration? %i\n",doConstraint);
        if (doConstraint) {
            printf("  The Type of constraint is '%s'\n",constraintType);
        }
    }

    if (doConstraint) {
        if (doConstraint && strcmp(type,"Q")==0 && strcmp(constraintType,"chi")!=0) {
            PyErr_SetString( PyExc_Exception, 
                "Cannot perform the desired integration. If the integration type is Q, the constrain integration type must be chi");
            return 0;
        }
        if (doConstraint && strcmp(type,"2theta")==0 && strcmp(constraintType,"chi")!=0) {
            PyErr_SetString( PyExc_Exception, 
                "Cannot perform the desired integration. If the integration type is 2theta, the constrain integration type must be chi");
            return 0;
        }
        if (doConstraint && strcmp(type,"chi")==0 && strcmp(constraintType,"Q")!=0 && strcmp(constraintType,"2theta")!=0) {
            PyErr_SetString( PyExc_Exception, 
                "Cannot perform the desired integration. If the integration type is chi, the constrain integration type must be either Q or 2theta");
            return 0;
        }
    }

    // passed array has to be 2 dimensional ints
    if (diffractionData->nd != 2 || diffractionData->descr->type_num != PyArray_INT) {
        PyErr_SetString(PyExc_Exception,"diffractionData must be two-dimensional and of type integer");
        return 0;
    }

    // create a new Numeric data structure to hold the integrated intensity
    dimensions[0]=num;
    integratedIntensity=(PyArrayObject *)PyArray_FromDims(1,dimensions,PyArray_DOUBLE);
    values = (PyArrayObject *)PyArray_FromDims(1,dimensions,PyArray_DOUBLE);


    // store totals also in a regular c data structure.
    total = malloc(num*sizeof(unsigned int) );
    if (total == NULL) {
        PyErr_SetString(PyExc_MemoryError,"No Memeory to create temporary data structure");
        return 0;
    }

    // initialize the data to 0
    for (i=0;i<num;i++) {
            total[i]=0;
            *(double *)(integratedIntensity->data + i*integratedIntensity->strides[0])=0;
    }

    // calculate sin & cos for later use.
    cos_beta  = cos(beta*PI/180.0);
    sin_beta  = sin(beta*PI/180.0);
    cos_alpha = cos(alpha*PI/180.0);
    sin_alpha = sin(alpha*PI/180.0);
    cos_rotation = cos(rotation*PI/180.0);
    sin_rotation = sin(rotation*PI/180.0); 

    // calulate the step size between different bins
    step = (upper-lower)*1.0/(num-1.0);

    if (verbose) {
        printf("  lower = %f, upper = %f\n",lower,upper);
        printf("  num = %d,  step = %f\n",num,step);
    }

    for (x=0.0;x<diffractionData->dimensions[0];x++) {
        for (y=0.0;y<diffractionData->dimensions[1];y++) {
            // treat each type of integration differently
            if (strcmp(type,"Q")==0) {
                // calculate the q chi cordiante for each pixel
                getQChi(centerX,centerY,distance,energy,x,y,pixelLength,
                        pixelHeight,rotation,cos_beta,sin_beta,cos_alpha,
                        sin_alpha,cos_rotation,sin_rotation,&q,&chi);

                // find the right bin to put it in
                qBin = (int)((q-lower)*1.0/step);

                // if the bin exists, put it into the bin
                if (qBin >=0 && qBin < num) {

                    // constraint must be of the chi value
                    // if chi is out of the constraint range, then ignore this value
                    if (doConstraint && (chi < constraintLower || chi > constraintUpper)) 
                        continue;

                    intensity = (double)*(int *)(diffractionData->data + 
                            ((int)x)*diffractionData->strides[0] + 
                            ((int)y)*diffractionData->strides[1]); 

                    total[qBin]+=1;
                    if (doPolarizationCorrection)
                        intensity = polarizationCorrection(intensity,P,twoTheta,chi);

                    // if we are doing maskinging, make sure the intensity has the 
                    // right bounds and is not in a polygon mask. Otherwise, ignore 
                    // the current pixel
                    if ( (doGreaterThanMask && intensity > greaterThanMask) ||
                            (doLessThanMask && intensity < lessThanMask) || 
                            (doPolygonMask && isInPolygons(polygonsX,polygonsY,
                            polygonBeginningsIndex,polygonNumberOfItems,x,y)))
                        continue;

                    *(double *)(integratedIntensity->data + 
                            qBin*integratedIntensity->strides[0]) += intensity;
                }
            } else if (strcmp(type,"2theta")==0) {
                getTwoThetaChi(centerX,centerY,distance,x,y,pixelLength,
                        pixelHeight,rotation,cos_beta,sin_beta,cos_alpha,
                        sin_alpha,cos_rotation,sin_rotation,&twoTheta,&chi);

                // find the right bin to put it in
                twoThetaBin = (int)((twoTheta-lower)*1.0/step);

                // if the bin exists, put it into the bin
                if (twoThetaBin >=0 && twoThetaBin < num) {

                    // constraint must be of the chi value
                    // if chi is out of the constraint range, then ignore this value
                    if (doConstraint && (chi < constraintLower || chi > constraintUpper))
                        continue;

                    intensity = (double)*(int *)(diffractionData->data + 
                            ((int)x)*diffractionData->strides[0] + 
                            ((int)y)*diffractionData->strides[1]); 

                    total[twoThetaBin]+=1;
                    if (doPolarizationCorrection) 
                        intensity = polarizationCorrection(intensity,P,twoTheta,chi);

                    // if we are doing maskinging, make sure the intensity has the 
                    // right bounds and is not in a polygon mask. Otherwise, ignore 
                    // the current pixel
                    if ( (doGreaterThanMask && intensity > greaterThanMask) ||
                            (doLessThanMask && intensity < lessThanMask) || 
                            (doPolygonMask && isInPolygons(polygonsX,polygonsY,
                            polygonBeginningsIndex,polygonNumberOfItems,x,y)))
                        continue;

                    *(double *)(integratedIntensity->data + 
                            twoThetaBin*integratedIntensity->strides[0]) += (double)intensity;

                }
            } else if (strcmp(type,"chi")==0) {
                getTwoThetaChi(centerX,centerY,distance,x,y,pixelLength,
                        pixelHeight,rotation,cos_beta,sin_beta,cos_alpha,
                        sin_alpha,cos_rotation,sin_rotation,&twoTheta,&chi);

                q = convertTwoThetaToQ(twoTheta,convertEnergyToWavelength(energy));

                // find the right bin to put it in
                chiBin = (int)((chi-lower)*1.0/step);

                // chi values can vary from -360 to 360. If our value is not in a bin, check
                // if 360-chi fall in a bin. Since the chi range is at most 360 degrees,
                // we will never have to bin something in two places.
                if (chiBin <0 || chiBin >= num) {
                    chi-=360;
                    chiBin = (int)((chi-lower)*1.0/step);
                }

                // if the bin exists, put it into the bin
                if (chiBin >=0 && chiBin < num) {

                    // if chi is out of the constraint range, then ignore this value
                    if (doConstraint && strcmp(constraintType,"Q")==0 && 
                            (q < constraintLower || q > constraintUpper))
                        continue;
                    if (doConstraint && strcmp(constraintType,"2theta")==0 && 
                            (twoTheta < constraintLower || twoTheta > constraintUpper))
                        continue;

                    intensity = (double)*(int *)(diffractionData->data + 
                            (int)x*diffractionData->strides[0] + 
                            ((int)y)*diffractionData->strides[1]); 

                    total[chiBin]+=1;
                    if (doPolarizationCorrection) 
                        intensity = polarizationCorrection(intensity,P,twoTheta,chi);

                    // if we are doing maskinging, make sure the intensity has the 
                    // right bounds and is not in a polygon mask. Otherwise, ignore 
                    // the current pixel
                    if ( (doGreaterThanMask && intensity > greaterThanMask) ||
                            (doLessThanMask && intensity < lessThanMask) || 
                            (doPolygonMask && isInPolygons(polygonsX,polygonsY,
                            polygonBeginningsIndex,polygonNumberOfItems,x,y)))
                        continue;

                    *(double *)(integratedIntensity->data + 
                            chiBin*integratedIntensity->strides[0]) += intensity;
                }
            }

        }
    }

    for (i=0;i<num;i++) {
        // set the values values
        *(double *)(values->data + i*values->strides[0]) = (lower + (i+0.5)*step);

        // You only need to acutally do the average if there is more then 1 value
        if (total[i]>1) {
            *(double *)(integratedIntensity->data + i*integratedIntensity->strides[0]) /= total[i];
        } else {
            // -1 means nothing was put into the bin
            *(double *)(integratedIntensity->data + i*integratedIntensity->strides[0]) = -1;
        }

    }

    // free the array we created so that we do not cause a memory leak
    free(total);

    // Why I have to do this is described http://mail.python.org/pipermail/python-list/2002-October/167549.html
    return Py_BuildValue("NN",values,integratedIntensity);
}


static PyMethodDef DiffractionAnalysisWrap_methods[] = {
    {"bilinearInterpolation",DiffractionAnalysisWrap_BilinearInterpolation,METH_VARARGS,""},
    {"cake",DiffractionAnalysisWrap_cake,METH_VARARGS,""},
    {"integrate",DiffractionAnalysisWrap_integrate,METH_VARARGS,""},
    {"getQChi",DiffractionAnalysisWrap_getQChi,METH_VARARGS,""},
    {"convertEnergyToWavelength",DiffractionAnalysisWrap_convertEnergyToWavelength,METH_VARARGS,""},
    {"convertWavelengthToEnergy",DiffractionAnalysisWrap_convertWavelengthToEnergy,METH_VARARGS,""},
    {"convertTwoThetaToQ",DiffractionAnalysisWrap_convertTwoThetaToQ,METH_VARARGS,""},
    {"convertQToTwoTheta",DiffractionAnalysisWrap_convertQToTwoTheta,METH_VARARGS,""},
    {"getXY",DiffractionAnalysisWrap_getXY,METH_VARARGS,""},
    {NULL,NULL}
};
    

void initDiffractionAnalysisWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("DiffractionAnalysisWrap", DiffractionAnalysisWrap_methods); 
}

