#include <stdio.h>
#include <math.h>

#include "Python.h"
#include "Numeric/arrayobject.h"

#define PI 3.14159265358979323846


// below is code to do the transformations with the rotation


double mod(double a, double b) {
    while (a < 0) a+=b;
    while (a >= b) a-=b;
    return a;
}


/*
 * This is just the same as for convertWavelengthToEnergy but in reverse.
 */
double convertEnergyToWavelength(double energy) {
    return 12398.4172/energy;
}


/*
 * Wavelength is given in units of angrstrom. Energy is in units of eV.
 * Wavelengths are converted into energy units. 
 * From Google: (Planck's constant * the speed of light)/(electron volt * angstrom) = 12 398.4172
 * Thus, (when we realize that wavelength input is in units of angstrom), we see that
 * E = hc/wavelength = 12,398.4172 eV*angstrom/(wavelength*angstrom)  = 12,398.4172/wavelength (in units of eV, as desired)
 * So our formula for energy is E=12398.4172/wavelength. The units get taken care of properly!
 */
double convertWavelengthToEnergy(double wavelength) {
    return 12398.4172/wavelength;
}


/*
 * Use the famous Q=4*pi*sin(2theta/2)/lambda formula
 */
double convertTwoThetaToQ(double twoTheta,double wavelength) {
    // convert twoTheta from degrees to radians first
    return 4.0*PI*sin( (twoTheta*PI/180.0) /2.0)/wavelength;
}


double convertQToTwoTheta(double Q, double wavelength) {
    // convert twoTheta to degrees before returning
    return 2.0*asin(Q*wavelength/(4*PI))*180.0/PI;
}


/*
 * This transformation is done using Josh's equations derived
 * in the software manual. The notation in the manual 
 * corresponds to the variable names by:
 *   xMeasured = x'''
 *   yMeasured = y'''
 *   xPhysical = x_d
 *   yPhysical = y_d
 */
void getTwoThetaChi(double xCenter,double yCenter,
        double distance,double xPixel,double yPixel,
        double pixelLength,double pixelHeight,
        double rotation,double cos_beta,double sin_beta,
        double cos_alpha,double sin_alpha,
        double cos_rotation,double sin_rotation,
        double *twoTheta,double *chi) {

    double pixelLength_mm,pixelHeight_mm;
    double xMeasured,yMeasured;
    double bottom;
    double xPhysical,yPhysical;

    // pixellength comes in in units of micron
    // We convert pixelLength & pixelHeight into mm units so 
    // that they are comparable with distance (in units of 
    //  millimeters)
    pixelLength_mm = pixelLength/1000.0;
    pixelHeight_mm = pixelHeight/1000.0;
    
    xMeasured = (xPixel-xCenter)*pixelLength_mm;
    yMeasured = (yPixel-yCenter)*pixelHeight_mm;

    bottom = distance+(xMeasured*cos_rotation+ 
            yMeasured*sin_rotation)*sin_beta+
            (-xMeasured*sin_rotation+
            yMeasured*cos_rotation)*sin_alpha*cos_beta;
    
    // calculate the x y coordinates on the imaginary 
    // detector using fancy math
    xPhysical = distance*((xMeasured*cos_rotation+
            yMeasured*sin_rotation)*cos_beta
            -(-xMeasured*sin_rotation+
            yMeasured*cos_rotation)*sin_alpha)/bottom;

    yPhysical = distance*(-xMeasured*sin_rotation+
            yMeasured*cos_rotation)*cos_alpha/bottom;

    *twoTheta = atan2(sqrt(xPhysical*xPhysical+
            yPhysical*yPhysical),distance);
    // Convert to radians
    *twoTheta = *twoTheta * 180.0/PI;

    // explicitly convert chi to degrees
    *chi=atan2(yPhysical,xPhysical)*180.0/PI;
    
    // then add rotation to it so that chi always points 
    // to the right. Also, we have to multiply chi by -1 
    // because we have been defining our angles the inverse 
    // of the way they should be. There is a probably a 
    // better way to do this if I really thought through 
    // exactly how chi is defined. For the moment, through, 
    // this does exactly the right thing.
    *chi = (*chi + rotation)*(-1);

    // make sure that chi is b/n 0 and 360
    *chi = mod(*chi, 360.0);
}


