#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>


#include "Python.h"
#include "Numeric/arrayobject.h"

#include "lm.h"
#include "Transform.c"

#define PI 3.14159265358979323846

// silly data strucure for getting two arrays returned from a function.
struct both {
    double * first;
    double * second;
};


/* 
 * Finds one particular peak and returns the x,y cordinates of it 
 * by modifying peakX and peakY
 */
struct both * constantChiSlice(PyArrayObject * diffractionData,double xCenter,
        double yCenter,double distance,double energy,double pixelLength,
        double pixelHeight,double alpha,double beta,double rotation,double qLower,
        double qUpper, double chi,int * numValues) {

    double x1,y1;
    double x2,y2;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;
    double m;
    int xSize,ySize;
    double xUpperFirst,yUpperFirst,xLowerFirst,yLowerFirst;
    double xUpperSecond,yUpperSecond,xLowerSecond,yLowerSecond;
    double xCurrent,yCurrent;
    int dataLow,dataHigh;
    int xLow,xHigh,yLow,yHigh;
    int counter;
    double qCurrent,chiCurrent;
    double dataInterpolate;

    struct both * vals;

    cos_beta  = cos(beta*PI/180.0);
    sin_beta  = sin(beta*PI/180.0);
    cos_alpha = cos(alpha*PI/180.0);
    sin_alpha = sin(alpha*PI/180.0);
    cos_rotation = cos(rotation*PI/180.0);
    sin_rotation = sin(rotation*PI/180.0);

    // find the beginning & ending pixel values for our Q,chi range.
    getXY(xCenter,yCenter,distance,energy,qLower,chi,
        pixelLength,pixelHeight,rotation,cos_beta,sin_beta,
        cos_alpha,sin_alpha,cos_rotation,sin_rotation,&x1,&y1);
   
    getXY(xCenter,yCenter,distance,energy,qUpper,chi,
        pixelLength,pixelHeight,rotation,cos_beta,sin_beta,
        cos_alpha,sin_alpha,cos_rotation,sin_rotation,&x2,&y2);

    xSize = diffractionData->dimensions[0];
    ySize = diffractionData->dimensions[0];
    
    // If the two points to find values between are off the image, 
    // Point the answer to nothing.
    if (ceil(x1)<0 || floor(x1)>xSize || ceil(y1)<0 || 
        floor(y1)>=ySize || ceil(x2)<0 || 
        floor(x2) >= xSize || ceil(y2)<0 || floor(y2)>=ySize) {
        return NULL;
    }

    // Make sure that xLower < xUpper for our first sweep
    if (x1>x2) {
        xUpperFirst=x1;yUpperFirst=y1;
        xLowerFirst=x2;yLowerFirst=y2;
    } else {
        xLowerFirst=x1;yLowerFirst=y1;
        xUpperFirst=x2;yUpperFirst=y2;
    }

    // Make sure that yLower < yUpperfor our second sweep
    if (y1 > y2) {
        xUpperSecond=x1;yUpperSecond=y1;
        xLowerSecond=x2;yLowerSecond=y2;
    } else {
        xLowerSecond=x1;yLowerSecond=y1;
        xUpperSecond=x2;yUpperSecond=y2;
    }

    // figure out all the data points to sample 
    *numValues = ( (int)floor(xUpperFirst)-(int)ceil(xLowerFirst) +1 );
    if (yUpperSecond != yLowerSecond)
        *numValues += ( (int)floor(yUpperSecond)-(int)ceil(yLowerSecond) +1 );

    vals=malloc( sizeof(struct both) );
    vals->first = malloc( (*numValues)*sizeof(double) );
    vals->second = malloc( (*numValues)*sizeof(double) );

    m=(yUpperFirst-yLowerFirst)*1.0/(xUpperFirst-xLowerFirst);

    counter=0;

    for(xCurrent=ceil(xLowerFirst);xCurrent<=floor(xUpperFirst);xCurrent++) {
        // get all points that lie on constant integer y values in the image
        yCurrent=yLowerFirst +m*(xCurrent-xLowerFirst);

        yHigh = (int)ceil(yCurrent);
        yLow = (int)floor(yCurrent);

        dataLow=*(int *)(diffractionData->data + ((int)xCurrent)*diffractionData->strides[0] + 
                yLow*diffractionData->strides[1]);
        dataHigh=*(int *)(diffractionData->data + ((int)xCurrent)*diffractionData->strides[0] + 
                yHigh*diffractionData->strides[1]);

        dataInterpolate = dataLow + (yCurrent-yLow)*(dataHigh-dataLow);

        getQChi(xCenter,yCenter,distance,energy,xCurrent,yCurrent,
                pixelLength,pixelHeight,rotation,cos_beta,sin_beta,cos_alpha,
                sin_alpha,cos_rotation,sin_rotation,&qCurrent,&chiCurrent);

        vals->first[counter] = qCurrent;
        vals->second[counter] = dataInterpolate;
        counter++;
    }

    if (yUpperSecond - yLowerSecond > .00001 ) {
        m=(xUpperSecond-xLowerSecond)*1.0/(yUpperSecond-yLowerSecond);

        for (yCurrent=(int)ceil(yLowerSecond);yCurrent<=(int)floor(yUpperSecond);yCurrent++) {
            // get all points that lie on constant integer x values in the image
            
            xCurrent = xLowerSecond + m*(yCurrent-yLowerSecond);

            xHigh=(int)ceil(xCurrent);
            xLow=(int)floor(xCurrent);

            dataLow=*(int *)(diffractionData->data + xLow*diffractionData->strides[0] + 
                    ((int)yCurrent)*diffractionData->strides[1]);
            dataHigh=*(int *)(diffractionData->data + xHigh*diffractionData->strides[0] + 
                    ((int)yCurrent)*diffractionData->strides[1]);

            dataInterpolate = dataLow + (xCurrent-xLow)*(dataHigh-dataLow);

            getQChi(xCenter,yCenter,distance,energy,xCurrent,yCurrent,
                    pixelLength,pixelHeight,rotation,cos_beta,sin_beta,cos_alpha,
                    sin_alpha,cos_rotation,sin_rotation,&qCurrent,&chiCurrent);

            vals->first[counter] = qCurrent;
            vals->second[counter] = dataInterpolate;
            counter++;
        }
    }

    // now, counter must equal *numValues. Return success
    return vals;
}


