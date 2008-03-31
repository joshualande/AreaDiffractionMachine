"""
    Below are Functions for converting (x,y) values back and forth to (Q,chi) values.
    These rely on the theory of geometric transforms. Note that chi is in inputted
    and outputted in degrees!

    You need to pass getXY() and getQChi() a calibration Data full of experimental 
    parameters.  Here, I am setting the parameters of a particular experiment. You
    can optionally pass these function a bunch of sins and cosines of alpha and beta.
    This is nice if you are going to call these functions many times so that you can
    save the trig values and only calculate them once.

        >>> import CalibrationData
        >>> calibrationData = CalibrationData.CalibrationData()
        >>> center = 1725
        >>> calibrationData.setCenterX(center)
        >>> calibrationData.setCenterY(center)
        >>> calibrationData.setDistance(125.296)
        >>> calibrationData.setWavelength(.97354)
        >>> calibrationData.setAlpha(0)
        >>> calibrationData.setBeta(0)
        >>> calibrationData.setRotation(0)
        >>> calibrationData.setPixelLength(100)
        >>> calibrationData.setPixelHeight(100)

    geMaxQ() will print out the maximum Q value (for a given wavelength).

        >>> print "%.10f" % getMaxQ(calibrationData)
        9.1272735340

    geMaxWavelenth() will print out the maximum Q value (for a given Q).

        >>> print "%.7f" % getMaxWavelength(9.1272735340)
        0.9735400

    Now, do the transform:
    
        >>> (Q,chi) = getQChi(calibrationData,1725,1725)
        >>> print "%.5f" % Q
        0.00000
        >>> print "%.5f" % chi
        0.00000
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        1725.00000,1725.00000
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi,
        ...     math.cos(calibrationData.getBeta()['val']*math.pi/180.),
        ...     math.sin(calibrationData.getBeta()['val']*math.pi/180.), 
        ...     math.cos(calibrationData.getAlpha()['val']*math.pi/180.),
        ...     math.sin(calibrationData.getAlpha()['val']*math.pi/180.),
        ...     math.cos(calibrationData.getRotation()['val']*math.pi/180.),
        ...     math.sin(calibrationData.getRotation()['val']*math.pi/180.) )
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        1725.00000,1725.00000

    Functions should undo each other:

        >>> calibrationData.setAlpha(1)
        >>> calibrationData.setAlpha(.5)
        >>> (Q,chi) = getQChi(calibrationData,3000,2000)
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        3000.00000,2000.00000

    Test them undoing each other again...

        >>> calibrationData.setAlpha(1)
        >>> calibrationData.setAlpha(.5)
        >>> calibrationData.setDistance(1000)
        >>> calibrationData.setWavelength(10)
        >>> print "%.10f" % getMaxQ(calibrationData)
        0.8885765876
        >>> print "%.7f" % getMaxWavelength(0.8885765876)
        10.0000000
        >>> calibrationData.setPixelLength(1)
        >>> calibrationData.setPixelHeight(10000)
        >>> (Q,chi) = getQChi(calibrationData,30000,2)
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        30000.00000,2.00000


    Below, I will test doing the inverting for coordinates in all 4 quadrants for
    x,y pairs and for chi values where chi points in all 4 quadrants. The reason
    that I do this is to make sure that all the inverse tangent functions actually
    invert to the correct quadrants. I was earlier having problems doing this.
    
    Here, I am testing an x,y pair in the 3rd quadrant:

        >>> (Q,chi) = getQChi(calibrationData,-30000,-2)
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        -30000.00000,-2.00000

    And again. Here, I am testing an x,y pair in the 2nd quadrant:

        >>> (Q,chi) = getQChi(calibrationData,-30000,2)
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        -30000.00000,2.00000

    And again. Here, I am testing an x,y pair in the 4th quadrant:

        >>> (Q,chi) = getQChi(calibrationData,30000,-2)
        >>> (xPixel,yPixel)=getXY(calibrationData,Q,chi)
        >>> print "%.5f,%.5f" % (xPixel,yPixel)
        30000.00000,-2.00000

    And again. Here, I am testing a Q,chi pair with chi between 0 and 90
    
        >>> # Now, test going the other way
        >>> (xPixel,yPixel)=getXY(calibrationData,0.8,80)
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.80000,80.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel,
        ...     math.cos(calibrationData.getBeta()['val']*math.pi/180.), 
        ...     math.sin(calibrationData.getBeta()['val']*math.pi/180.),
        ...     math.cos(calibrationData.getAlpha()['val']*math.pi/180.), 
        ...     math.sin(calibrationData.getAlpha()['val']*math.pi/180.),
        ...     math.cos(calibrationData.getRotation()['val']*math.pi/180.), 
        ...     math.sin(calibrationData.getRotation()['val']*math.pi/180.) )
        >>> print "%.5f,%.5f" % (Q,chi)
        0.80000,80.00000

    And again. Here, I am testing a Q,chi pair with chi between 90 and 180

        >>> (xPixel,yPixel)=getXY(calibrationData,0.51,155.5)
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.51000,155.50000

    And again. Here, I am testing a Q,chi pair with chi between 180 and 270

        >>> (xPixel,yPixel)=getXY(calibrationData,0.501,255.5)
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50100,255.50000

    And again. Here, I am testing a Q,chi pair with chi between 270 and 360

        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,311.1)
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,311.10000

    Here, I am testing with a chi of 0, 90, 180, 270, and 360. I was having trouble
    earilier getting these to transform. It should work now :)

        >>> calibrationData.setAlpha(0)
        >>> calibrationData.setBeta(0)

    Test chi=0

        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,0)
        >>> print "%.5f" % (yPixel-center)
        0.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,0.00000

    Test chi=90

        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,90)
        >>> print "%.5f" % (xPixel-center)
        0.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,90.00000

    Test chi=180

        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,180)
        >>> print "%.5f" % (yPixel-center)
        0.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,180.00000

    Test chi=270
        
        >>> from math import pi
        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,270)
        >>> print "%.5f" % (xPixel-center)
        0.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,270.00000

    Test chi=360

        >>> (xPixel,yPixel)=getXY(calibrationData,0.5001,360)
        >>> print "%.5f" % (yPixel-center)
        0.00000
        >>> (Q,chi) = getQChi(calibrationData,xPixel,yPixel)
        >>> print "%.5f,%.5f" % (Q,chi)
        0.50010,0.00000
"""
import math
import DiffractionAnalysisWrap


