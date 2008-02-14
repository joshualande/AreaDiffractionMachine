import os
import copy
import Numeric
import PIL
import Image
import string
import math
import time

# imports that I wrote below
import MakeDiffractionImage
import CalibrationData
import QData
import Fit
from Cake import Cake
from IntegrateIntensity import IntegrateIntensity
import ColorMaps
import MarXXXX
import MarCCD
import Tiff
import Transform
import DiffractionAnalysisWrap 
from Exceptions import UnknownFiletypeException, UserInputException


# This is here for other objects to refer to
allExtensions = ['.mccd','.mar2300','.tiff','.tif','.mar3450']


class DiffractionData:
    """ An object for dealing with x-ray diffraction data.
	    This object should have methods for dealing with reading
	    in and analyzing x-ray diffraction data. 

            >>> ON_LINUX = 1

        This is how you call DiffractionData

            >>> if ON_LINUX:
            ...     object = DiffractionData("/home/jolande/data/LaB6_14_02_56.mar3450")     
            ... else:
            ...     object = DiffractionData("S:\work\Data\LaB6\LaB6_14_02_56.mar3450")

        There are getter objects to get stuff from the header file.

            >>> object.getSize()
            3450
            >>> object.getHeaderPixelLength()
            100.0
            >>> object.getHeaderPixelHeight()
            100.0
            >>> print '%.10f' % object.getHeaderWavelength()
            0.9735400000
            >>> print '%.10f' % object.getHeaderDistance()
            125.2960000000
            >>> print '%.10f' % object.getHeaderCenterX()
            1725.0000000000
            >>> print '%.10f' % object.getHeaderCenterY()
            1725.0000000000
          
        A calibrationData object stores the parameters of an experment.
        calibrationDataFromHeader() will pull this data out of the header
        of the diffraction file and return an object with the data in it.

            >>> calibrationData = object.calibrationDataFromHeader()
            >>> print "%.10f" % calibrationData.getCenterX()['val']
            1725.0000000000
            >>> print "%.10f" % calibrationData.getCenterY()['val']
            1725.0000000000
            >>> print "%.10f" % calibrationData.getDistance()['val']
            125.2960000000
            >>> print "%.10f" % calibrationData.getWavelength()['val']
            0.9735400000

        Alpha and beta are not set by calibrationDataFromHeader() usually

            >>> print "%.10f" % calibrationData.getPixelLength()['val']
            100.0000000000
            >>> print "%.10f" % calibrationData.getPixelHeight()['val']
            100.0000000000

        getPixeLValue() will return the acutal value at a particular x,y pixel

            >>> object.getPixelValue(1,1)
            0 
            >>> from ColorMaps import ColorMaps
            >>> maps = ColorMaps('colormaps.txt')
            >>> map = 'bone'
            >>> import tempfile
            >>> filename = tempfile.mktemp() + '.jpg'
            >>> object.saveDiffractionImage(filename,maps,map)
            >>> filename = tempfile.mktemp() + '.png'
            >>> object.saveDiffractionImage(filename,maps,map)


        """

    theDiffractionData = None
    theImage = None

    # store previous values for drawing image
    lastLowerBoundDiffractionImage = None
    lastUpperBoundDiffractionImage = None
    lastLogScaleDiffractionImage = None
    lastColorMapNameDiffractionImage = None

    lastCalibrationDataGetSmallsetRange = None
    lastRangeGetSmallestRange = None

    lastMaskedPixelInfo = None

    def __init__(self,filename,extension = None):
        """ Does everything to initialize the object. 
            Either you can pass in the type of file that you are using
            by explicitly giving its extension, or the program can try
            to figure this out for you. If filename is a list, all of the
            files will be opened and added together, but only if they
            are the same type of file. """

        if type(filename) == type([]): 
            # if a list is given, read all files
            filenames = filename # explicitly SAy many files are given

            if extension == None:

                extensions = []
                for file in filenames:
                    split = os.path.basename(file).split('.')
                    if len(split)>0:
                        extension = split[-1]
                    extensions.append(extension.lower())

                for extension in extensions:
                    if extension != extensions[0]:
                        raise UnknownFiletypeException("Cannot read in multiple files because they do not have the same extension")

                extension = extensions[0] # Only one extension to store

            allData = []
            for file in filenames:
                if extension in ["mar2300", "mar3450"]:
                    allData.append(MarXXXX.MarXXXX(file))
                elif extension == "mccd":
                    allData.append(MarCCD.MarCCD(file))
                elif extension in ["tiff", "tif"]:
                    allData.append(Tiff.Tiff(file))
                else:
                    raise UnknownFiletypeException("%s is an unknown filetype" % file)

            for data in allData:
                if data.size != allData[0].size:
                    raise UserInputException("Cannot add files because they are of different size.")

            filename = ""
            # store all filenames in one string
            for data in allData:
                filename = filename + " " + data.filename

            self.theDiffractionData = allData.pop() # store all iamges in one

            # add all the data together
            for data in allData:
                self.theDiffractionData.data += data.data

        else: # otherwise, only given one file so do the regular thing

            if extension == None:
                split = os.path.basename(filename).split('.')
                if len(split)>0:
                    extension = split[-1]

            extension = extension.lower()

            if extension in ["mar2300", "mar3450"]:
                self.theDiffractionData = MarXXXX.MarXXXX(filename)
            elif extension == "mccd":
                self.theDiffractionData = MarCCD.MarCCD(filename)
            elif extension in ["tiff", "tif"]:
                self.theDiffractionData = Tiff.Tiff(filename)
            else:
                raise UnknownFiletypeException("%s is an unknown filetype" % filename)


    def saveDiffractionImage(self,filename,colorMaps,colorMapName,
            maskedPixelInfo,
            pixel1X=None,pixel1Y=None, pixel2X=None, pixel2Y=None, 
            lowerBound=0, upperBound=1, logScale = None, invert = None, 
            drawQLines=None,drawdQLines=None,QData=None,calibrationData=None,
            drawPeaks=None,peakList=None, qLinesColor = None, dQLinesColor = None,
            peakLinesColor = None):

        image = self.getDiffractionImage(colorMaps,colorMapName,
                maskedPixelInfo,
                None,None,None,None,None,None,
                lowerBound,upperBound,logScale,invert)
 

        if drawQLines or drawdQLines:
            if QData == None:
                raise Exception("Cannot save the diffraction data until a q list is given.")
            if calibrationData == None:
                raise Exception("Cannot save the diffraction data until the calibration Data is given.")

            if drawQLines:
                if qLinesColor == None:
                    raise Exception('Cannot add q lines to the saved image until the q line color is set.')
                for Q,dQ in QData.getAllQPairs():
                    MakeDiffractionImage.addConstantQLineDiffractionImage(image,Q,
                            calibrationData,qLinesColor)

            if drawdQLines:
                if dQLinesColor == None:
                    raise Exception('Cannot add delta q lines to the saved image until the delta q line color is set.')
                for Q,dQ in QData.getAllQPairs():
                    MakeDiffractionImage.addConstantQLineDiffractionImage(image,Q-dQ,
                            calibrationData,dQLinesColor)
                    MakeDiffractionImage.addConstantQLineDiffractionImage(image,Q+dQ,
                            calibrationData,dQLinesColor)

        if drawPeaks and peakList != None:
            if peakLinesColor == None:
                raise Exception("Cannot  add peaks to the saved iamge until the peak color is set.")

            MakeDiffractionImage.addPeaksDiffractionImage(image,peakList,peakLinesColor)


        # by default, return entire image
        if pixel1X != None and pixel1Y != None and pixel2X != None and pixel2Y !=None:
            image = image.crop((min(pixel1X,pixel2X), min(pixel1Y,pixel2Y), 
                    max(pixel1X,pixel2X), max(pixel1Y,pixel2Y)))

        try:
            image.save(filename)
        except Exception,e:
            raise UserInputException("Cannot save image: %s has an unknown file extension" % filename )
     

    def getDiffractionImage(self,colorMaps,colorMapName,maskedPixelInfo,
            pixel1X=None,pixel1Y=None,pixel2X=None, pixel2Y=None, width = None, height = None, 
            lowerBound=0, upperBound=1, logScale = 0,invert=None):

        # only create new image if it hasn't been made yet or if any
        # of the intensity bounds or if the log scale has changed,
        # or if some of the pixel masking parameters have changed
        if self.theImage == None or \
                self.lastLowerBoundDiffractionImage != lowerBound or \
                self.lastUpperBoundDiffractionImage != upperBound or \
                self.lastLogScaleDiffractionImage != logScale or \
                colorMapName != self.lastColorMapNameDiffractionImage or \
                invert != self.lastInvert or \
                maskedPixelInfo != self.lastMaskedPixelInfo:

            self.theImage = MakeDiffractionImage.getDiffractionImage(self.theDiffractionData.data,
                    lowerBound=lowerBound,
                    upperBound=upperBound,
                    logScale = logScale,
                    colorMaps = colorMaps,
                    colorMapName=colorMapName,
                    invert=invert, 
                    maskedPixelInfo = maskedPixelInfo)

            self.lastLowerBoundDiffractionImage=lowerBound
            self.lastUpperBoundDiffractionImage=upperBound
            self.lastLogScaleDiffractionImage = logScale
            self.lastColorMapNameDiffractionImage = colorMapName
            self.lastInvert = invert
    
            # only do a shallow copy because the weird widget in the object can't be copied
            self.lastMaskedPixelInfo = copy.copy(maskedPixelInfo)

        # by default, return entire image
        if pixel1X==None or pixel1Y==None or pixel2X==None or pixel2Y==None:
            if width==None or height==None:
                return self.theImage
            return self.theImage.resize( (width, height), Image.BILINEAR )

        temp = self.theImage.crop( (
                min(pixel1X,pixel2X), min(pixel1Y,pixel2Y), 
                max(pixel1X,pixel2X) ,max(pixel1Y,pixel2Y)) )
        if width != None and height != None:
            temp = temp.resize( (width, height), Image.BILINEAR )
        return temp


    def getSize(self): 
        """ Returns x or y size of the image. """
        return self.theDiffractionData.size


    def getHeaderPixelLength(self): 
        """ Returns the PIXEL LENGTH value read from the 
            diffraction file. PIXEL LENGTH is the size 
            of one pixel in micron units. """
        return self.theDiffractionData.headerPixelLength


    def getHeaderPixelHeight(self): 
        """ Returns the PIXEL HEIGHT value read from the 
            diffraction file. PIXEL HEIGHT is the size 
            of one pixel in micron units. """
        return self.theDiffractionData.headerPixelHeight


    def getHeaderWavelength(self): 
        """ Returns the WAVELENGTH value read from the 
            diffraction file. WAVELENGTH is the wavelength
            used during the experiment as measured in 
            Angstroems. """
        return self.theDiffractionData.headerWavelength


    def getHeaderDistance(self): 
        return self.theDiffractionData.headerDistance


    def getHeaderCenterX(self): 
        return self.theDiffractionData.headerCenterX


    def getHeaderCenterY(self): 
        return self.theDiffractionData.headerCenterY


    def getPixelValue(self,x,y):
        return self.theDiffractionData.data[x][y]

    def getPixelValueBilinearInterpolation(self,x,y):
        if x<0 or x>self.theDiffractionData.size or \
                y<0 or y>self.theDiffractionData.size:
            raise Exception("Cannot calculate the intensity outside of the image.\n")

        return DiffractionAnalysisWrap.bilinearInterpolation(self.theDiffractionData.data,x,y)


    def calibrationDataFromHeader(self):
        """ This function takes all of the necessary 
            data form the header file to create a 
            CalibrationData object. The CalibreationData 
            object with this information is
            what is returend. This function is supposed to 
            be more of a convenience than anything else. 
            Since the header file dose not have any 
            sort of imformation on the amout of tilt of 
            the CCD that was used to take the picture, the 
            two tilt angles are arbitrarily set to 0 (no tilt). 
            This function does not set alpha, beta, or the 
            rotation angle because that data is not stored in 
            any header data. """
        data = CalibrationData.CalibrationData()
        if self.getHeaderCenterX() != None:
            data.setCenterX(self.getHeaderCenterX())
        if self.getHeaderCenterY() != None:
            data.setCenterY(self.getHeaderCenterY())
        if self.getHeaderDistance() != None:
            data.setDistance(self.getHeaderDistance())
        if self.getHeaderWavelength() != None:
            data.setWavelength(self.getHeaderWavelength())
        if self.getHeaderPixelLength() != None:
            data.setPixelLength(self.getHeaderPixelLength())
        if self.getHeaderPixelHeight() != None:
            data.setPixelHeight(self.getHeaderPixelHeight())

        if self.getHeaderCenterX() != None and \
                self.getHeaderCenterY() != None and \
                self.getHeaderDistance() != None and \
                self.getHeaderWavelength() != None and \
                self.getHeaderPixelLength() != None and \
                self.getHeaderPixelHeight() != None:
            data.setAlpha(0)
            data.setBeta(0)
            data.setRotation(0)

        return data


    def fit(self,initialGuess,qData,numberOfChi=None,stddev=None,peakList=None):
        if (numberOfChi==None and peakList==None):
            raise Exception("Cannot fit the calibration data unless either the number of chi values or a peak list are given.")

        # make peak list
        if peakList == None:
            peakList = Fit.getPeakList(self.theDiffractionData.data,qData,
                    initialGuess,numberOfChi,stddev)

        # do fitting
        return Fit.fit(self.theDiffractionData.data,
                initialGuess,peakList)


    def savePeakListToFile(self,filename,initialGuess,qData,numberOfChi,stddev):
        peakList = Fit.getPeakList(self.theDiffractionData.data,qData,
                initialGuess,numberOfChi,stddev)

        # now, save to file
        file = open(filename,'w')
        file.write("# A list of peaks found in the diffraction image.\n")
        file.write("# Calculated on "+time.asctime()+"\n")
        file.write("# Calibration data used to find peaks:\n")
        initialGuess.writeCommentString(file)
        file.write("#\tx\ty\tRealQ\tFitQ\tchi\twidth\tintensity\t2theta\n")
        for peak in peakList:
            x,y,realQ,fitQ,chi,width = peak
            
            intensity=self.getPixelValueBilinearInterpolation(x,y)
            twoTheta = Transform.convertQToTwoTheta(fitQ,initialGuess)
            file.write("%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n" % \
                    (x,y,realQ,fitQ,chi,width,intensity,twoTheta) )
        file.close()
        return peakList


    def saveCakeImage(self, filename, calibrationData, 
            qLower, qUpper, numQ, chiLower, chiUpper,numChi,
            doPolarizationCorrection,P,maskedPixelInfo,
            colorMaps, colorMapName, lowerBound, upperBound, logScale = None,
            invert = None, drawQLines = None, drawdQLines = None, 
            QData = None, drawPeaks = None, peakList = None,
            qLinesColor = None, dQLinesColor = None, 
            peakLinesColor = None):

        image = self.getCakeImage(
                calibrationData = calibrationData,
                qLower = qLower,
                qUpper = qUpper,
                numQ = numQ,
                chiLower = chiLower,
                chiUpper = chiUpper,
                numChi = numChi,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                maskedPixelInfo = maskedPixelInfo,
                width = None,
                height = None,
                colorMaps = colorMaps,
                colorMapName = colorMapName,
                lowerBound = lowerBound,
                upperBound = upperBound,
                logScale = logScale,
                invert = invert)

        if drawQLines or drawdQLines:
            if QData == None:
                raise Exception("Cannot save the cake data until a q list is given.")

            if drawQLines:
                if qLinesColor == None:
                    raise Exception('Cannot add q lines to the saved image until the q line color is set.')
                for Q,dQ in QData.getAllQPairs():
                    Cake.addConstantQLineCakeImage(image,Q,qLower,qUpper,numQ,chiLower,chiUpper,numChi,qLinesColor)

            if drawdQLines:
                if dQLinesColor == None:
                    raise Exception('Cannot add delta q lines to the saved image until the delta q line color is set.')
                for Q,dQ in QData.getAllQPairs():
                    Cake.addConstantQLineCakeImage(image,Q-dQ,qLower,qUpper,numQ,chiLower,chiUpper,numChi,dQLinesColor)
                    Cake.addConstantQLineCakeImage(image,Q+dQ,qLower,qUpper,numQ,chiLower,chiUpper,numChi,dQLinesColor)

        if drawPeaks and peakList != None:
            if peakLinesColor == None:
                raise Exception("Cannot  add peaks to the saved iamge until the peak color is set.")

            smallest  = self.getSmallestRange(calibrationData)

            Cake.addPeaksCakeImage(image,qLower,qUpper,numQ,chiLower,chiUpper,numChi,
                    peakList,calibrationData,peakLinesColor,
                    smallestRangeQLower = smallest['qLower'],
                    smallestRangeQUpper = smallest['qUpper'],
                    smallestRangeChiLower =  smallest['chiLower'],
                    smallestRangeChiUpper =  smallest['chiUpper'])
        try:
            image.save(filename)
        except Exception,e:
            raise UserInputException("Cannot save the cake: %s has an unknown file extension" % filename )


    def saveCakeData(self,filename,calibrationData,qLower,
            qUpper,numQ,chiLower,chiUpper,numChi,doPolarizationCorrection,P,maskedPixelInfo):

        data = Cake(diffractionData = self.theDiffractionData.data,
                calibrationData = calibrationData,
                qLower = qLower,
                qUpper = qUpper,
                numQ = numQ,
                chiLower = chiLower,
                chiUpper = chiUpper,
                numChi = numChi,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                maskedPixelInfo = maskedPixelInfo)

        data.toFile(filename,self.theDiffractionData.filename)


    def getCakeImage(self,calibrationData,qLower,qUpper,numQ,chiLower,
            chiUpper,numChi,doPolarizationCorrection,P,maskedPixelInfo,
            width,height,colorMaps,colorMapName,
            lowerBound,upperBound,logScale=None,invert=None):

        data = Cake(self.theDiffractionData.data,calibrationData,
            qLower,qUpper,numQ,chiLower,chiUpper,numChi,doPolarizationCorrection,P,
            maskedPixelInfo)

        image = data.getImage(lowerBound,upperBound,logScale,colorMaps,colorMapName,invert)

        # change width and height of image
        if width==None or height==None:
            return image
        return image.resize( (width, height), Image.BILINEAR )


    def integrateQI(self,calibrationData,lower,upper,num,constraintLower,
            constraintUpper,doConstraint,doPolarizationCorrection,P,typeOfConstraint,
            maskedPixelInfo):
        return IntegrateIntensity(diffractionData = self.theDiffractionData.data,
                calibrationData = calibrationData,
                lower = lower,
                upper = upper,
                num = num,
                constraintLower = constraintLower,
                constraintUpper = constraintUpper,
                doConstraint = doConstraint,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                typeOfIntegration = 'Q',
                typeOfConstraint = typeOfConstraint,
                maskedPixelInfo = maskedPixelInfo)


    def integrate2ThetaI(self,calibrationData,lower,upper,num,constraintLower,
            constraintUpper,doConstraint,doPolarizationCorrection,P,
            typeOfConstraint,maskedPixelInfo):
        return IntegrateIntensity(diffractionData = self.theDiffractionData.data,
                calibrationData = calibrationData,
                lower = lower,
                upper = upper,
                num = num,
                constraintLower = constraintLower,
                constraintUpper = constraintUpper,
                doConstraint = doConstraint,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                typeOfIntegration = '2theta',
                typeOfConstraint = typeOfConstraint,
                maskedPixelInfo = maskedPixelInfo)

    def integrateChiI(self,calibrationData,lower,upper,num,constraintLower,
            constraintUpper,doConstraint,doPolarizationCorrection,P,
            typeOfConstraint,maskedPixelInfo):
        return IntegrateIntensity(diffractionData = self.theDiffractionData.data,
                calibrationData = calibrationData,
                lower = lower,
                upper = upper,
                num = num,
                constraintLower = constraintLower,
                constraintUpper = constraintUpper,
                doConstraint = doConstraint,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                typeOfIntegration = 'chi',
                typeOfConstraint = typeOfConstraint,
                maskedPixelInfo = maskedPixelInfo)


    def getSmallestRange(self,calibrationData):
        """ Get Smallest Range picks the smallest 
            range in the image which contains
            the whole diffraction image. 

            If the center of the beam is inside the 
            diffraction data, we know that there will
            be some of all chi so chi should very 
            from -180 to 180. Furthermore, we
            know that Q will vary from 0 to its max 
            which will be on a corner. So
            in that case, we can just look in the 
            corners to find the largets Q value.

            If the center of the image is ouside the 
            diffraction data, that all we know is
            that the extremum will be somewhere on 
            the edge of the image. In that case, we 
            have to loop through the entire border 
            to find the extremum
        """

        # check if it has already been calculated

        if self.lastCalibrationDataGetSmallsetRange != None:
            if calibrationData == self.lastCalibrationDataGetSmallsetRange:
                return self.lastRangeGetSmallestRange
            else:
                self.lastCalibrationDataGetSmallsetRange = None
                self.lastRangeGetSmallestRange = None

        # store value in case it changes.
        self.lastCalibrationDataGetSmallsetRange = copy.deepcopy(calibrationData)
            
        if calibrationData.getCenterX()['val'] < 0 or \
            calibrationData.getCenterX()['val']  > self.theDiffractionData.size-1 or \
            calibrationData.getCenterY()['val'] < 0 or \
            calibrationData.getCenterY()['val']  > self.theDiffractionData.size-1:

            qLower = None
            qUpper = None
            chiLower = None
            chiUpper = None

            for temp in range(self.theDiffractionData.size):
                # go around each edge of the image, finding the most extreme q and chi values
                q0,chi0 = Transform.getQChi(calibrationData,0,temp)
                q1,chi1 = Transform.getQChi(calibrationData,self.theDiffractionData.size-1,temp)
                q2,chi2 = Transform.getQChi(calibrationData,temp,0)
                q3,chi3 = Transform.getQChi(calibrationData,temp,self.theDiffractionData.size-1)

                lowerQ = min(q0,q1,q2,q3)
                higherQ = max(q0,q1,q2,q3)
                if qLower==None or lowerQ < qLower: qLower = lowerQ
                if qUpper==None or higherQ > qUpper: qUpper = higherQ

                if chi0 > 180: chi0 -=360
                if chi1 > 180: chi1 -=360
                if chi2 > 180: chi2 -=360
                if chi3 > 180: chi3 -=360

                lowerChi = min(chi0,chi1,chi2,chi3)
                higherChi = max(chi0,chi1,chi2,chi3)

                if chiLower==None or lowerChi < chiLower: chiLower = lowerChi
                if chiUpper==None or higherChi > chiUpper: chiUpper = higherChi

            tempRange = {'qLower':qLower,'qUpper':qUpper,'chiLower':chiLower,'chiUpper':chiUpper}
            self.lastRangeGetSmallestRange = tempRange
            return tempRange

        else:
            q0,chi0 = Transform.getQChi(calibrationData,0,0)
            q1,chi1 = Transform.getQChi(calibrationData,0,self.theDiffractionData.size-1)
            q2,chi2 = Transform.getQChi(calibrationData,self.theDiffractionData.size-1,0)
            q3,chi3 = Transform.getQChi(calibrationData,self.theDiffractionData.size-1,
                    self.theDiffractionData.size-1)

            qUpper = max(q0,q1,q2,q3)
            qUpper = float(str(qUpper)[:8])

            tempRange = {'qLower':0,'qUpper':qUpper,'chiLower':-180,'chiUpper':180}
            self.lastRangeGetSmallestRange = tempRange
            return tempRange


def test():
    import doctest
    import DiffractionData
    doctest.testmod(DiffractionData,verbose=0)
        
if __name__ == "__main__":
    test()
 
