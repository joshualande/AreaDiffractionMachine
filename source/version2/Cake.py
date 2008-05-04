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
    qOrTwoThetaLower,qOrTwoThetaUpper,numQOrTwoTheta=None,None,None
    chiLower,chiUpper,numChi=None,None,None

    def __init__(self,diffractionData,calibrationData,
            qOrTwoThetaLower,qOrTwoThetaUpper,numQOrTwoTheta,
            chiLower,chiUpper,numChi,doPolarizationCorrection,P,
            maskedPixelInfo,type):

        self.cake(diffractionData,calibrationData,qOrTwoThetaLower,
                qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,
                numChi,doPolarizationCorrection,P,maskedPixelInfo,type)

    def getData(self):
        return self.cakeData

    def cake(self,diffractionData,calibrationData,qOrTwoThetaLower,
            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,numChi,
            doPolarizationCorrection,P,maskedPixelInfo,type):

        if chiLower >= chiUpper:
            raise Exception("Unable to cake. The lower chi value must be \
less then the upper chi value.")

        if (chiUpper - chiLower) > 360:
            raise Exception("The chi values must have a range no larger \
then 360 degrees.")

        if type == 'Q':
            if qOrTwoThetaLower >= qOrTwoThetaUpper:
                raise Exception("Unable to cake. The lower Q value must be \
less then the upper Q value")

            if qOrTwoThetaLower < 0: 
                raise Exception("Unable to cake. The lower Q value must be \
larger then 0.")

            if qOrTwoThetaUpper > Transform.getMaxQ(calibrationData):
                raise Exception("Unable to cake. The upper Q value must be \
less then the largest possible Q value.")

            if numQOrTwoTheta < 1:
                raise Exception("Unable to cake. The number of Q must be at \
least 1.")

        elif type == '2theta':
            if qOrTwoThetaLower >= qOrTwoThetaUpper:
                raise Exception("Unable to cake. The lower 2theta value must \
be less then the upper 2theta value")

            if qOrTwoThetaLower < 0: 
                raise Exception("Unable to cake. The lower 2theta value must \
be larger then 0.")

            if qOrTwoThetaUpper > Transform.getMaxTwoTheta():
                raise Exception("Unable to cake. The upper 2theta value must \
be smaller then 90.")

            if numQOrTwoTheta < 1:
                raise Exception("Unable to cake. The number of 2theta must \
be at least 1.")
        else:
            raise Exception("Unable to cake. The function must be passed \
for the parameter type either 'Q', or '2theta'")


        if maskedPixelInfo.doLessThanMask:
            lessThanMask = maskedPixelInfo.lessThanMask
        else:
            # We can just send the function a bunch of junk since 
            # it won't be used
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
                qOrTwoThetaLower, qOrTwoThetaUpper,
                numQOrTwoTheta,
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
                calibrationData.getPixelHeight()['val'],
                type)

        # store the values for later
        self.qOrTwoThetaLower=qOrTwoThetaLower
        self.qOrTwoThetaUpper=qOrTwoThetaUpper
        self.numQOrTwoTheta=numQOrTwoTheta 
        self.chiLower=chiLower
        self.chiUpper=chiUpper
        self.numChi=numChi
        self.doPolarizationCorrection=doPolarizationCorrection
        self.P=P
        self.type = type

        # We should make a shallow copy so that the widget dose
        # not get copied over. Nevertheless, all the stuff we 
        # care about are single values so they will get really copied over
        self.maskedPixelInfo = copy.copy(maskedPixelInfo)

        self.calibrationData = copy.deepcopy(calibrationData)
        self.diffractionData = diffractionData


    def getImage(self,lowerBound,upperBound,logScale,
            colorMaps,colorMapName,invert):
        mode = "RGB"

        if self.maskedPixelInfo.doLessThanMask:
            (lessThanMaskColorR,lessThanMaskColorG, \
                    lessThanMaskColorB) = \
                    self.maskedPixelInfo.getLessThanMaskColorRGB()
        else:
            # We can just send the function a bunch 
            # of junk since it won't be used
            (lessThanMaskColorR,lessThanMaskColorG, \
                    lessThanMaskColorB) = (0,0,0) 

        if self.maskedPixelInfo.doGreaterThanMask:
            (greaterThanMaskColorR,greaterThanMaskColorG, \
                    greaterThanMaskColorB) = \
                    self.maskedPixelInfo.getGreaterThanMaskColorRGB()
        else:
            (greaterThanMaskColorR,greaterThanMaskColorG, \
                    greaterThanMaskColorB) = (0,0,0)

        if self.maskedPixelInfo.doPolygonMask:
            (polygonMaskColorR,polygonMaskColorG, \
                    polygonMaskColorB) = \
                    self.maskedPixelInfo.getPolygonMaskColorRGB()
        else:
            (polygonMaskColorR,polygonMaskColorG, \
                    polygonMaskColorB) = (0,0,0) 


        palette = colorMaps.getPalette(colorMapName, \
                invert=invert)

        string = DrawWrap.getCakeImageString(
                self.cakeData,
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

        img = Image.fromstring(mode,(self.cakeData.shape[1],
                self.cakeData.shape[0]),string)

        return img


    def toFile(self,filename,diffractionDataName):
        """ Saves cake data to a file. """

        file = open(filename,'w')

        # I am not exactly sure why the last 2 numbers 
        # would ever not be 1. But I am trying to stick 
        # to convention.
        file.write("# Cake of: %s \n" % diffractionDataName)
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
            file.write("#   Greater than mask = %f\n" % \
                    self.maskedPixelInfo.greaterThanMask)
        else:
            file.write("# No greater than mask was applied\n")

        if self.maskedPixelInfo.doLessThanMask:
            file.write("# A Less Than Mask was applied\n")
            file.write("#   Less than mask = %f\n" % \
                    self.maskedPixelInfo.lessThanMask)
        else:
            file.write("# No less than mask was applied\n")

        if self.maskedPixelInfo.doPolygonMask and \
                self.maskedPixelInfo.numPolygons() > 0:

            file.write("# Polygon mask(s) were applied\n")  
            file.write(self.maskedPixelInfo.writePolygonCommentString())
        else:
            file.write("# No polygon masks were applied\n")

        file.write("# Cake range:\n")
        if self.type == "Q":
            file.write("#   Q Lower = %f\n" % \
                    self.qOrTwoThetaLower)
            file.write("#   Q Upper = %f\n" % \
                    self.qOrTwoThetaUpper)
            file.write("#   Number of Q = %f\n" % \
                    self.numQOrTwoTheta)
            file.write("#   Q Step = %f\n" % \
                    ((self.qOrTwoThetaUpper-self.qOrTwoThetaLower)/ \
                    self.numQOrTwoTheta))
        elif self.type == "2theta":
            file.write("#   2theta Lower = %f\n" % \
                    self.qOrTwoThetaLower)
            file.write("#   2theta Upper = %f\n" % \
                    self.qOrTwoThetaUpper)
            file.write("#   number of 2theta = %f\n" % \
                    self.numQOrTwoTheta)
            file.write("#   2theta Step = %f\n" % \
                    ((self.qOrTwoThetaUpper-self.qOrTwoThetaLower)/ \
                    self.numQOrTwoTheta))
        else:
            raise Exception("Unable to save cake data to a file. \
The function must be passed for the parameter type either 'Q',  \
or '2theta'")

        file.write("#   chi Lower = %f\n" % self.chiLower)
        file.write("#   chi Upper = %f\n" % self.chiUpper)
        file.write("#   Number of Chi = %f\n" % self.numChi)
        file.write("#   chi Step = %f\n" % \
                ((self.chiUpper-self.chiLower)/self.numChi))
        file.write("# Note: pixels outside the diffraction \
image are saved as -1\n");

        if self.maskedPixelInfo.doGreaterThanMask:
            file.write("#   Pixels greater than the greater \
than mask are saved as -2\n")

        if self.maskedPixelInfo.doLessThanMask:
            file.write("#   Pixels less than the less than \
mask are saved as -3\n")

        if self.maskedPixelInfo.doPolygonMask and \
                self.maskedPixelInfo.numPolygons() > 0:
            file.write("#   Pixels inside of a polygon masks \
are saved as -4\n")  

        if self.type == "Q":
            file.write("# chi increased down. Q increases \
to the right\n")

        elif self.type == "2theta":
            file.write("# chi increased down. 2theta \
increases to the right\n")

        for chiLoop in range(self.numChi):
            for qOrTwoThetaLoop in range(self.numQOrTwoTheta):
                val = '%17.10E    ' % \
                        self.cakeData[chiLoop][qOrTwoThetaLoop]
                file.write(val)
            if chiLoop!= self.numChi-1:
                file.write('\n')
        file.close()


def addConstantQLineCakeImage(image,Q,qOrTwoThetaLower,
        qOrTwoThetaUpper,numQOrTwoTheta,chiLower,
        chiUpper,numChi,color,calibrationData,type):

    draw = ImageDraw.Draw(image)

    if type == "Q":
        if Q < qOrTwoThetaLower or Q > qOrTwoThetaUpper:
            return

        qIndex = (numQOrTwoTheta-1)*(Q-qOrTwoThetaLower)/ \
                (qOrTwoThetaUpper-qOrTwoThetaLower)

        draw.line( (qIndex,0)+(qIndex,numChi-1),fill=color)
    
    elif type == "2theta":
        twoTheta = Transform.convertQToTwoTheta(Q,calibrationData)
        if twoTheta < qOrTwoThetaLower or \
                twoTheta > qOrTwoThetaUpper:
            return

        twoThetaIndex = (numQOrTwoTheta-1)* \
                (twoTheta-qOrTwoThetaLower)/ \
                (qOrTwoThetaUpper-qOrTwoThetaLower)

        draw.line( (twoThetaIndex,0)+(twoThetaIndex,numChi-1),
                fill=color)
        
    else:
        raise Exception("Unable to add constant Q \
lines to the cake image. The function must be passed \
for the parameter type either 'Q', or '2theta'")


def addPeaksCakeImage(image,qOrTwoThetaLower,
        qOrTwoThetaUpper,numQOrTwoTheta,chiLower,
        chiUpper,numChi,peakList,calibrationData,
        color,smallestRangeQOrTwoThetaLower,
        smallestRangeQOrTwoThetaUpper,
        smallestRangeChiLower,smallestRangeChiUpper,
        maskedPixelInfo,type):

    draw = ImageDraw.Draw(image)

    unZoomWidth = 2.5
    # scale the length of the xs. For example, zoomed 
    # in to 50% means will cause the xs to be drawn 
    # with double the length.
    numTimesZoomInQOrTwoTheta = \
            abs((smallestRangeQOrTwoThetaUpper - \
            smallestRangeQOrTwoThetaLower)/ \
            (qOrTwoThetaUpper-qOrTwoThetaLower))

    numTimesZoomInChi = abs((smallestRangeChiUpper-\
            smallestRangeChiLower)/(chiUpper-chiLower))

    scalingFactor = min(numTimesZoomInQOrTwoTheta,
            numTimesZoomInChi)

    halflength = unZoomWidth*scalingFactor

    for x,y,qReal,qFit,chi,width in \
            peakList.getMaskedPeakList(maskedPixelInfo):
        
        # for each peak, we want to take the true 
        # x,y value of where the peak is on the 
        # image and figure out where it belongs on 
        # the cake data.
        qTemp,chiTemp = Transform.getQChi(calibrationData,x,y)

        # if our chi range begins in the negative, 
        # we might have to place our chi values 
        # in their 360 degree rotated values. Note 
        # that getQChi always returns chi between 
        # 0 and 360
        if (chiTemp-360) > chiLower and \
                (chiTemp-360) < chiUpper:
                chiTemp -= 360
            
        if type == "Q":    
            cakeX = (numQOrTwoTheta-1)*(qTemp-qOrTwoThetaLower)/ \
                    (qOrTwoThetaUpper-qOrTwoThetaLower)
        elif type == '2theta':
            twoThetaTemp = Transform.convertQToTwoTheta(
                    qTemp,calibrationData)
            cakeX = (numQOrTwoTheta-1)* \
                    (twoThetaTemp-qOrTwoThetaLower)/ \
                    (qOrTwoThetaUpper-qOrTwoThetaLower)
        else:
            raise Exception("Unable to add peak to the cake \
image. The function must be passed for the parameter type \
either 'Q', or '2theta'")

        cakeY = (numChi-1)*(chiTemp-chiLower)/(chiUpper-chiLower)

        # add in new lines if they would be visible
        if cakeX >= 0 and cakeX < numQOrTwoTheta and  \
                cakeY >= 0 and cakeY < numChi:

            draw.line( (cakeX-halflength,cakeY-halflength) +
                    (cakeX+halflength,cakeY+halflength),fill=color)

            draw.line( (cakeX+halflength,cakeY-halflength) +
                    (cakeX-halflength,cakeY+halflength),fill=color)


