import os
import copy
import Numeric
import PIL
import Image
import string
from math import sqrt
import time

# imports that I wrote below
import MakeDiffractionImage
import CalibrationData
import QData
import Fit

# Note that I need to call functions from inside of Cake
# so I can't do a from Cake import Cake because then
# it will be ambiguous whether I would be calling a 
# function from the file Cake or a function that
# the object Cake has
import Cake
from IntegrateIntensity import IntegrateIntensity
from General import getextension
import ColorMaps
import MarXXXX
import MarCCD
import ESRF
import Bruker
from EdfFile import EdfFile
import Tiff
import Transform
import DiffractionAnalysisWrap 
from Exceptions import UnknownFiletypeException, UserInputException


# This is here for other objects to refer to
allExtensions = [".mccd",".mar2300",".edf",".tiff",".tif",".mar3450",".sfrm",".gfrm"]


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
          
        A calibrationData object stores the parameters of an experiment.
        calibrationDataFromHeader() will pull this data out of the header
        of the diffraction file and return an object with the data in it.

            >>> calibrationData = object.calibrationDataFromHeader()
            >>> print "%.10f" % calibrationData.getCenterX()["val"]
            1725.0000000000
            >>> print "%.10f" % calibrationData.getCenterY()["val"]
            1725.0000000000
            >>> print "%.10f" % calibrationData.getDistance()["val"]
            125.2960000000
            >>> print "%.10f" % calibrationData.getWavelength()["val"]
            0.9735400000

        Alpha and beta are not set by calibrationDataFromHeader() usually

            >>> print "%.10f" % calibrationData.getPixelLength()["val"]
            100.0000000000
            >>> print "%.10f" % calibrationData.getPixelHeight()["val"]
            100.0000000000

        getPixeLValue() will return the acutal value at a particular x,y pixel

            >>> object.getPixelValue(1,1)
            0 
            >>> from ColorMaps import ColorMaps
            >>> maps = ColorMaps("colormaps.txt")
            >>> map = "bone"
            >>> import tempfile
            >>> filename = tempfile.mktemp() + ".jpg"
            >>> object.saveDiffractionImage(filename,maps,map)
            >>> filename = tempfile.mktemp() + ".png"
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
    lastTypeGetSmallestRange = None

    lastMaskedPixelInfo = None

    lastFitString = None

    lastDoScaleFactor = None
    lastScaleFactor = None
    lastSetMinMax = None
    lastMinIntensity = None
    lastMaxIntensity = None

    def __init__(self,filenames,extension = None):
        """ Does everything to initialize the object. 
            Either you can pass in the type of file that you are using
            by explicitly giving its extension, or the program can try
            to figure this out for you. Filenames must be a list of all of the
            files that will be opened and added together. If the list 
            only has one file in it, then only that one will be loaded. """

        if len(filenames) < 1:
            raise Exception("Cannot initialize a DiffractionData \
object without being given at least one file to load in.")

        if len(filenames) > 1:
            # Many files to load

            if extension == None:

                extensions = []
                for file in filenames:
                    split = os.path.basename(file).split(".")
                    if len(split)>0:
                        extension = split[-1]
                    extensions.append(extension.lower())

                for extension in extensions:
                    if extension != extensions[0]:
                        raise UnknownFiletypeException("Cannot \
read in multiple files because they do not have the same extension")

                extension = extensions[0] # Only one extension to store

            allData = []
            for file in filenames:
                if extension in ["mar2300", "mar3450"]:
                    allData.append(MarXXXX.MarXXXX(file))
                elif extension == "mccd":
                    allData.append(MarCCD.MarCCD(file))
                elif extension == "edf":
                    allData.append(ESRF.ESRF(file))
                elif extension in ["tiff", "tif"]:
                    allData.append(Tiff.Tiff(file))
                elif extension in ["sfrm","gfrm"]:
                    allData.append(Bruker.Bruker(file))
                else:
                    raise UnknownFiletypeException("%s is an unknown file \
type" % file)

            for data in allData:
                if data.size != allData[0].size:
                    raise UserInputException("Cannot add files because \
they are of different size.")

            filename = ""
            # store all filenames in one string
            for index in range(len(allData)):
                filename += allData[index].filename.strip() + " "

            self.theDiffractionData = allData.pop() # store all images in one

            # add all the data together
            for data in allData:
                self.theDiffractionData.data += data.data

            # store the merged filename for later
            self.theDiffractionData.filename = filename

        else: 
            # Only one file to load

            filename = filenames[0] # get out the only file

            if extension == None:
                split = os.path.basename(filename).split(".")
                if len(split)>0:
                    extension = split[-1]

            extension = extension.lower()

            if extension in ["mar2300", "mar3450"]:
                self.theDiffractionData = MarXXXX.MarXXXX(filename)
            elif extension == "mccd":
                self.theDiffractionData = MarCCD.MarCCD(filename)
            elif extension == "edf":
                self.theDiffractionData = ESRF.ESRF(filename)
            elif extension in ["tiff", "tif"]:
                self.theDiffractionData = Tiff.Tiff(filename)
            elif extension in ["sfrm","gfrm"]:
                self.theDiffractionData = Bruker.Bruker(filename)
            else:
                raise UnknownFiletypeException("%s is an unknown file \
type" % filename)


    def saveDiffractionImage(self,filename,colorMaps,colorMapName,
            maskedPixelInfo,doScaleFactor,scaleFactor,setMinMax,
            minIntensity,maxIntensity,
            pixel1X=None,pixel1Y=None, pixel2X=None, pixel2Y=None, 
            lowerBound=0, upperBound=1, logScale=None, invert=None, 
            drawQLines=None,drawdQLines=None,QData=None,calibrationData=None,
            drawPeaks=None,peakList=None, qLinesColor=None, dQLinesColor=None,
            peakLinesColor=None):

        # save EDF data specially
        if getextension(filename) == ".edf":
            edf = EdfFile(filename)
            #You can write any relevant information in the dictionary.
            edf.WriteImage({"Title":"Edf file converted by the Area Diffraction Machine"},
                    Numeric.transpose(self.theDiffractionData.data),
                    DataType= "SignedInteger",
                    Append=0)
            del edf # to force file close
            return

        # otherwise, try to save it using the PIL

        image = self.getDiffractionImage(
                colorMaps=colorMaps,
                colorMapName=colorMapName,
                maskedPixelInfo=maskedPixelInfo,
                pixel1X=None,
                pixel1Y=None,
                pixel2X=None,
                pixel2Y=None,
                width=None,
                height=None,
                lowerBound=lowerBound,
                upperBound=upperBound,
                logScale=logScale,
                invert=invert,
                doScaleFactor=doScaleFactor,
                scaleFactor=scaleFactor,
                setMinMax=setMinMax,
                minIntensity=minIntensity,
                maxIntensity=maxIntensity)

        if drawQLines or drawdQLines:
            if QData == None:
                raise Exception("Cannot save the diffraction data until a Q \
list is given.")
            if calibrationData == None:
                raise Exception("Cannot save the diffraction data until the \
calibration Data is given.")

            if drawQLines:
                if qLinesColor == None:
                    raise Exception("Cannot add q lines to the saved image until \
the q line color is set.")
                for Q,dQ in QData.getAllQPairs():
                    MakeDiffractionImage.addConstantQLineDiffractionImage(image,Q,
                            calibrationData,qLinesColor)

            if drawdQLines:
                if dQLinesColor == None:
                    raise Exception("Cannot add delta Q lines to the saved image \
until the delta Q line color is set.")
                for Q,dQ in QData.getAllQPairs():
                    MakeDiffractionImage.addConstantQLineDiffractionImage(
                            image,Q-dQ,calibrationData,dQLinesColor)
                    MakeDiffractionImage.addConstantQLineDiffractionImage(
                            image,Q+dQ,calibrationData,dQLinesColor)

        if drawPeaks and peakList != None:
            if peakLinesColor == None:
                raise Exception("Cannot add peaks to the saved image until \
the peak color is set.")

            MakeDiffractionImage.addPeaksDiffractionImage(image,peakList,
                    maskedPixelInfo,peakLinesColor)

        # by default, return entire image
        if pixel1X != None and pixel1Y != None and pixel2X != None and pixel2Y !=None:
            image = image.crop((min(int(pixel1X),int(pixel2X)), 
                    min(int(pixel1Y),int(pixel2Y)), 
                    max(int(pixel1X),int(pixel2X)), 
                    max(int(pixel1Y),int(pixel2Y))))
        try:
            image.save(filename)
        except Exception,e:
            raise UserInputException("Cannot save image: %s has an unknown \
file extension" % filename )
     

    def getDiffractionImage(self,colorMaps,colorMapName,
            maskedPixelInfo,pixel1X=None,pixel1Y=None,
            pixel2X=None,pixel2Y=None,width=None,height=None,
            lowerBound=0,upperBound=1,logScale=0,invert=None,
            doScaleFactor=None,scaleFactor=None,setMinMax=None,
            minIntensity=None,maxIntensity=None):

        # only create new image if it hasn't been made yet or if any
        # of the intensity bounds or if the log scale has changed,
        # or if some of the pixel masking parameters have changed
        if self.theImage == None or \
                self.lastLowerBoundDiffractionImage != lowerBound or \
                self.lastUpperBoundDiffractionImage != upperBound or \
                self.lastLogScaleDiffractionImage != logScale or \
                colorMapName != self.lastColorMapNameDiffractionImage or \
                invert != self.lastInvert or \
                maskedPixelInfo != self.lastMaskedPixelInfo or \
                doScaleFactor != self.lastDoScaleFactor or \
                scaleFactor != self.lastScaleFactor or \
                setMinMax != self.lastSetMinMax or \
                minIntensity != self.lastMinIntensity or \
                maxIntensity != self.lastMaxIntensity:

            self.theImage = MakeDiffractionImage.getDiffractionImage(
                    self.theDiffractionData.data,
                    lowerBound=lowerBound,
                    upperBound=upperBound,
                    logScale = logScale,
                    colorMaps = colorMaps,
                    colorMapName=colorMapName,
                    invert=invert, 
                    maskedPixelInfo = maskedPixelInfo,
                    doScaleFactor=doScaleFactor,
                    scaleFactor=scaleFactor,
                    setMinMax=setMinMax,
                    minIntensity=minIntensity,
                    maxIntensity=maxIntensity)

            self.lastLowerBoundDiffractionImage=lowerBound
            self.lastUpperBoundDiffractionImage=upperBound
            self.lastLogScaleDiffractionImage = logScale
            self.lastColorMapNameDiffractionImage = colorMapName
            self.lastInvert = invert
    
            # only do a shallow copy because the weird widget 
            # in the object can't be copied
            self.lastMaskedPixelInfo = copy.copy(maskedPixelInfo)

            self.lastDoScaleFactor = doScaleFactor 
            self.lastScaleFactor = scaleFactor 
            self.lastSetMinMax = setMinMax 
            self.lastMinIntensity = minIntensity 
            self.lastMaxIntensity = maxIntensity

        # by default, return entire image
        if pixel1X==None or pixel1Y==None or pixel2X==None or pixel2Y==None:
            if width==None or height==None:
                return self.theImage
            return self.theImage.resize( (width, height), Image.BILINEAR )

        temp = self.theImage.crop((
                min(int(pixel1X),int(pixel2X)), 
                min(int(pixel1Y),int(pixel2Y)), 
                max(int(pixel1X),int(pixel2X)),
                max(int(pixel1Y),int(pixel2Y))))
        if width != None and height != None:
            temp = temp.resize((width,height),Image.BILINEAR)
        return temp


    def getSize(self): 
        """ Returns x or y size of the image. """
        return self.theDiffractionData.size


    def getPixelValue(self,x,y):
        return self.theDiffractionData.data[x][y]


    def getPixelValueBilinearInterpolation(self,x,y):
        if x<0 or x>self.theDiffractionData.size or \
                y<0 or y>self.theDiffractionData.size:
            raise Exception("Cannot calculate the intensity \
outside of the image.\n")

        return DiffractionAnalysisWrap.bilinearInterpolation(
                self.theDiffractionData.data,x,y)


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
        if self.theDiffractionData.headerCenterX != None:
            data.setCenterX(self.theDiffractionData.headerCenterX)
        if self.theDiffractionData.headerCenterY != None:
            data.setCenterY(self.theDiffractionData.headerCenterY)
        if self.theDiffractionData.headerDistance != None:
            data.setDistance(self.theDiffractionData.headerDistance)
        if self.theDiffractionData.headerWavelength != None:
            data.setWavelength(self.theDiffractionData.headerWavelength)
        if self.theDiffractionData.headerPixelLength != None:
            data.setPixelLength(self.theDiffractionData.headerPixelLength)
        if self.theDiffractionData.headerPixelHeight != None:
            data.setPixelHeight(self.theDiffractionData.headerPixelHeight)

        if self.theDiffractionData.headerCenterX != None and \
            self.theDiffractionData.headerCenterY != None and \
                self.theDiffractionData.headerDistance != None and \
                self.theDiffractionData.headerWavelength != None and \
                self.theDiffractionData.headerPixelLength != None and \
                self.theDiffractionData.headerPixelHeight != None:
            data.setAlpha(0)
            data.setBeta(0)
            data.setRotation(0)

        return data


    def fit(self,initialGuess,qData,maskedPixelInfo,
            numberOfChi=None,stddev=None,peakList=None):
        if (numberOfChi==None and peakList==None):
            raise Exception("Cannot fit the calibration data \
unless either the number of chi values or a peak list are given.")

        # make peak list
        print 
        print "Finding diffraction peaks..."
        if peakList == None:
            peakList = Fit.getPeakList(self.theDiffractionData.data,qData,
                    initialGuess,numberOfChi,stddev)

        print 
        print "Performing image calibration..."
        # do fitting

        bestGuess,peakList,covariance,initialResidual,finalResidual, \
                reasonForQuitting = Fit.fit(self.theDiffractionData.data,
                initialGuess,peakList,maskedPixelInfo)

        print " - Before fitting, the calculated residual \
per peak is ",initialResidual
        print " - After fitting, the calculated residual \
per peak is ",finalResidual
        print " - Reason for quitting the fit: %d, " % reasonForQuitting,
        if reasonForQuitting == 2:
            print "stopped by small gradient J^T e\n"
        elif reasonForQuitting == 2:
            print "stopped by small Dp\n"
        elif reasonForQuitting == 3:
            print "stopped by itmax\n"
        elif reasonForQuitting == 4:
            print "singular matrix. Restart from current p with increased \\mu\n"
        elif reasonForQuitting == 5:
            print "no further error reduction is possible. Restart with increased mu\n"
        elif reasonForQuitting == 6:
            print "stopped by small ||e||_2\n"
        else:
            print "Reason for quitting unknown\n"
        
        print "Covariance Matrix:"
        print Numeric.array2string(covariance,max_line_width=1000,precision=3)
        print
        print "Root of the diagonal of the covariance matrix (I think these are uncertainties)"
        print " - xc    %17.10f" % sqrt(covariance[0][0])
        print " - yc    %17.10f" % sqrt(covariance[1][1])
        print " - d     %17.10f" % sqrt(covariance[2][2])
        print " - E     %17.10f" % sqrt(covariance[3][3])
        print " - alpha %17.10f" % sqrt(covariance[4][4])
        print " - beta  %17.10f" % sqrt(covariance[5][5])
        print " - R     %17.10f" % sqrt(covariance[6][6])

        # create the string to save to a file (if requested)
        self.lastFitString = ""
        self.lastFitString += "Fit done of: %s\n" % self.theDiffractionData.filename
        self.lastFitString += "\n"
        self.lastFitString += "Initial Guess at calibration parameters:\n"
        self.lastFitString += str(initialGuess)
        self.lastFitString += "\n"
        self.lastFitString += "Before fitting, the calculated residual \
per peak is "+str(initialResidual)+"\n"
        self.lastFitString += "\n"
        self.lastFitString += "Refined calibration parameters:\n"
        self.lastFitString += str(bestGuess)
        self.lastFitString += "\n"
        self.lastFitString += "After fitting, the calculated residual \
per peak is "+str(finalResidual)+"\n"
        self.lastFitString += "\n"

        self.lastFitString += "Reason for quitting the fit: %d-" % reasonForQuitting
        if reasonForQuitting == 2:
            self.lastFitString += "stopped by small gradient J^T e\n"
        elif reasonForQuitting == 2:
            self.lastFitString += "stopped by small Dp\n"
        elif reasonForQuitting == 3:
            self.lastFitString += "stopped by itmax\n"
        elif reasonForQuitting == 4:
            self.lastFitString += "singular matrix. Restart from current p with increased \\mu\n"
        elif reasonForQuitting == 5:
            self.lastFitString += "no further error reduction is possible. Restart with increased mu\n"
        elif reasonForQuitting == 6:
            self.lastFitString += "stopped by small ||e||_2\n"
        else:
            self.lastFitString += "Reason for quitting unknown\n"
        
        self.lastFitString += "\n"

        self.lastFitString += "Covariance Matrix:\n"
        self.lastFitString += "%s\n" % Numeric.array2string(covariance,
                max_line_width=1000,precision=10)
        self.lastFitString += "\n"
        self.lastFitString += "Root of the diagonal of the \
covariance matrix (I think these are uncertainties)\n"
        self.lastFitString += "xc    %17.10f\n" % sqrt(covariance[0][0])
        self.lastFitString += "yc    %17.10f\n" % sqrt(covariance[1][1])
        self.lastFitString += "d     %17.10f\n" % sqrt(covariance[2][2])
        self.lastFitString += "E     %17.10f\n" % sqrt(covariance[3][3])
        self.lastFitString += "alpha %17.10f\n" % sqrt(covariance[4][4])
        self.lastFitString += "beta  %17.10f\n" % sqrt(covariance[5][5])
        self.lastFitString += "R     %17.10f\n" % sqrt(covariance[6][6])

        self.lastFitString += "\n"
        self.lastFitString += "Q Data used when calibrating:\n"
        self.lastFitString += str(qData)

        return bestGuess,peakList


    def canSaveLastFit(self):
        if self.lastFitString == None:
            return 0
        return 1


    def lastFitToFile(self,filename):
        if not self.canSaveLastFit():
            raise Exception("No previous fit was done.")

        file = open(filename,"w")
        file.write(self.lastFitString)
        file.close()
        

    def savePeakListToFile(self,filename,initialGuess,qData,
            numberOfChi,maskedPixelInfo,stddev):
        peakList = Fit.getPeakList(self.theDiffractionData.data,qData,
                initialGuess,numberOfChi,stddev)

        # now, save to file
        file = open(filename,"w")
        file.write("# A list of diffraction peaks found.\n")
        file.write("# Diffraction Data: %s\n" % self.theDiffractionData.filename)
        file.write("# Calculated on "+time.asctime()+"\n")
        file.write("# Calibration data used to find peaks:\n")
        initialGuess.writeCommentString(file)
        file.write("# Q data used to find peaks:\n")
        file.write("# Peaks:\n")
        qData.writeCommentString(file)

        if maskedPixelInfo.doPolygonMask and maskedPixelInfo.numPolygons() > 0:
            file.write("# All peaks inside of polygon mask(s) were ignored.\n")
            file.write(maskedPixelInfo.writePolygonCommentString())

        file.write("#%16s%21s%21s%21s%21s%21s%21s%21s\n" % \
                ("x","y","Real Q","Fit Q","chi","width","intensity","2theta"))
        for peak in peakList.getMaskedPeakList(maskedPixelInfo):
            x,y,realQ,fitQ,chi,width = peak
            
            intensity=self.getPixelValueBilinearInterpolation(x,y)
            twoTheta = Transform.convertQToTwoTheta(fitQ,initialGuess)
            file.write("%17.10f    %17.10f    %17.10f    %17.10f    %17.10f    %17.10f    %17.10f    %17.10f\n" % \
                    (x,y,realQ,fitQ,chi,width,intensity,twoTheta) )
        file.close()
        return peakList


    def saveCakeImage(self, filename, calibrationData, 
            qOrTwoThetaLower, qOrTwoThetaUpper, numQOrTwoTheta, 
            chiLower, chiUpper,numChi,
            doPolarizationCorrection,P,maskedPixelInfo,
            colorMaps, colorMapName, lowerBound, upperBound,type,
            doScaleFactor,
            scaleFactor,
            setMinMax,
            minIntensity,
            maxIntensity,
            logScale=None,
            invert=None, drawQOrTwoThetaLines=None, drawdQOrTwoThetaLines=None, 
            QData=None, drawPeaks=None, peakList=None,
            qOrTwoThetaLinesColor=None, dQOrTwoThetaLinesColor=None, 
            peakLinesColor=None):

        image = self.getCakeImage(
                calibrationData=calibrationData,
                qOrTwoThetaLower=qOrTwoThetaLower,
                qOrTwoThetaUpper=qOrTwoThetaUpper,
                numQOrTwoTheta=numQOrTwoTheta,
                chiLower=chiLower,
                chiUpper=chiUpper,
                numChi=numChi,
                doPolarizationCorrection=doPolarizationCorrection,
                P=P,
                maskedPixelInfo=maskedPixelInfo,
                width=None,
                height=None,
                colorMaps=colorMaps,
                colorMapName=colorMapName,
                lowerBound=lowerBound,
                upperBound=upperBound,
                logScale=logScale,
                invert=invert,
                type=type,
                doScaleFactor=doScaleFactor,
                scaleFactor=scaleFactor,
                setMinMax=setMinMax,
                minIntensity=minIntensity,
                maxIntensity=maxIntensity)

        if drawQOrTwoThetaLines or drawdQOrTwoThetaLines:
            if QData == None:
                raise Exception("Cannot save the cake data until \
a Q list is given.")

            if drawQOrTwoThetaLines:
                if qOrTwoThetaLinesColor == None:
                    raise Exception("Cannot add Q lines to the \
saved image until the Q line color is set.")
                for Q,dQ in QData.getAllQPairs():
                    Cake.addConstantQLineCakeImage(image,Q,qOrTwoThetaLower,
                            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,numChi,
                            qOrTwoThetaLinesColor,calibrationData,type)

            if drawdQOrTwoThetaLines:
                if dQOrTwoThetaLinesColor == None:
                    raise Exception("Cannot add delta QOrTwoTheta lines to the saved \
image until the delta QOrTwoTheta line color is set.")

                for Q,dQ in QData.getAllQPairs():
                    Cake.addConstantQLineCakeImage(image,Q-dQ,qOrTwoThetaLower,
                            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,
                            numChi,dQOrTwoThetaLinesColor,calibrationData,type)
                    Cake.addConstantQLineCakeImage(image,Q+dQ,qOrTwoThetaLower,
                            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,
                            numChi,dQOrTwoThetaLinesColor,calibrationData,type)

        if drawPeaks and peakList != None:
            if peakLinesColor == None:
                raise Exception("Cannot add peaks to the saved image \
until the peak color is set.")

            smallest  = self.getSmallestRange(calibrationData,type)

            Cake.addPeaksCakeImage(image,qOrTwoThetaLower,qOrTwoThetaUpper,
                    numQOrTwoTheta,chiLower,chiUpper,numChi,
                    peakList,calibrationData,peakLinesColor,
                    smallestRangeQOrTwoThetaLower = smallest["qOrTwoThetaLower"],
                    smallestRangeQOrTwoThetaUpper = smallest["qOrTwoThetaUpper"],
                    smallestRangeChiLower = smallest["chiLower"],
                    smallestRangeChiUpper = smallest["chiUpper"],
                    maskedPixelInfo = maskedPixelInfo,
                    type = type)
        try:
            image.save(filename)
        except Exception,e:
            raise UserInputException("Cannot save the cake: %s has an \
unknown file extension" % filename )


    def saveCakeData(self,filename,calibrationData,qOrTwoThetaLower,
            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,chiUpper,numChi,
            doPolarizationCorrection,P,maskedPixelInfo,type):

        data = Cake.Cake(diffractionData = self.theDiffractionData.data,
                calibrationData = calibrationData,
                qOrTwoThetaLower = qOrTwoThetaLower,
                qOrTwoThetaUpper = qOrTwoThetaUpper,
                numQOrTwoTheta = numQOrTwoTheta,
                chiLower = chiLower,
                chiUpper = chiUpper,
                numChi = numChi,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                maskedPixelInfo = maskedPixelInfo,
                type = type)

        data.toFile(filename,self.theDiffractionData.filename)


    def getCakeImage(self,calibrationData,qOrTwoThetaLower,
            qOrTwoThetaUpper,numQOrTwoTheta,chiLower,
            chiUpper,numChi,doPolarizationCorrection,P,maskedPixelInfo,
            width,height,colorMaps,colorMapName,
            lowerBound,upperBound,type,
            doScaleFactor,
            scaleFactor,
            setMinMax,minIntensity,maxIntensity,
            logScale=None,invert=None):

        data = Cake.Cake(
            diffractionData = self.theDiffractionData.data,
            calibrationData = calibrationData,
            qOrTwoThetaLower = qOrTwoThetaLower,
            qOrTwoThetaUpper = qOrTwoThetaUpper,
            numQOrTwoTheta = numQOrTwoTheta,
            chiLower = chiLower,
            chiUpper = chiUpper,
            numChi = numChi,
            doPolarizationCorrection = doPolarizationCorrection,
            P = P,
            maskedPixelInfo = maskedPixelInfo,
            type = type)

        image = data.getImage(lowerBound,upperBound,logScale,
                colorMaps,colorMapName,invert,
                doScaleFactor,
                scaleFactor,
                setMinMax,
                minIntensity,
                maxIntensity)

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
                typeOfIntegration = "Q",
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
                typeOfIntegration = "2theta",
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
                typeOfIntegration = "chi",
                typeOfConstraint = typeOfConstraint,
                maskedPixelInfo = maskedPixelInfo)


    def getSmallestRange(self,calibrationData,type):
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
        if self.lastCalibrationDataGetSmallsetRange != None and \
                calibrationData == self.lastCalibrationDataGetSmallsetRange and \
                self.lastTypeGetSmallestRange == type:
            return self.lastRangeGetSmallestRange

        # store value in case it changes.
        self.lastCalibrationDataGetSmallsetRange = copy.deepcopy(calibrationData)
        self.lastTypeGetSmallestRange = type
            
        if calibrationData.getCenterX()["val"] < 0 or \
            calibrationData.getCenterX()["val"]  > self.theDiffractionData.size-1 or \
            calibrationData.getCenterY()["val"] < 0 or \
            calibrationData.getCenterY()["val"]  > self.theDiffractionData.size-1:

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

            tempRange = {"qLower":qLower,"qUpper":qUpper,"chiLower":chiLower,"chiUpper":chiUpper}
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

            if type == "Q":
                lower = 0
                upper = qUpper
            elif type == "2theta":
                lower = Transform.convertQToTwoTheta(0,calibrationData)
                upper = Transform.convertQToTwoTheta(qUpper,calibrationData)

            else:
                raise Exception("Unable to find smallest range. \
This function must be passed for the parameter type either \
'Q', or '2theta'")

            tempRange = {"qOrTwoThetaLower":lower,"qOrTwoThetaUpper":upper,
                    "chiLower":-180,"chiUpper":180}

            self.lastRangeGetSmallestRange = tempRange
            return tempRange


def test():
    import doctest
    import DiffractionData
    doctest.testmod(DiffractionData,verbose=0)
        
if __name__ == "__main__":
    test()
 
