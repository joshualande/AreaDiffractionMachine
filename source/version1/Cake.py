import Transform 
import DiffractionAnalysisWrap
import DrawWrap
import time
import Numeric

import Image
import ImageDraw
import copy

class Cake:
    cakeData=None
    qLower,qUpper,numQ=None,None,None
    chiLower,chiUpper,numChi=None,None,None

    def __init__(self,diffractionData,calibrationData,qLower,qUpper,numQ,
            chiLower,chiUpper,numChi,doPolarizationCorrection,P,
            maskedPixelInfo):

        self.cake(diffractionData,calibrationData,qLower,qUpper,numQ,
            chiLower,chiUpper,numChi,doPolarizationCorrection,P,
            maskedPixelInfo)

    def getData(self):
        return self.cakeData

    def cake(self,diffractionData,calibrationData,qLower,qUpper,numQ,
            chiLower,chiUpper,numChi,doPolarizationCorrection,P,
            maskedPixelInfo):

        if chiLower >= chiUpper:
            raise Exception("Unable to cake. The lower chi value must be less then the upper chi value.")

        if (chiUpper - chiLower) > 360:
            raise Exception("The chi values must have a range no larger then 360 degrees.")

        if qLower >= qUpper:
            raise Exception("Unable to cake. The lower q value must be less then the upper q value.")

        if qLower < 0: 
            raise Exception("Unable to cake. The lower q value must be larger then 0.")

        if qUpper > Transform.getMaxQ(calibrationData):
            raise Exception("Unable to cake. The upper q value must be less then the largest possible Q value.")


        if maskedPixelInfo.doLessThanMask:
            lessThanMask = maskedPixelInfo.lessThanMask
        else:
            # We can just send the function a bunch of junk since it won't be used
            lessThanMask = -1

        if maskedPixelInfo.doGreaterThanMask:
            greaterThanMask = maskedPixelInfo.greaterThanMask
        else:
            greaterThanMask = -1

        if maskedPixelInfo.doPolygonMask:
            polygonsX = maskedPixelInfo.polygonsX
            polygonsY = maskedPixelInfo.polygonsY
            polygonBeginningsIndex = maskedPixelInfo.polygonBeginningsIndex
            polygonNumberOfItems = maskedPixelInfo.polygonNumberOfItems
        else:
            polygonsX = Numeric.array([])
            polygonsY = Numeric.array([])
            polygonBeginningsIndex = Numeric.array([])
            polygonNumberOfItems = Numeric.array([])


        # use the wraped C code to do the caking
        self.cakeData = DiffractionAnalysisWrap.cake(
                diffractionData,
                calibrationData.getCenterX()['val'],
                calibrationData.getCenterY()['val'],
                calibrationData.getDistance()['val'],
                calibrationData.getEnergy()['val'],
                calibrationData.getAlpha()['val'], 
                calibrationData.getBeta()['val'],
                calibrationData.getRotation()['val'],
                qLower, qUpper,
                numQ,
                chiLower, chiUpper,
                numChi,
                doPolarizationCorrection, P,
                maskedPixelInfo.doGreaterThanMask, greaterThanMask,
                maskedPixelInfo.doLessThanMask, lessThanMask,
                maskedPixelInfo.doPolygonMask,
                polygonsX, polygonsY,
                polygonBeginningsIndex,
                polygonNumberOfItems,
                calibrationData.getPixelLength()['val'],
                calibrationData.getPixelHeight()['val'])

        if type(self.cakeData) == type(None):
            raise Exception("Error occured while caking the data.")

        # store the values for later
        self.qLower=qLower
        self.qUpper=qUpper
        self.numQ=numQ
        self.chiLower=chiLower
        self.chiUpper=chiUpper
        self.numChi=numChi
        self.doPolarizationCorrection=doPolarizationCorrection
        self.P=P

        # We should make a shallow copy so that the widget dose
        # not get copied over. Nevertheless, all the stuff we 
        # care about are single values so they will get really copied over
        self.maskedPixelInfo = copy.copy(maskedPixelInfo)

        self.calibrationData = copy.deepcopy(calibrationData)
        self.diffractionData = diffractionData


    def getImage(self,lowerBound,upperBound,logScale,colorMaps,colorMapName,invert):
        mode = "RGB"

        if self.maskedPixelInfo.doLessThanMask:
            (lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB) = \
                    self.maskedPixelInfo.getLessThanMaskColorRGB()
        else:
            # We can just send the function a bunch of junk since it won't be used
            (lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB) = (0,0,0) 

        if self.maskedPixelInfo.doGreaterThanMask:
            (greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB) = \
                    self.maskedPixelInfo.getGreaterThanMaskColorRGB()
        else:
            (greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB) = (0,0,0)

        if self.maskedPixelInfo.doPolygonMask:
            (polygonMaskColorR,polygonMaskColorG,polygonMaskColorB) = \
                    self.maskedPixelInfo.getPolygonMaskColorRGB()
        else:
            (polygonMaskColorR,polygonMaskColorG,polygonMaskColorB) = (0,0,0) 


        palette = colorMaps.getPalette(colorMapName,invert=invert)

        string = DrawWrap.getCakeImageString(self.cakeData,
                self.diffractionData,
                lowerBound,
                upperBound,
                logScale,
                palette,
                self.maskedPixelInfo.doLessThanMask,
                self.maskedPixelInfo.lessThanMask, 
                lessThanMaskColorR, 
                lessThanMaskColorG,lessThanMaskColorB, 
                self.maskedPixelInfo.doGreaterThanMask,
                self.maskedPixelInfo.greaterThanMask, 
                greaterThanMaskColorR,
                greaterThanMaskColorG, 
                greaterThanMaskColorB,
                self.maskedPixelInfo.doPolygonMask,
                polygonMaskColorR,
                polygonMaskColorG,
                polygonMaskColorB)

        img = Image.fromstring(mode,(self.cakeData.shape[1],self.cakeData.shape[0]),string)

        return img


    def toFile(self,filename,diffractionDataName):
        """ Saves cake data to a file. """

        file = open(filename,'w')

        # I am not exactly sure why the last 2 numbers would ever not be 1
        # But I am trying to stick to convention.
        file.write("# Cake of %s\n" % (diffractionDataName) )
        file.write("# Data Caked on "+time.asctime()+"\n")
        file.write("# Calibration data used to make the cake:\n")
        self.calibrationData.writeCommentString(file)

        if self.doPolarizationCorrection:
            file.write("# A Polarization correction was applied\n")
            file.write("#   P = %f\n" % self.P)
        else:
            file.write("# No polarization correction was applied\n")

        if self.maskedPixelInfo.doGreaterThanMask:
            file.write("# A greater than mask was applied\n")
            file.write("#   Greater than mask = %f\n" % self.maskedPixelInfo.greaterThanMask)
        else:
            file.write("# No greater than mask was applied\n")

        if self.maskedPixelInfo.doLessThanMask:
            file.write("# A Less Than Mask was applied\n")
            file.write("#   Less than mask = %f\n" % self.maskedPixelInfo.lessThanMask)
        else:
            file.write("# No less than mask was applied\n")

        if self.maskedPixelInfo.doPolygonMask and self.maskedPixelInfo.numPolygons() > 0:
            file.write("# Polygon mask(s) were applied\n")  
            file.write(self.maskedPixelInfo.writePolygonCommentString())
        else:
            file.write("# No polygon masks were applied\n")

        file.write("# Cake range:\n")
        file.write("#   qLower = %f\n" % self.qLower)
        file.write("#   qUpper = %f\n" % self.qUpper)
        file.write("#   numQ = %f\n" % self.numQ)
        file.write("#   qStep = %f\n" % ( (self.qUpper-self.qLower)/self.numQ) )

        file.write("#   chiLower = %f\n" % self.chiLower)
        file.write("#   chiUpper = %f\n" % self.chiUpper)
        file.write("#   numChi = %f\n" % self.numChi)
        file.write("#   chiStep = %f\n" % ( (self.chiUpper-self.chiLower)/self.numChi) )
        file.write("# Note: pixels outside the diffraction image are saved as -1\n");

        if self.maskedPixelInfo.doGreaterThanMask:
            file.write("#   Pixels greater than the greater than mask are saved as -2\n")

        if self.maskedPixelInfo.doLessThanMask:
            file.write("#   Pixels less than the less than mask are saved as -3\n")

        if self.maskedPixelInfo.doPolygonMask and self.maskedPixelInfo.numPolygons() > 0:
            file.write("#   Pixels inside of a polygon masks are saved as -4\n")  

        file.write("# chi increased down. Q increases to the right\n")

        for chiLoop in range(self.numChi):
            for qLoop in range(self.numQ):
                val = '%17.8E' % self.cakeData[chiLoop][qLoop]
                file.write(val)
            if chiLoop!= self.numChi-1:
                file.write('\n')
        file.close()