double average(double * list,int num) {
    int i;
    double total;

    total=0;
    for (i=0;i<num;i++) {
        total+=list[i];
    }
    return total*1.0/num;
}


int maxIndex(double * list,int num) {
    int index,i;

    index = 0;
    if (num==1)
        return index;

    for (i=1;i<num;i++) {
        if (list[i]>list[index]) {
            index = i;
        }
    }
    return index;
}


void gaussian(double *p, double *f, int m, int n, void *data) {
    register int i;

    // returns f(x) for all n inputted x values given a set of parameters.
    double * x = (double *)(data);

    for(i=0; i<n; ++i) {
        f[i]=p[0]*exp(-(x[i]-p[1])*(x[i]-p[1])*1.0/(2*p[2]*p[2]))+p[3];
    }
}


int fitPeak(double xCenter,double yCenter,double distance,double energy,
        double pixelLength,double pixelHeight,double alpha,double beta,double rotation,
        double * sliceQ,double * sliceVal,int numValues,
        double qLower,double qUpper,double chi,double allowedStddevRatio,double *x,double *y,double * qFit,double * deviationFit) {

    double avgVal,maxVal;
    int index;
    double p[4];
    int status;
    double cos_beta,sin_beta,cos_alpha,sin_alpha,cos_rotation,sin_rotation;
    double stddev,sum;
    int i,num;
    //double chiSquare,fit;

    double heightFit,bgFit;
    double covar[4][4];

    int VERBOSE;

    VERBOSE = 0;

    // can't fit unless you have several values
    if (numValues < 10) 
        return 0;

    avgVal = average(sliceVal,numValues);
    index = maxIndex(sliceVal,numValues);
    maxVal = sliceVal[index];

    // 'real' parameters
    p[0]=maxVal-avgVal;
    p[1]=sliceQ[index];
    p[2]= (qUpper-qLower)/15.0;
    p[3]= avgVal;

    status=dlevmar_dif(gaussian, p, sliceVal, 4, numValues, 
            1000,NULL, NULL, NULL,*covar,(void *)sliceQ);

    // check to see if fit is good.
    // if not, return 0 to tell the code that no fit was found

    if (status <= 0) // for successful operation status > 0
        return 0;

    heightFit = p[0];
    *qFit = p[1];
    *deviationFit = p[2]; // pass pack to caller
    bgFit = p[3];
    sum = 0;
    num = 0;

    /*
    if (sqrt(covar[0][0]) > heightFit) {
        if (VERBOSE) printf("Uncertanty in height large compared to height.\n");
        return 0;
    }
    */

    /*
    if (sqrt(covar[1][1]) > *deviationFit) {
        if (VERBOSE) printf("Uncertanty in postion large compared to width of peak.\n");
        return 0;
    }
    */


    // I am not sure this is a good thing to test, b/c there could be a good fit even with a weird b/g
    /*
    if (sqrt(covar[3][3]) > .3*heightFit) {
        if (VERBOSE) printf("Uncertanty in backgound too much\n");
        return 0;
    }
    */
        

    // peak must be signifigantly larger then background
    /*
    if (heightFit < 0.05*bgFit) {
        if (VERBOSE) printf("Peak is not tall enough to count\n");
        return 0;
    }
    */
    
    // make sure fit does not fall too far off the data
    if (*qFit-2* (*deviationFit) < qLower || *qFit+2* (*deviationFit) > qUpper) {
        if (VERBOSE) printf("Fit is too far off the data.\n");
        return 0;
    }

    stddev = 0;
    sum = 0;
    num = 0;

    // calculate variation of background outsize 2 sigma of fit
    for (i=0;i<numValues;i++) {
        if (sliceQ[i] > *qFit+2* (*deviationFit) || sliceQ[i] < 
                *qFit-2* (*deviationFit) ) {
            sum+=(sliceVal[i]-bgFit)*(sliceVal[i]-bgFit);
            num+=1;
        }
    }
    stddev = sqrt(sum*1.0/num);

    // make sure height is bigger then deviation of background by user specified ratio
    if (heightFit < allowedStddevRatio*stddev) {
        if (VERBOSE) printf("Background stddev is too large.\n");
        return 0;
    }

    // good fit, calc x,y cordinates of it.
    cos_beta  = cos(beta*PI/180.0);
    sin_beta  = sin(beta*PI/180.0);
    cos_alpha = cos(alpha*PI/180.0);
    sin_alpha = sin(alpha*PI/180.0);
    cos_rotation = cos(rotation*PI/180.0);
    sin_rotation = sin(rotation*PI/180.0);

    // get physical pixel cordinates
    getXY(xCenter,yCenter,distance,energy,*qFit,chi,
        pixelLength,pixelHeight,rotation,cos_beta,sin_beta,
        cos_alpha,sin_alpha,cos_rotation,sin_rotation,x,y);

    return 1; // success!
}
        