void getQChi(double xCenter,double yCenter,double distance,
        double energy,double xPixel,double yPixel,
        double pixelLength,double pixelHeight,
        double rotation,double cos_beta,double sin_beta,
        double cos_alpha,double sin_alpha,
        double cos_rotation,double sin_rotation,
        double *q,double *chi) {

    double wavelength;
    double twoTheta;
    wavelength = 12398.4172/energy;

    getTwoThetaChi(xCenter,yCenter,distance,xPixel,yPixel,
        pixelLength,pixelHeight,rotation,cos_beta,sin_beta, 
        cos_alpha,sin_alpha,cos_rotation,sin_rotation,
        &twoTheta,chi); 

    *q=convertTwoThetaToQ(twoTheta,wavelength);
}


/*
 * This transformation is done using Josh's equations derived
 * in the software manual. The notation in the manual 
 * corresponds to the variable names by:
 *   xMeasured = x'''
 *   yMeasured = y'''
 *   xPhysical = x_d
 *   yPhysical = y_d
 */
void getXY(double xCenter,double yCenter,double distance,
        double energy,double q,double chi,double pixelLength,
        double pixelHeight,double rotation,double cos_beta,
        double sin_beta,double cos_alpha,double sin_alpha,
        double cos_rotation,double sin_rotation,
        double * xPixel,double * yPixel) {

    double wavelength;
    double twoTheta;
    double xPhysical,yPhysical;
    double bottom;
    double pixelLength_mm,pixelHeight_mm;
    double xMeasured,yMeasured;

    double tan_chi;

    wavelength = 12398.4172/energy;

    // rotate chi back to point whatever way it is supposed 
    // to point
    chi = chi*(-1) - rotation;

    chi = mod(chi, 360.0);
    
    // explicitly convert chi to radians
    chi*=PI/180.0;

    twoTheta = 2.0*asin(wavelength*q/(4.0*PI));

    tan_chi = tan(chi);
    xPhysical = fabs(distance*tan(twoTheta)/sqrt(1.0+
            tan_chi*tan_chi));

    // one must determine explicitly the sign of xPhysical 
    // by inspecting the diagram. This is b/c at one point 
    // we take a sqrt in our derivation.
    if (chi>PI/2.0 && chi<3.0*PI/2.0) 
        xPhysical = -1.0*xPhysical;

    yPhysical=fabs(xPhysical*tan_chi);

    // set the sign of y explicitly
    if (chi > PI && chi < 2.0*PI)
        yPhysical = -1.0*fabs(yPhysical);

    // I should worry about cos_alpha being 0
    bottom = distance*cos_beta-xPhysical*sin_beta-
            cos_beta*(xPhysical*cos_beta+distance)/(
            (xPhysical*cos_alpha)/(yPhysical*sin_alpha)+1);

    xMeasured = (distance*xPhysical*cos_rotation-
            distance*xPhysical*cos_beta*sin_rotation/
            (xPhysical*cos_alpha/yPhysical+sin_alpha))/
            bottom;

    yMeasured = (distance*xPhysical*sin_rotation+ 
            distance*xPhysical*cos_beta*cos_rotation/
            (xPhysical*cos_alpha/yPhysical+sin_alpha))/
            bottom;

    // convert pixelLength & pixelHeight into mm units so 
    // that they are comparable with distance (in units of 
    // millimeters)
    pixelLength_mm = pixelLength/1000.0;
    pixelHeight_mm = pixelHeight/1000.0;

    *xPixel = xMeasured/pixelLength_mm + xCenter;
    *yPixel = yMeasured/pixelHeight_mm + yCenter;
}