def convertEnergyToWavelength(energy):
    return DiffractionAnalysisWrap.convertEnergyToWavelength(energy)


def convertWavelengthToEnergy(wavelength):
    return DiffractionAnalysisWrap.convertWavelengthToEnergy(wavelength)


def convertTwoThetaToQ(twoTheta,calibrationData):
    """ Calculates Q when given twoTheta and the wavelength. """
    wav= calibrationData.getWavelength()['val']
    return DiffractionAnalysisWrap.convertTwoThetaToQ(twoTheta,wav)


def convertQToTwoTheta(Q,calibrationData):
    """ Calculates twoTheta when given Q and the wavelength. """
    return DiffractionAnalysisWrap.convertQToTwoTheta(Q,
            calibrationData.getWavelength()['val'])

def getMaxTwoTheta():
    """ This is a stupid function, but it adds a nice 
        symmetry to the GetMaxQ function. """
    return 90

def getMaxQ(calibrationData):
    """ Max Q happens when 2_theta = pi/2. This,
        Qmax = 4*pi*sin(pi/4)/wavelength """
    return getMaxQ_UGLY(calibrationData.getWavelength()['val'] )


def getMaxQ_UGLY(wavelength):
    return 4*math.pi*math.sin(math.pi/4.0)/wavelength

def getMaxWavelength(Q):
    """ Similarly, the max wavelength is the largest
        wavelength which will allow for a particular Q
        value. wavelength_max = 4*pi*sin(pi/4)/Q. """
    return 4*math.pi*math.sin(math.pi/4.0)/Q