def addConstantQLineCakeImage(image,Q,qLower,qUpper,numQ,chiLower,
        chiUpper,numChi,color):

    draw = ImageDraw.Draw(image)

    if Q < qLower or Q > qUpper:
        return

    qIndex = (numQ-1)*(Q-qLower)/(qUpper-qLower)

    draw.line( (qIndex,0)+(qIndex,numChi-1),fill=color)


def addPeaksCakeImage(image,qLower,qUpper,numQ,chiLower,chiUpper,
        numChi,peakList,calibrationData,color,
        smallestRangeQLower,smallestRangeQUpper,smallestRangeChiLower,smallestRangeChiUpper):

    draw = ImageDraw.Draw(image)

    unZoomWidth = 2.5
    # scale the length of the xs. For example, zoomed in to 50% means will 
    # cause the xs to be drawn with double the length.
    numTimesZoomInQ = abs((smallestRangeQUpper-smallestRangeQLower)/ \
            (qUpper-qLower))

    numTimesZoomInChi = abs((smallestRangeChiUpper-smallestRangeChiLower)/ \
            (chiUpper-chiLower))

    scalingFactor = min(numTimesZoomInQ,numTimesZoomInChi)

    halflength = unZoomWidth*scalingFactor

    for x,y,qReal,qFit,chi,width in peakList:
        
        # for each peak, we want to take the true x,y value of
        # where the peak is on the image and figure out where
        # it belongs on the cake data.
        qTemp,chiTemp = Transform.getQChi(calibrationData,x,y)

        # if our chi range begins in the negative, we might have to place 
        # our chi values in their 360 degree rotated values. Note that
        # getQChi always returns chi between 0 and 360
        if (chiTemp-360) > chiLower and \
                (chiTemp-360) < chiUpper:
                chiTemp -= 360
            
        cakeX = (numQ-1)*(qTemp-qLower)/(qUpper-qLower)
        cakeY = (numChi-1)*(chiTemp-chiLower)/(chiUpper-chiLower)

        # add in new lines if they would be visible
        if cakeX >= 0 and cakeX < numQ and  \
                cakeY >= 0 and cakeY < numChi:

            draw.line( (cakeX-halflength,cakeY-halflength) +
                    (cakeX+halflength,cakeY+halflength),fill=color)

            draw.line( (cakeX+halflength,cakeY-halflength) +
                    (cakeX-halflength,cakeY+halflength),fill=color)