static PyObject * FitWrap_getPeak(PyObject *self, PyObject *args) {
    PyArrayObject * diffractionData;
    double xCenter,yCenter,distance,energy,alpha,beta,rotation;
    double pixelLength,pixelHeight;
    double qLower,qUpper,chi;

    int numValues;
    struct both * vals;
    double * sliceQ;
    double * sliceVal;
    int status;
    double fitX,fitY,qFit,deviationFit;
    double stddev;

    // get the parameters out of the python call
    PyArg_ParseTuple(args,"O!ddddddddddddd",&PyArray_Type,&diffractionData,
            &stddev,&xCenter,&yCenter,&distance,&energy,&alpha,&beta,&rotation,
            &qLower,&qUpper,&chi,&pixelLength,&pixelHeight);

    vals = constantChiSlice(diffractionData,xCenter,yCenter,
            distance,energy,pixelLength,pixelHeight,alpha,
            beta,rotation,qLower,qUpper,chi,&numValues);

    if (vals==NULL) {
        PyErr_SetString(PyExc_ValueError, "Cannot find the particular peaks because the call to the function constant chi slice failed.");
        return 0;
    }
    
    // get the data back from the return
    sliceQ = vals->first;
    sliceVal = vals->second;
    free(vals);

    status = fitPeak(xCenter,yCenter,distance,energy,
        pixelLength,pixelHeight,alpha,beta,rotation,sliceQ,
        sliceVal,numValues,qLower,qUpper,chi,stddev,&fitX,&fitY,&qFit,&deviationFit);

    free(sliceQ);
    free(sliceVal);

    if (status != 1) {
        PyErr_SetString( PyExc_ValueError, "Fit of peak did not work.");
        return 0;
    }

    return Py_BuildValue("(d,d,d,d)",fitX,fitY,qFit,deviationFit);
}
      