def getQChi(calibrationData,xPixel,yPixel,cos_beta=None, 
        sin_beta=None, cos_alpha=None, sin_alpha=None, 
         cos_rotation=None, sin_rotation=None):
    """ calibrationData is a CalibrationData object holding
        the x and y center of the image in pixels, the
        distance from detector to sample, the energy of 
        the incoming photons, and the alpha and beta tilt 
        parameters of the experiment. It also holds 
        pixelLength, the physical length of one pixel in micron
        units, and pixelheight, the physical length of one pixel in
        micron units (1 mm = 1000 microns).  
        x,y are the coordinates to transform into Q and Chi values.
        Returns chi in units of degrees. """

    # call wrapped c code.
    if cos_beta == None or sin_beta == None or \
            cos_alpha == None or sin_alpha == None or \
            cos_rotation == None or sin_rotation == None:
        return DiffractionAnalysisWrap.getQChi(
                calibrationData.getCenterX()['val'],
                calibrationData.getCenterY()['val'],
                calibrationData.getDistance()['val'],
                calibrationData.getEnergy()['val'],
                calibrationData.getAlpha()['val'],
                calibrationData.getBeta()['val'],
                calibrationData.getRotation()['val'],
                xPixel,yPixel,
                calibrationData.getPixelLength()['val'],
                calibrationData.getPixelHeight()['val'])

    return DiffractionAnalysisWrap.getQChi(
            calibrationData.getCenterX()['val'],
            calibrationData.getCenterY()['val'],
            calibrationData.getDistance()['val'],
            calibrationData.getEnergy()['val'],
            calibrationData.getAlpha()['val'],
            calibrationData.getBeta()['val'],
            calibrationData.getRotation()['val'],
            xPixel,yPixel,
            calibrationData.getPixelLength()['val'],
            calibrationData.getPixelHeight()['val'],
            cos_beta,sin_beta,
            cos_alpha,sin_alpha,
            cos_rotation,sin_rotation)


def getXY(calibrationData,Q,chi,
        cos_beta=None, sin_beta=None, cos_alpha=None, sin_alpha=None,
        cos_rotation = None,sin_rotation = None):
    """ calibrationData is a CalibrationData object holding
        the x and y center of the image in pixels, the
        distance from detector to sample, the energy of 
        the incoming photons, and the alpha and beta tilt 
        parameters of the experiment. CalibrationData also
        holds the rotation angle and the pixel length and pixel 
        height in micron units (1mm = 1000 microns).
        Q and chi are the coordinates to convert to x,y pixel values.
        chi is in units of degrees. """

    # call wrapped c code.
    if cos_beta == None or sin_beta == None or \
            cos_alpha == None or sin_alpha == None or\
            cos_rotation == None or sin_rotation == None:
        return DiffractionAnalysisWrap.getXY(
                calibrationData.getCenterX()['val'],
                calibrationData.getCenterY()['val'],
                calibrationData.getDistance()['val'],
                calibrationData.getEnergy()['val'],
                calibrationData.getAlpha()['val'],
                calibrationData.getBeta()['val'],
                calibrationData.getRotation()['val'],
                Q,chi,
                calibrationData.getPixelLength()['val'],
                calibrationData.getPixelHeight()['val'])

    return DiffractionAnalysisWrap.getXY(
            calibrationData.getCenterX()['val'],
            calibrationData.getCenterY()['val'],
            calibrationData.getDistance()['val'],
            calibrationData.getEnergy()['val'],
            calibrationData.getAlpha()['val'],
            calibrationData.getBeta()['val'],
            calibrationData.getRotation()['val'],
            Q,chi,
            calibrationData.getPixelLength()['val'],
            calibrationData.getPixelHeight()['val'],
            cos_beta,sin_beta,
            cos_alpha,sin_alpha,
            cos_rotation,sin_rotation)


def test():
    import doctest
    import Transform
    doctest.testmod(Transform,verbose=1)
        
if __name__ == "__main__":
    test()
