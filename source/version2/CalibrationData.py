### DOCUMENT REFINING and HOW IT WORKS !!! Also document parameter bounds

import copy
from Exceptions import UserInputException
import Transform

class CalibrationData:
    r""" CalibrationData is an object for dealing with the experimental
        parameters for an x-ray diffraction experiment. There parameters
        are particularly useful for calibrating diffraction data.
        The experimental parameters that are interesting (and deal with
        in this object are)
        * The x and y center of the image. This is the location of the 
        pixel which would be hit by the incoming beam. 
        * The distance between the experiment and the detector.
        * The energy or wavelength of the incoming x-rays. This code
        will do the proper conversion so that you set whichever you
        want and get whatever you say. 
        * Alpha and Beta, the two tilts of the detector.
        * pixellength and pixelheight are the width and height of
        each pixel in microns.

        This object is smart enough to deal with files of calibration Data.
        The calibration data file format is easy to use. Here is an example
        calibration data file:
        +-----------------------+
        |# Calibration File     |         
        |xc	1                   |
        |yc	2                   |
        |D	3                   |
        |E	4                   |
        |alpha	5               |
        |beta   -10             |
        |pixellength    100     |
        |pixelheight    100     |
        +-----------------------+
        This is easy. You can have this object read in one of these files
        with the method fromFile() and write to the file with the method
        toFile().


        Here, I am showing you you can set values in the object and get values from the object.

            >>> data = CalibrationData()
            >>> data.setCenterX(1.5)

        If you give the setting function a second value, this is the fixed flag. It must be 
        either 0 or 1.

            >>> data.setCenterY(2.5,1)
            >>> data.setDistance(3.5)
            >>> data.setEnergy(4.5,1)
            >>> data.setAlpha(5.5,0)
            >>> data.setRotation(0,0)
            >>> data.allSet()
            0
            >>> data.setBeta(6.5,1)
            >>> data.setPixelLength(100)
            >>> data.setPixelHeight(100)
            >>> data.allSet()
            1

        The getters return a dictionary of the from 
        {'val':value,'fixed':fixed,'lower':lower,'upper':upper}.
        Here, val is the value of the parameter, fixed is wether or not to fix
        the value, lower is a lower bound on the value and upper is an upper
        bound on the value. By default, fixed is 0 and lower and upper are None.
            
            >>> data.getCenterX()['val']
            1.5
            >>> data.getCenterX()['fixed']
            0
            >>> data.getCenterY()['val']
            2.5
            >>> data.getCenterY()['fixed']
            1
            >>> data.getDistance()['val']
            3.5
            >>> data.getDistance()['fixed']
            0
            >>> data.getEnergy()['val']
            4.5
            >>> data.getEnergy()['fixed']
            1
            >>> data.getAlpha()['val']
            5.5
            >>> data.getAlpha()['fixed']
            0
            >>> data.getBeta()['val']
            6.5
            >>> data.getBeta()['fixed']
            1
            >>> data.getPixelLength()['val']
            100
            >>> data.getPixelHeight()['val']
            100
            >>> data.setPixelLength(10)
            >>> data.getPixelLength()['val']
            10
            >>> data.setPixelLength(100)
            >>> data.getPixelLength()['val']
            100
            >>> data.setWavelength(1.0)
            >>> print '%.10f' % data.getWavelength()['val']
            1.0000000000
            >>> print '%.10f' % data.getEnergy()['val']
            12398.4172000000
            >>> data.setWavelength(3099.6043)
            >>> print '%.10f' % data.getWavelength()['val']
            3099.6043000000
            >>> print '%.10f' % data.getWavelength()['val']
            3099.6043000000
            >>> data.getWavelength()['fixed']
            0
            >>> print '%.10f' % data.getEnergy()['val']
            4.0000000000
            >>> data.getEnergy()['fixed']
            0

        Now, here is the toFile function in action. I am saving the data 
        to a temporary file and then reading it back out.

            >>> import tempfile
            >>> tempFile = tempfile.mktemp()
            >>> data.toFile(tempFile,energyOrWavelength='energy')
            >>> file = open(tempFile,'r')
            >>> file.readline() 
            '# Calibration File\n'
            >>> file.readline() 
            'xc\t1.500000\t0\n'
            >>> file.readline()
            'yc\t2.500000\t1\n'
            >>> file.readline()
            'D\t3.500000\t0\n'
            >>> file.readline()
            'E\t4.000000\t0\n'
            >>> file.readline()
            'alpha\t5.500000\t0\n'
            >>> file.readline()
            'beta\t6.500000\t1\n'
            >>> file.readline()
            'rotation\t0.000000\t0\n'
            >>> file.close()

        You can also read data from a temporary files.
        I will read data back from this temp.

            >>> data = CalibrationData(tempFile)
            >>> data.getCenterX()['val']
            1.5
            >>> data.getCenterY()['val']
            2.5
            >>> data.getDistance()['val']
            3.5
            >>> data.getEnergy()['val']
            4.0
            >>> data.getAlpha()['val']
            5.5
            >>> data.getBeta()['val']
            6.5

        You can also set and get parameters 
        by explicitly naming the things you are chaning.

            >>> data.setCenterX(-1,fixed=1)
            >>> data.getCenterX()['val']
            -1
            >>> data.getCenterX()['fixed']
            1
            >>> data.setCenterX(-2,fixed=0)
            >>> data.getCenterX()['val']
            -2
            >>> data.getCenterX()['fixed']
            0


        Now, test reading a file which has some of
        the parameters fixed.

            >>> tempFile = tempfile.mktemp()
            >>> file = open(tempFile,'w')
            >>> file.write('# Calibration File\n')
            >>> file.write('# more comments\n')
            >>> file.write('xc\t1.500000\t1\n')
            >>> file.write('yc\t2.500000\n')
            >>> file.write('D\t3.500000\t1\n')
            >>> file.write('# more comments\n')
            >>> file.write('E\t4.000000\t1\n')
            >>> file.write('alpha\t5.500000\n')
            >>> file.write('beta\t6.500000\t0\n')
            >>> file.write('rotation\t0\t0\n')
            >>> file.write('pixelLength\t100\n')
            >>> file.write('pixelHeight\t100\n')
            >>> file.close()

        Get the data back out of the next file 

            >>> data = CalibrationData(tempFile)
            >>> data.getCenterX()['val']
            1.5
            >>> data.getCenterX()['fixed']
            1
            >>> data.getCenterY()['val']
            2.5
            >>> data.getCenterY()['fixed']
            0
            >>> data.getDistance()['val']
            3.5
            >>> data.getDistance()['fixed']
            1
            >>> data.getEnergy()['val']
            4.0
            >>> data.getEnergy()['fixed']
            1
            >>> data.getAlpha()['val']
            5.5
            >>> data.getAlpha()['fixed']
            0
            >>> data.getBeta()['val']
            6.5
            >>> data.getBeta()['fixed']
            0

        Try setting some more values and get them back.

            >>> data.setCenterX(2.75,fixed=1)
            >>> data.setCenterY(0.75,fixed=1)
            >>> data.setDistance(10.75,fixed=1)
            >>> data.setEnergy(11.25,fixed=1)
            >>> data.getCenterX()['val']
            2.75
            >>> data.getCenterX()['fixed']
            1
            >>> data.getCenterY()['val']
            0.75
            >>> data.getCenterY()['fixed']
            1
            >>> data.getDistance()['val']
            10.75
            >>> data.getDistance()['fixed']
            1
            >>> data.getEnergy()['val']
            11.25
            >>> data.getEnergy()['fixed']
            1
            >>> data.getAlpha()['val']
            5.5
            >>> data.getAlpha()['fixed']
            0

            >>> data.getBeta()['val']
            6.5
            >>> data.getBeta()['fixed']
            0

        This time, read the wavelength from a file. Also,
        test to make sure comment lines in the file don't
        confuse my program.

            >>> tempFile = tempfile.mktemp()
            >>> file = open(tempFile,'w')
            >>> file.write('# Calibration File\n')
            >>> file.write('# more comments\n')
            >>> file.write('xc\t1.500000\n')
            >>> file.write('yc\t2.500000\n')
            >>> file.write('D\t3.500000\n')
            >>> file.write('# more comments\n')
            >>> file.write('wavelength\t1.000000\n')
            >>> file.write('alpha\t5.500000\n')
            >>> file.write('beta\t6.500000\n')
            >>> file.write('rotation\t0\n')
            >>> file.write('pixelLength\t100\n')
            >>> file.write('pixelHeight\t100\n')
            >>> file.close()
            >>> data = CalibrationData(tempFile)
            >>> print '%.10f' % data.getWavelength()['val']
            1.0000000000
            >>> print '%.10f' % data.getEnergy()['val']
            12398.4172000000
    """

    # centerX and centerY are the x and y centers of the image, in pixels. 
    centerX = {'val':None,'fixed':None,'lower':None,'upper':None}
    centerY = {'val':None,'fixed':None,'lower':None,'upper':None}
    # Distance is the distance from the sample to the middle of the detector, 
    # in units of mm. 
    distance = {'val':None,'fixed':None,'lower':None,'upper':None}
    # Energy is the energy of the x-rays used during the diffraction 
    # experiment, in units of eV. 
    energy = {'val':None,'fixed':None,'lower':None,'upper':None}
    # alpha and beta are the tilt angles of the detector, in units 
    # of degrees
    alpha = {'val':None,'fixed':None,'lower':None,'upper':None}
    beta = {'val':None,'fixed':None,'lower':None,'upper':None}
    rotation = {'val':None,'fixed':None,'lower':None,'upper':None}

    # pixelLength/pixelHeight have no bound and cannot be varied (need no 'fixed')
    pixelLength = {'val':None}
    pixelHeight = {'val':None}


    def __init__(self,filename=None):
        """ Initialize the object. If no parameters are given, do nothing. If a filename is given,
            get the calibration parameters from the file. """
        if filename != None:
            self.fromFile(filename)

    def __ne__(self,other):
        return not self.__eq__(other)

    def __eq__(self,other):
        if type(self) == type(None) or type(other) == type(None):
            return 0

        if self.centerX == other.centerX and \
                self.centerY == other.centerY and \
                self.distance == other.distance and \
                self.energy == other.energy and \
                self.alpha == other.alpha and \
                self.beta == other.beta and \
                self.rotation == other.rotation and \
                self.pixelLength == other.pixelLength and \
                self.pixelHeight == other.pixelHeight:
            return 1



    def allSet(self):
        """ Returns 1 if all the values and fixeds have been set, and 0 otherwise. """
        if self.centerX['val'] != None and self.centerX['fixed'] != None and \
                self.centerY['val'] != None and self.centerY['fixed'] != None and \
                self.distance['val'] != None and self.distance['fixed'] != None and \
                self.energy['val'] != None and self.energy['fixed'] != None and \
                self.alpha['val'] != None and self.alpha['fixed'] != None and \
                self.beta['val'] != None and self.beta['fixed'] != None and \
                self.rotation['val'] != None and self.rotation['fixed'] != None and \
                self.pixelLength['val'] != None and self.pixelHeight['val'] != None:
            return 1

        return 0

    def allParametersFixed(self):
        if self.centerX['fixed']==1 and self.centerY['fixed']==1 and \
                self.distance['fixed']==1 and self.energy['fixed']==1 and \
                self.alpha['fixed']==1 and self.beta['fixed']==1 and \
                self.rotation['fixed']==1: 
            return 1

        return 0



    def fromFile(self,filename):
        """ This function reads in calibration data from a file and stores it in the object. """

        # reset data
        centerX = {'val':None,'fixed':None,'lower':None,'upper':None}
        centerY = {'val':None,'fixed':None,'lower':None,'upper':None}
        distance = {'val':None,'fixed':None,'lower':None,'upper':None}
        energy = {'val':None,'fixed':None,'lower':None,'upper':None}
        alpha = {'val':None,'fixed':None,'lower':None,'upper':None}
        beta = {'val':None,'fixed':None,'lower':None,'upper':None}
        rotation = {'val':None,'fixed':None,'lower':None,'upper':None}
        pixelLength = {'val':None}
        pixelHeight = {'val':None}

        # if an energy line has been found, this will turn into a 1
        # once that has happened, the loop will not set a wavelength 
        # in the file after an energy line has been found. 
        energyFound = 0

        file = open(filename,'r')
        line = file.readline()
        while line:
            # remove comments from the line
            line = line.split('#')[0]

            # Ignore any blank or comment lines
            if line!='':
                words = line.split()

                if len(words) !=2 and len(words) !=3:
                    line = line.split('\n')[0]
                    raise UserInputException('"%s" is not a valid line in the calibration file %s. Calibration lines should be of the form "name   value" or "name   value   fixed".' % (line,filename) )

                name = words[0].lower()
                try:
                    val = float(words[1])
                except:
                    line = line.split('\n')[0]
                    raise UserInputException('"%s" is not a valid line in the calibration file %s. Calibration lines should be of the form "name   value" or "name   value   fixed" with value a valid number.' % (line,filename) )

                # by default, the fixed value is 0
                fixed = 0
                if len(words) == 3:
                    try:
                        fixed = int(words[2])
                    except:
                        line = line.split('\n')[0]
                        raise UserInputException('"%s" is not a valid line in the calibration file %s. Calibration lines should be of the form "name   value" or "name   value   fixed" with fixed either 0 or 1.' % (line,filename) )
                    if fixed != 1 and fixed != 0:
                        line = line.split('\n')[0]
                        raise UserInputException('"%s" is not a valid line in the calibration file %s. Calibration lines should be of the form "name   value" or "name   value   fixed" with fixed either 0 or 1.' % (line, filename) )
                    

                if name == "xc" or name == "xcenter" or name == "x":
                    self.setCenterX(val,fixed)
                elif name == "yc" or name == "ycenter" or name == "y":
                    self.setCenterY(val,fixed)
                elif name == "d" or name == "distance":
                    self.setDistance(val,fixed)
                elif name == "wave" or name == "wavelength" or name == "w" and energyFound ==0:
                    self.setWavelength(val,fixed)
                elif name == "e" or name == "energy":
                    self.setEnergy(val,fixed)
                elif name == "alpha":
                    self.setAlpha(val,fixed)
                elif name == "beta":
                    self.setBeta(val,fixed)
                elif name == "rotation" or name == "r" or name == "rot":
                    self.setRotation(val,fixed)
                elif name == "pixellength" or name == "pl":
                    self.setPixelLength(val)
                elif name == "pixelheight" or name == "ph":
                    self.setPixelHeight(val)
                else:
                    raise UserInputException('"%s" is not a valid parameter to set in the calibration file %s. You can only set the parameter xc, yc, D, E, wave, alpha, beta, and rotation, pixellength, and pixelheight.' % (name,filename) )

            line = file.readline()

        # once we are done, check to see if all the values have been set
        if self.centerX['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the x center.' % filename )
        if self.centerY['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the y center.' % filename )
        if self.distance['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the distance.' % filename )
        if self.energy['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the energy.' % filename )
        if self.alpha['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set alpha.' % filename )
        if self.beta['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set beta.' % filename )
        if self.rotation['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the rotation angle.' % filename )
        if self.pixelLength['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the pixel length.' % filename )
        if self.pixelHeight['val']==None:
            raise UserInputException('%s is not a valid calibration file because it does not set the pixel height.' % filename )


    def toFile(self,filename,energyOrWavelength):
        if self.centerX['val'] == None or self.centerX['fixed']==None:
            raise UserInputException('Function toFile() cannot run because the x center has not been set yet.')
        if self.centerY['val'] == None or self.centerY['fixed']==None:
            raise UserInputException('Function toFile() cannot run because the y center has not been set yet.')
        if self.distance['val'] == None or self.distance['fixed']==None:
            raise UserInputException('Function toFile() cannot run because the distance has not been set yet.')
        if self.energy['val'] == None or self.energy['fixed']==None:
            return UserInputException('Function toFile() cannot run because neither the wavelength nor the energy have been set yet.')
        if self.alpha['val']== None or self.alpha['fixed']==None:
            raise UserInputException('Function toFile() cannot run because alpha has not been set yet.')
        if self.beta['val'] == None or self.alpha['fixed']==None:
            raise UserInputException('Function toFile() cannot run because beta has not been set yet.')
        if self.rotation['val'] == None or self.rotation['fixed']==None:
            raise UserInputException('Function toFile() cannot run because rotation has not been set yet.')
        if self.pixelLength['val'] == None:
            raise UserInputException('Function toFile() cannot run because the pixel length has not been set yet.')
        if self.pixelHeight['val'] == None:
            raise UserInputException('Function toFile() cannot run because the pixel height has not been set yet.')

        energyOrWavelength = energyOrWavelength.lower()
        if energyOrWavelength != 'energy' and energyOrWavelength != 'wavelength':
            raise UserInputException("Function toFile() cannot run because parameter energyOrWavelength must be set to either 'energy' or 'wavelength'.")

        file = open(filename,'w')
        file.write("# Calibration File\n")

        # write the fixed values to the file
        dict = self.getCenterX()
        file.write('xc\t%f\t%d\n' % (dict['val'],dict['fixed']))

        dict = self.getCenterY()
        file.write('yc\t%f\t%d\n' % (dict['val'],dict['fixed']))

        dict = self.getDistance()
        file.write('D\t%f\t%d\n' % (dict['val'],dict['fixed']))

        if energyOrWavelength == 'energy':
            dict = self.getEnergy()
            file.write('E\t%f\t%d\n' % (dict['val'],dict['fixed']))
        if energyOrWavelength == 'wavelength':
            dict = self.getWavelength()
            file.write('wavelength\t%f\t%d\n' % (dict['val'],dict['fixed']))

        dict = self.getAlpha()
        file.write('alpha\t%f\t%d\n' % (dict['val'],dict['fixed']))

        dict = self.getBeta()
        file.write('beta\t%f\t%d\n' % (dict['val'],dict['fixed']))
        
        dict = self.getRotation()
        file.write('rotation\t%f\t%d\n' % (dict['val'],dict['fixed']))

        dict = self.getPixelLength()
        file.write('pixelLength\t%f\n' % dict['val'])

        dict = self.getPixelHeight()
        file.write('pixelHeight\t%f\n' % dict['val'])


    def __str__(self):
        """ Stringify the object. Useful for debugging. """
        string = ''
        if self.centerX['val'] != None and self.centerX['fixed'] != None:
            string+=' - x center:    %15.7f     fixed = %d\n' % (self.centerX['val'],self.centerX['fixed'])
        if self.centerY['val'] != None and self.centerY['fixed'] != None:
            string+=' - y center:    %15.7f     fixed = %d\n' % (self.centerY['val'],self.centerY['fixed'])
        if self.distance['val'] != None and self.distance['fixed'] != None:
            string+=' - distance:    %15.7f     fixed = %d\n' % (self.distance['val'],self.distance['fixed'])
        if self.energy['val'] != None and self.energy['fixed'] != None:
            string+=' - energy:      %15.7f     fixed = %d\n' % (self.energy['val'],self.energy['fixed'])
        if self.alpha['val'] != None and self.alpha['fixed'] != None:
            string+=' - alpha:       %15.7f     fixed = %d\n' % (self.alpha['val'],self.alpha['fixed'])
        if self.beta['val'] != None and self.beta['fixed'] != None:
            string+=' - beta:        %15.7f     fixed = %d\n' % (self.beta['val'],self.beta['fixed'])
        if self.rotation['val'] != None and self.rotation['fixed'] != None:
            string+=' - rotation:    %15.7f     fixed = %d\n' % (self.rotation['val'],self.rotation['fixed'])
        if self.pixelLength['val'] != None:
            string+=' - pixelLength: %15.7f\n' % self.pixelLength['val']
        if self.pixelHeight['val'] != None:
            string+=' - pixelHeight: %15.7f\n' % self.pixelHeight['val']
        return string

    def writeCommentString(self,file):
        """ Writes to a 'file' a comment string which contains the values of the diffraction data. """
        if self.centerX['val'] != None:
            file.write('#   x center: %15.7f pixels\n' % self.centerX['val'])
        if self.centerY['val'] != None:
            file.write('#   y center: %15.7f pixels\n' % self.centerY['val'])
        if self.distance['val'] != None:
            file.write('#   distance: %15.7f mm\n' % self.distance['val'])
        if self.energy['val'] != None:
            file.write('#   energy:   %15.7f eV\n' % self.energy['val'])
        if self.alpha['val'] != None:
            file.write('#   alpha:    %15.7f degrees\n' % self.alpha['val'])
        if self.beta['val'] != None:
            file.write('#   beta:     %15.7f degrees\n' % self.beta['val'])
        if self.rotation['val'] != None:
            file.write('#   rotation: %15.7f degrees\n' % self.rotation['val'])
        if self.pixelLength['val'] != None:
            file.write('#   pixel length: %15.7f microns\n' % self.pixelLength['val'])
        if self.pixelHeight['val'] != None:
            file.write('#   pixel height: %15.7f microns\n' % self.pixelHeight['val'])
         

    def setCenterX(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the x center because the fixed value must be either 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the x center because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the x center because the upper bound must be greater then the value.")

        self.centerX = {'val':val,'fixed':fixed,'lower':lower,'upper':upper}


    def getCenterX(self):
        if self.centerX['val']==None or self.centerX['fixed']== None:
            raise UserInputException('Cannot get the x center because it has not been set.')

        return copy.copy(self.centerX)


    def setCenterY(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the y center because fixed must be either 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the y center because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the y center because the upper bound must be greater then the value.")

        self.centerY = {'val':val,'fixed':fixed,'lower':lower,'upper':upper}


    def getCenterY(self):
        if self.centerY['val']==None or self.centerY['fixed']==None:
            raise UserInputException('Cannot get the y center because it has not been set.')

        return copy.copy(self.centerY)


    def setDistance(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the distance because fixed must be either to 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the distance because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the distance because the upper bound must be greater then the value.")
        if val <= 0:
            raise UserInputException("Canont set the distance because it must be a positive quantity.")

        self.distance = {'val':val,'fixed':fixed,'lower':lower,'upper':upper}


    def getDistance(self):
        if self.distance['val']==None or self.distance['fixed']==None:
            raise UserInputException('Cannot get the distance because it has not been set.')

        return copy.copy(self.distance)


    def setEnergy(self,val,fixed=0,lower=None,upper=None):
        """ The energy input is in units of eV. """
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the energy because fixed must be either 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the energy because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the energy because the upper bound must be greater then the value.")
        if val <= 0:
            raise UserInputException("Cannot set the energy because it must be a positive quantity.")

        self.energy = {'val':val,'fixed':fixed,'lower':lower,'upper':upper}


    def getEnergy(self):
        if self.energy['val']==None or self.energy['fixed']== None:
            return UserInputException('Cannot get the energy because neither the wavelength nor the energy have been set yet.')
        
        return copy.copy(self.energy)

    def setWavelength(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the wavelength because fixed must be set to 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the wavelength because the lower bound on wavelength must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the wavelength because the upper bound on wavelength must be greater then the value.")
        if val <= 0:
            raise UserInputException("Cannot set the wavelength because it must be a positive quantity.")

        val = Transform.convertWavelengthToEnergy(val)
        if lower != None: lower=hc/upper
        if upper != None: upper=hc/lower
        # note that a low wavelength is the same as a high energy and vice versa!
        self.energy = {'val':val,'fixed':fixed,'lower':upper,'upper':lower} 


    def getWavelength(self):
        if self.energy['val'] == None or self.energy['fixed'] == None:
            return UserInputException('Cannot get the wavelength because neither the wavelength nor the energy have been set.')

        val = Transform.convertEnergyToWavelength(self.energy['val'])
        lower,upper=None,None
        if self.energy['lower'] != None: lower = hc/self.energy['upper']
        if self.energy['upper'] != None: upper = hc/self.energy['lower']
        return {'val':val,'fixed':self.energy['fixed'],'lower':lower,'upper':upper}


    def setAlpha(self,val,fixed=0,lower=None,upper=None):
        if fixed!= 0 and fixed!= 1:
            raise UserInputException("Cannot set alpha because fixed must be set to 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set alpha because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set alpha because the upper bound must be greater then the value.")
        if val < -90 or val > 90:
            raise UserInputException("Cannot set alpha because it must be between -90 and 90")

        self.alpha = {'val':val,'fixed':fixed,'lower':upper,'upper':lower} 


    def getAlpha(self):
        if self.alpha['val']==None or self.alpha['fixed']== None:
            raise UserInputException('cannot get alpha because it has not been set.')
        
        return copy.copy(self.alpha)
      

    def setBeta(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set beta because fixed must be set to 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set beta because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set beta because the upper bound must be greater then the value.")
        if val < -90 or val > 90:
            raise UserInputException("Cannot set beta because it must be between -90 and 90")

        self.beta = {'val':val,'fixed':fixed,'lower':upper,'upper':lower} 


    def getBeta(self):
        if self.beta['val']==None or self.beta['fixed']== None:
            raise UserInputException('Cannot get beta because it has not been set.')
       
        return copy.copy(self.beta)


    def setRotation(self,val,fixed=0,lower=None,upper=None):
        if fixed != 0 and fixed != 1:
            raise UserInputException("Cannot set the rotation angle because fixed must be set to 0 or 1.")
        if lower != None and lower >= val:
            raise UserInputException("Cannot set the rotation angle because the lower bound must be less then the value.")
        if upper != None and upper <= val:
            raise UserInputException("Cannot set the rotation angle because the upper bound must be greater then the value.")
        if val < -360 or val > 360:
            raise UserInputException("Cannot set the rotation angle because it must be between -90 and 90")

        self.rotation = {'val':val,'fixed':fixed,'lower':upper,'upper':lower} 


    def getRotation(self):
        if self.rotation['val']==None or self.rotation['fixed']== None:
            raise UserInputException('Cannot get the rotation angle because it has not been set.')
       
        return copy.copy(self.rotation)
   

    def setPixelLength(self,val):
        if val<=0:
            raise UserInputException("Cannot set the pixel length because it must be greater then 0.")
        self.pixelLength = {'val':val}


    def getPixelLength(self):
        if self.pixelLength['val']==None: 
            raise UserInputException('Cannot get the pixel length because it has not been set.')
        return copy.copy(self.pixelLength)

    def setPixelHeight(self,val):
        if val<=0:
            raise UserInputException("Cannot set the pixel height because it must be greater then 0.")
        self.pixelHeight= {'val':val}


    def getPixelHeight(self):
        if self.pixelHeight['val']==None: 
            raise UserInputException('Cannot get the pixel height because it has not been set.')
        return copy.copy(self.pixelHeight)


def test():
    import doctest
    import CalibrationData
    doctest.testmod(CalibrationData,verbose=1)
        
if __name__ == "__main__":
    test()
