""" CODE WILL GET A DIVISION BY 0 when you take a chi slice going certain ways
    ERROR AND NOT DO THE RIGHT THING. I NEED to write a more robust algorithm
    For the time being, just don't do any chi slices exactly up or over. """

from math import floor,ceil,pi,sqrt
import tempfile
import os
import Numeric

import copy
from random import Random
import CalibrationData
import Transform
from General import frange
import FitWrap
import PeakList
from Exceptions import UserInputException



def fit(data,initialGuess,peakList,maskedPixelInfo,verbose=1):

    print 
    print 'Performing the image calibration'

    # create nice Numeric data structures to store all of 
    # the peak stuff in. This lets us read our data easily 
    # once we get into C
    xValues,yValues,qReal,chi,width,intensity = peakList.getMaskedPeakArrays(maskedPixelInfo,data)

    # make C do the hard work :)
    centerX,centerY,distance,energy,alpha,beta,rotation,covariance = FitWrap.fitCalibrationParameters(
            xValues,yValues,qReal,intensity,
            initialGuess.getCenterX()['val'],
            initialGuess.getCenterX()['fixed'],
            initialGuess.getCenterY()['val'],
            initialGuess.getCenterY()['fixed'],
            initialGuess.getDistance()['val'],
            initialGuess.getDistance()['fixed'],
            initialGuess.getEnergy()['val'],
            initialGuess.getEnergy()['fixed'],
            initialGuess.getAlpha()['val'],
            initialGuess.getAlpha()['fixed'],
            initialGuess.getBeta()['val'],
            initialGuess.getBeta()['fixed'],
            initialGuess.getRotation()['val'],
            initialGuess.getRotation()['fixed'],
            initialGuess.getPixelLength()['val'],
            initialGuess.getPixelHeight()['val'])

    print 'Covariance Matrix'
    print Numeric.array2string(covariance,precision=2)
    print 'Root of the diagonal of the covariance matrix (I think these are uncertainties)'
    print 'xc: ',sqrt(covariance[0][0])
    print 'yc: ',sqrt(covariance[1][1])
    print 'd: ',sqrt(covariance[2][2])
    print 'E: ',sqrt(covariance[3][3])
    print 'alpha: ',sqrt(covariance[4][4])
    print 'beta: ',sqrt(covariance[5][5])
    print 'rotation: ',sqrt(covariance[6][6])


    # add the fit data to a new calibration file
    ret = CalibrationData.CalibrationData() 
    ret.setCenterX(centerX, fixed = initialGuess.getCenterX()['fixed'] )
    ret.setCenterY(centerY, fixed = initialGuess.getCenterY()['fixed'] )
    ret.setDistance(distance, fixed = initialGuess.getDistance()['fixed'] )
    ret.setEnergy(energy, fixed = initialGuess.getEnergy()['fixed'] )
    ret.setAlpha(alpha, fixed = initialGuess.getAlpha()['fixed'] )
    ret.setBeta(beta, fixed = initialGuess.getBeta()['fixed'] )
    ret.setRotation(rotation, fixed = initialGuess.getRotation()['fixed'] )
    # pixel length & height don't change
    ret.setPixelLength(initialGuess.getPixelLength()['val'])
    ret.setPixelHeight(initialGuess.getPixelHeight()['val'])

    return ret,peakList


def getPeakList(data,qData,initialGuess,numberOfChi,stddev,verbose=1):

    if numberOfChi <=1:
        raise Exception("This program must look for at least 2 chi slices.")
    chiUpper = 360.0
    chiLower = 0.11
    # the -1 allows for us to include chiLower & chiUpper in our count
    chiStep = (chiUpper-chiLower)*1.0/(numberOfChi-1)

    peakList = PeakList.PeakList()
    print 'len = ',len(peakList.peakList)

    if verbose: print ' - %d total Q values. Calculating peaks for Q =' % (len(qData.getAllQPairs())),
    for Q,dQ in qData.getAllQPairs():
        if verbose: print ' %f' % Q,

        for chi in frange(chiLower,chiUpper,chiStep):
            try:
                x,y,qFit,width=FitWrap.getPeak(data,stddev,initialGuess.getCenterX()['val'],
                        initialGuess.getCenterY()['val'],initialGuess.getDistance()['val'],
                        initialGuess.getEnergy()['val'],initialGuess.getAlpha()['val'],
                        initialGuess.getBeta()['val'],initialGuess.getRotation()['val'],Q-dQ,Q+dQ,chi,
                        initialGuess.getPixelLength()['val'],initialGuess.getPixelHeight()['val'])

                peakList.addPeak(x,y,Q,qFit,chi,width)

            except ValueError: # this means no peak found
                pass

    print 
    return peakList
    