// silly data strucure for getting two arrays returned from a function.
struct everything {
    double * x;
    double * y;
    double * qReal;
    double * intensity;
    double pixelLength;
    double pixelHeight;
};


void residual(double *p, double *qFit, int m, int n, void *data) {
    register int i;
    struct everything * useful;
    double q,chi;
    double rotation;
    double cos_beta,sin_beta;
    double cos_alpha,sin_alpha;
    double cos_rotation,sin_rotation;

    useful = (struct everything *)(data);

    // calculate sin & cos for later use.
    cos_alpha = cos(p[4]*PI/180.0);
    sin_alpha = sin(p[4]*PI/180.0);
    cos_beta  = cos(p[5]*PI/180.0);
    sin_beta  = sin(p[5]*PI/180.0);
    rotation = p[6];
    cos_rotation = cos(p[6]*PI/180.0);
    sin_rotation = sin(p[6]*PI/180.0); 

    for (i=0;i<n;i++) {
        getQChi(p[0],p[1],p[2],p[3],useful->x[i],useful->y[i],
            useful->pixelLength,useful->pixelHeight,rotation,cos_beta,
            sin_beta,cos_alpha,sin_alpha,cos_rotation,
            sin_rotation,&q,&chi);
        qFit[i] = q;
    }

}


double getResidual(double *p, double *qReal, int m, int n, void *data) {
    double * qFit;
    int i;
    double total;
    total = 0;

    qFit = malloc(n*sizeof(double));
    residual(p,qFit,m,n,data);
    for (i=0;i<n;i++) 
        total += (qFit[i]-qReal[i])*(qFit[i]-qReal[i]);
    free(qFit);

    // normalize based upon the number of peaks to fit, so that
    // the residual won't be significantly higher when more
    // peaks are added to the fit.
    total = total/n;
    return total;
}


/*
 * Performs the image calibration. Requires Numeric arrays containing x values, 
 * y values, Q values, and intensities for diffraction data. xValues[i], yValues[i]
 * refer to the x,y pixel coordinate of a diffraction peak and qValues[i] and
 * intensity[i] is the Q value (from the peak list) and intensity of the peak.
 * Then requires an initial guess of the x center of the image, and whether or
 * not to fix the parameter. The program requires the same pair for the y center,
 * the detector distance, the energy, alpha, beta, rotation. It then requires 
 * the value of the pixel length and pixel height.
 *
 * The program returns the refined value of the x center of the image, the y center
 * of the image, the distance, energy, alpha, beta, and rotation. It returns 
 * a numeric array containing the covariance matrix, a calculation of the initial
 * residual, the final residual per peak, and the reason for quitting (told
 * to the function by the fitting algorithm).
 */
