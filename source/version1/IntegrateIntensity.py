import PmwFreeze as Pmw
import Numeric
import copy
import time

import Transform
import DiffractionAnalysisWrap

class IntegrateIntensity:
    values = None
    intensityData = None

    
    def __init__(self,diffractionData,calibrationData,lower,upper,num,
            constraintLower,constraintUpper,doConstraint,
            doPolarizationCorrection,P,
            typeOfIntegration,typeOfConstraint,maskedPixelInfo):

        self.integrate(diffractionData = diffractionData,
                calibrationData = calibrationData,
                lower = lower,
                upper = upper,
                num = num,
                constraintLower = constraintLower,
                constraintUpper = constraintUpper,
                doConstraint = doConstraint,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                typeOfIntegration = typeOfIntegration,
                typeOfConstraint = typeOfConstraint,
                maskedPixelInfo = maskedPixelInfo)
            

    def integrate(self,diffractionData,calibrationData,lower,
            upper,num,constraintLower,constraintUpper,doConstraint,
            doPolarizationCorrection,P,
            typeOfIntegration,typeOfConstraint,maskedPixelInfo):

        if typeOfIntegration == 'Q':
            if lower >= upper:
                raise Exception("Unable to integrate the intensity. The lower Q value must be less then the upper Q value")

            if lower < 0: 
                raise Exception("Unable to integrate intensity. The lower Q value must be larger then 0.")

            if upper > Transform.getMaxQ(calibrationData):
                raise Exception("Unable to integrate intensity. The upper Q value must be less then the largest possible Q value.")

            if num < 1:
                raise Exception("Unable to integrate intensity. The number of Q must be at least 1.")

        elif typeOfIntegration == '2theta':
            if lower >= upper:
                raise Exception("Unable to integrate the intensity. The lower 2theta value must be less then the upper 2theta value")

            if lower < 0: 
                raise Exception("Unable to integrate intensity. The lower 2theta value must be larger then 0.")

            if upper > 90:
                raise Exception("Unable to integrate intensity. The upper 2theta value must be smaller then 90.")

            if num < 1:
                raise Exception("Unable to integrate intensity. The number of 2theta must be at least 1.")

        elif typeOfIntegration == 'chi':
            if lower >= upper:
                raise Exception("Unable to integrate the intensity. The lower chi value must be less then the upper chi value")

            if lower < -360: 
                raise Exception("Unable to integrate intensity. The lower chi value must be larger then -360 degrees.")

            if upper > +360: 
                raise Exception("Unable to integrate intensity. The upper chi value must be lower then 360 degrees.")

            if upper - lower > 360:
                raise Exception("Unable to integrate intensity. The chi range can be at most 360 degrees.")

            if num < 1:
                raise Exception("Unable to integrate intensity. The number of chi must be at least 1.")
        else:
            raise Exception("Unable to integrate intensity. The function integrate must be passed for the parameter typeOfIntegration either 'Q', '2theta', or 'chi'")

        if doConstraint: 
            if (typeOfIntegration == 'Q' or typeOfIntegration == '2theta') and \
                typeOfConstraint == 'chi':

                if constraintLower >= constraintUpper:
                    raise Exception("Unable to integrate the intensity. The constraint lower chi value must be less then the upper chi value")

                if constraintLower < -360: 
                    raise Exception("Unable to integrate intensity. The constraint lower chi value must be larger then -360 degrees.")

                if constraintUpper > +360: 
                    raise Exception("Unable to integrate intensity. The constraint upper chi value must be lower then 360 degrees.")

                if constraintUpper - constraintLower > 360:
                    raise Exception("Unable to integrate intensity. The constraint chi range can be at most 360 degrees.")
            elif (typeOfIntegration == 'chi' and typeOfConstraint == 'Q'):

                if constraintLower >= constraintUpper:
                    raise Exception("Unable to integrate the intensity. The constraint lower Q value must be less then the upper Q value")

                if constraintLower < 0: 
                    raise Exception("Unable to integrate intensity. The constraint lower Q value must be larger then 0.")

                if constraintUpper > Transform.getMaxQ(calibrationData):
                    raise Exception("Unable to integrate intensity. The constraint upper Q value must be less then the largest possible Q value.")

            elif (typeOfIntegration == 'chi' and typeOfConstraint == '2theta'):

                if constraintLower >= constraintUpper:
                    raise Exception("Unable to integrate the intensity. The constraint lower 2theta value must be less then the upper 2theta value")

                if constraintLower < 0: 
                    raise Exception("Unable to integrate intensity. The constraint lower 2theta value must be larger then 0.")

                if constraintUpper > 90:
                    raise Exception("Unable to integrate intensity. The constraint upper 2theta value must be smaller then 90.")

            else:
                raise Exception("Constraint must be of the from chi, 2theta, or Q. Also, the constraint must be different from the type of integration.")


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
        self.values,self.intensityData = DiffractionAnalysisWrap.integrate(
                diffractionData,
                calibrationData.getCenterX()['val'],
                calibrationData.getCenterY()['val'],
                calibrationData.getDistance()['val'],
                calibrationData.getEnergy()['val'],
                calibrationData.getAlpha()['val'],
                calibrationData.getBeta()['val'],
                calibrationData.getRotation()['val'],
                lower, upper, num,
                constraintLower, constraintUpper,
                doConstraint,
                doPolarizationCorrection, P,
                maskedPixelInfo.doGreaterThanMask, greaterThanMask,
                maskedPixelInfo.doLessThanMask, lessThanMask,
                maskedPixelInfo.doPolygonMask,
                polygonsX,
                polygonsY,
                polygonBeginningsIndex,
                polygonNumberOfItems,
                calibrationData.getPixelLength()['val'],
                calibrationData.getPixelHeight()['val'],
                typeOfIntegration,
                typeOfConstraint)

        if type(self.intensityData) == type(None):
            raise Exception("Unspecified Error occured while integrating the data")

        self.typeOfIntegration = typeOfIntegration
        self.lower=lower
        self.upper=upper
        self.num=num
        self.constraintLower = constraintLower
        self.constraintUpper = constraintUpper
        self.doConstraint = doConstraint
        self.doPolarizationCorrection=doPolarizationCorrection
        self.P=P

        # We should make a shallow copy so that the widget dose
        # not get copied over. Nevertheless, all the stuff we
        # care about are single values so they will get really copied over
        self.maskedPixelInfo = copy.copy(maskedPixelInfo)

        self.typeOfConstraint = typeOfConstraint
        self.calibrationData=copy.deepcopy(calibrationData)


    def getValues(self): 
        return self.values
    

    def getIntensityData(self): 
        return self.intensityData


    def toFile(self,filename,diffractionDataName):
        """ Saves intensity integration to a file. """
        file = open(filename,'w')

        if self.typeOfIntegration == 'Q':
            file.write("# Q vs I Intensity Integration\n")
        elif self.typeOfIntegration == '2theta':
            file.write("# 2theta vs I Intensity Integration\n")
        elif self.typeOfIntegration == 'chi':
            file.write("# Chi vs I Intensity Integration\n")
        else:
            raise Exception("This should never happen")

        file.write("# Intensity integration of: %s\n" % diffractionDataName)
        file.write("# Data Integrated on "+time.asctime()+"\n")
        file.write("# Calibration data used:\n")
        self.calibrationData.writeCommentString(file)
        if self.doPolarizationCorrection:
            file.write("# A polarization correction was applied\n")
            file.write("#   P = %f\n" % self.P)
        else:
            file.write("# No polarization correction was applied\n")

        if self.maskedPixelInfo.doGreaterThanMask:
            file.write("# A greater than mask was applied\n")
            file.write("#   Greater than mask = %f (All pixels above %f were ignored)\n" % 
                    (self.maskedPixelInfo.greaterThanMask,self.maskedPixelInfo.greaterThanMask))
        else:
            file.write("# No greater than mask applied\n")

        if self.maskedPixelInfo.doLessThanMask:
            file.write("# A Less Than Mask was applied.\n")
            file.write("#   Less than mask = %f (All pixels below %f were ignored)\n" % 
                    (self.maskedPixelInfo.lessThanMask,self.maskedPixelInfo.lessThanMask))
        else:
            file.write("# No less than mask was applied\n")

        if self.maskedPixelInfo.doPolygonMask and self.maskedPixelInfo.numPolygons() > 0:
            file.write("# Polygon mask(s) were applied\n")
            file.write(self.maskedPixelInfo.writePolygonCommentString())
        else:
            file.write("# No polygon masks were applied\n")

        if self.doConstraint:
            if self.typeOfConstraint == "2theta":
                file.write("# Integration performed with a 2theta constraint\n")
                file.write("#   2theta constraint lower: %f\n" % self.constraintLower)
                file.write("#   2theta constraint upper: %f\n" % self.constraintUpper)
            if self.typeOfConstraint == "Q":
                file.write("# Integration performed with a Q constraint\n")
                file.write("#   Q constraint lower: %f\n" % self.constraintLower)
                file.write("#   Q constraint upper: %f\n" % self.constraintUpper)
            if self.typeOfConstraint == "chi":
                file.write("# Integration performed with a chi constraint\n")
                file.write("#   chi constraint lower: %f\n" % self.constraintLower)
                file.write("#   chi constraint upper: %f\n" % self.constraintUpper)
        else:
            if self.typeOfConstraint == "2theta":
                file.write("# No Constraint on 2theta was applied during the integration. All possible 2theta values were used.\n")
            if self.typeOfConstraint == "Q":
                file.write("# No Constraint on Q was applied during the integration. All possible Q values were used.\n")
            if self.typeOfConstraint == "chi":
                file.write("# No Constraint on chi was applied during the integration. All possible chi values were used.\n")

        step = (self.upper-self.lower)*1.0/self.num

        file.write("# Integration Range:\n")
    
        if self.typeOfIntegration == 'Q':
            file.write("#   Q Lower = %f\n" % self.lower)
            file.write("#   Q Upper = %f\n" % self.upper)
            file.write("#   Number of Q = %f\n" % self.num)
            file.write("#   Q Step = %f\n" % step )
            file.write('# Q\tAvg Intensity\n')
        if self.typeOfIntegration == 'chi':
            file.write("#   Chi Lower = %f\n" % self.lower)
            file.write("#   Chi Upper = %f\n" % self.upper)
            file.write("#   Number of Chi = %f\n" % self.num)
            file.write("#   Chi Step = %f\n" % step )
            file.write('# Chi\tAvg Intensity\n')
        if self.typeOfIntegration == '2theta':
            file.write("#   2theta Lower = %f\n" % self.lower)
            file.write("#   2theta Upper = %f\n" % self.upper)
            file.write("#   Number of 2theta = %f\n" % self.num)
            file.write("#   2theta Step = %f\n" % step )
            file.write("# Note: Average intensity values of -1 means that no data was put into the particular bin.\n")
            file.write('# 2theta\tAvg Intensity\n')

        for loop in range(self.num):
            # the current value is half way between the one lower bin value and the next lower bin value
            file.write('%f\t%f' % ( self.values[loop],self.intensityData[loop]))
            if loop != self.num-1:
                file.write('\n')
        file.close()