static PyObject * FitWrap_fitCalibrationParameters(PyObject *self, PyObject *args) {
 
    PyArrayObject * xValues;
    PyArrayObject * yValues;
    PyArrayObject * qReal;
    PyArrayObject * intensity;

    int covarianceMatrixDimensions[2];
    PyArrayObject * covarianceMatrix;

    double centerX,centerY,distance,energy,alpha,beta,rotation;
    int fixedCenterX,fixedCenterY,fixedDistance,fixedEnergy,fixedAlpha,fixedBeta,fixedRotation;
    double pixelLength,pixelHeight;

    struct everything * useful;

    double p[7]; // the parameters
    double lb[7]; // lower bounds
    double ub[7]; // upper bounds
    int status;
    int length;
    double info[LM_INFO_SZ];

    double initialResidual;
    double finalResidual;

    PyArg_ParseTuple(args,"O!O!O!O!didididididididd",
            &PyArray_Type,&xValues,
            &PyArray_Type,&yValues,
            &PyArray_Type,&qReal,
            &PyArray_Type,&intensity,
            &centerX,&fixedCenterX,&centerY,&fixedCenterY,
            &distance,&fixedDistance,&energy,&fixedEnergy,
            &alpha,&fixedAlpha,&beta,&fixedBeta,
            &rotation,&fixedRotation,&pixelLength,&pixelHeight);

    if (xValues->nd != 1 || xValues->descr->type_num != PyArray_DOUBLE) {
        PyErr_SetString(PyExc_ValueError,
                "First array to function Fit must be a 1 dimensional array of doubles.");
        return 0;
    }
    if (yValues->nd != 1 || yValues->descr->type_num != PyArray_DOUBLE) {
        PyErr_SetString(PyExc_ValueError,
                "Second array to function Fit must be a 1 dimensional array of doubles.");
        return 0;
    }
    if (qReal->nd != 1 || qReal->descr->type_num != PyArray_DOUBLE) {
        PyErr_SetString(PyExc_ValueError,
                "Third array to function Fit must be a 1 dimensional array of doubles.");
        return 0;
    }
    if (intensity->nd != 1 || intensity->descr->type_num != PyArray_DOUBLE) {
        PyErr_SetString(PyExc_ValueError,
                "Fourth array to function Fit must be a 1 dimensional array of doubles.");
        return 0;
    }

    if (intensity->dimensions[0] <= 7) {
        PyErr_SetString(PyExc_ValueError,
                "Cannot fit calibration data because the calibration parameters must be fit to at least 8 peaks.");
        return 0;
    }


    covarianceMatrixDimensions[0]=7;
    covarianceMatrixDimensions[1]=7;
    covarianceMatrix = (PyArrayObject *)PyArray_FromDims(2,
            covarianceMatrixDimensions,PyArray_DOUBLE);

    length = xValues->dimensions[0];
    useful = malloc( sizeof(struct everything) );

    length = xValues->dimensions[0];
    useful->x= (double *)xValues->data;
    useful->y= (double *)yValues->data;
    useful->intensity = (double *)intensity->data;
    useful->pixelLength = pixelLength;
    useful->pixelHeight = pixelHeight;

    // initial guesses
    p[0] = centerX;
    p[1] = centerY;
    p[2] = distance;
    p[3] = energy;
    p[4] = alpha;
    p[5] = beta;
    p[6] = rotation;

    // set the bounds on parameters
    if (fixedCenterX) {
        lb[0] = centerX;
        ub[0] = centerY;
    } else {
        lb[0] = -FLT_MAX;
        ub[0] = FLT_MAX;
    }

    if (fixedCenterY) {
        lb[1] = centerY;
        ub[1] = centerY;
    } else {
        lb[1] = -FLT_MAX; 
        ub[1] = FLT_MAX;
    }

    if (fixedDistance) {
        lb[2] = distance;
        ub[2] = distance;
    } else {
        lb[2] = 0;
        ub[2] = FLT_MAX;
    }

    if (fixedEnergy) {
        lb[3] = energy;
        ub[3] = energy;
    } else {
        lb[3] = 0;
        ub[3] = FLT_MAX; 
    }

    if (fixedAlpha) {
        lb[4] = alpha;
        ub[4] = alpha;
    } else {
        lb[4] = -90;
        ub[4] = 90;
    }

    if (fixedBeta) {
        lb[5] = beta;
        ub[5] = beta;
    } else {
        lb[5] = -90;
        ub[5] = 90;
    }

    if (fixedRotation) {
         lb[6] = rotation;
         ub[6] = rotation;
    } else {
        lb[6] = -360;
        ub[6] = 360;
    }

    initialResidual = getResidual(p,(double *)qReal->data, 7, length, (void *)useful);

    status=dlevmar_bc_dif(residual, p, (double *)qReal->data, 7, length, lb, ub,  
            10000,NULL, info, NULL,(double *)covarianceMatrix->data,(void *)useful);

    finalResidual = getResidual(p,(double *)qReal->data, 7, length, (void *)useful);

    // the fit gets stored in p, so we can get rid of useful
    free(useful);

    if (status <= 0) { 
        // When unsuccessful operation, return None
        printf(" - Status = %d\n",status);
        PyErr_SetString(PyExc_Exception,"Fit unsuccessful.");
        return 0;
    }

    // the reason I have to do the N is described at 
    // http://mail.python.org/pipermail/python-list/2002-October/167549.html
    return Py_BuildValue("dddddddNddi",p[0],p[1],p[2],p[3],p[4],p[5],p[6],covarianceMatrix,
            initialResidual,finalResidual,(int)info[6]);
    // return the data to the user
}
 

static PyMethodDef FitWrap_methods[] = {
    {"getPeak",FitWrap_getPeak,METH_VARARGS,""},
    {"fitCalibrationParameters",FitWrap_fitCalibrationParameters,METH_VARARGS,""},
    {NULL,NULL}
};
    

void initFitWrap(void) {
	PyObject *m;
    import_array();
	m = Py_InitModule("FitWrap", FitWrap_methods); 
}

