import struct
import Numeric
import string
import os
import General 

import UncompressWrap

class MarXXXX:
    """ An object for dealing with .mar3450 and .mar2300 data, and 
        presumably similarly formatted files. 
        Mar data is described at:
        http://www.mar-usa.com/support/downloads/mar345_formats.pdf """

    filename = None
    data = None
    size= None
    headerPixelLength=None
    headerPixelHeight=None
    headerWavelength=None
    headerDistance=None
    headerCenterX,headerCenterY=None,None

    _high=None

    def __init__(self,filename):

        if not os.path.exists(filename):
            raise Exception('Cannot open diffraction data. %s does not exist',filename)

        # store the file for later
        self.filename=filename

        self.readHeader()

        # Use a C wrapper to decompress the data
        self.data = UncompressWrap.get_pck(self.filename,self.size)

        self.getHighValues()
        

    def readHeader(self):
        """ This function opens a marXXX file and parses 
            the relevant information. It stores the data for later.
            a diffractionDataFile object. """
        file = open(self.filename,'rb')

        line = file.readline()
        while line!='' and line !="END OF HEADER\n": 

            words = string.split(line)

            if len(words)>0:
                if words[0] == "FORMAT": 
                    # this line is of the form: "FORMAT         3450  PCK 11902500"
                    if len(words)!=4: 
                        raise Exception('The FORMAT line in the header of your diffraction data file must be of the form "FORMAT         3450  PCK 11902500"')
                    self.size = int(words[1]) 

                if words[0] == "HIGH":
                    if len(words)!=2:
                        raise Exception('The HIGH line in the header of your diffraction data file must be of the form "HIGH           146"')
                    self._high = int(words[1])
                    

                if words[0] == "PIXEL":
                    # this line is of the form: "PIXEL          LENGTH 100  HEIGHT 100"
                    if words[1]!="LENGTH" or words[3]!="HEIGHT" or len(words)!=5:
                        raise Exception('The PIXEL line in the header of your diffraction data file must be of the form "PIXEL          LENGTH 100  HEIGHT 100"')

                    # pixel length & height in micron
                    self.headerPixelLength = float(words[2])
                    self.headerPixelHeight = float(words[4])

                if words[0] == "WAVELENGTH":
                    # this line is of the form: "WAVELENGTH     0.97354"
                    if len(words) !=2:
                        raise Exception('The WAVELENGTH line in the header of your diffraction data file must be of the form "WAVELENGTH     0.97354"')
                    self.headerWavelength = float(words[1])
                    if self.headerWavelength <= 0:
                        self.headerWavelength = None


                if words[0] == "DISTANCE": 
                    #this line is of the form: "DISTANCE       125.296"
                    if len(words)!=2:
                        raise Exception('The DISTANCE line in the header of your diffraction data file must be of the form "DISTANCE       125.296"')
                    self.headerDistance = float(words[1])
                    if self.headerDistance <= 0:
                        self.headerDistance = None


                if words[0] == "CENTER": 
                    # this line is: "CENTER         X 1725.000  Y 1725.000"
                    if words[1] !="X" or words[3] !="Y" or len(words)!=5:
                        raise Exception('The CENTER line in the header of your diffraction data file must be of the form "CENTER         X 1725.000  Y 1725.000"')
                    self.headerCenterX = float(words[2])
                    self.headerCenterY = float(words[4])

            line = file.readline()

        file.close()


    def getHighValues(self):
        """ Reads the overloaded pixel from the bottom of the mar data.
            Data must be an array of integers so that the high values 
            can inserted. High values are read from the mar345 file and 
            inserted into the array. The values are changed in place. The 
            format of these high values is described at: 
            http://www.mar-usa.com/support/downloads/mar345_formats.pdf """

        # The first thing that has to be done is to pass through the header data.
        # Do do this, ignore everything until the "END OF HEADER" line
        file = open(self.filename,'rb')
        line = file.readline()
        while line != "END OF HEADER\n":
            line = file.readline()

        # Next, there is a bunch of white space and new lines before we get to 
        # the packed high data. We need to ignore all the garbage and loop 
        # until we get to real data. This part is particularly klugey because 
        # the high data can apparently begin with the newline character even though
        # the newline character is also used as part of the garbage. So we have to
        # know when we find a new line whether it is followed by a space (and to keep
        # looking for garbage) or other stuff (in which case it is part of the packed data
        # and we need to make sure to read the newline as part of the high values.)
        # I don't get why they would design the file format like this. It seems particularly
        # silly, but it might be that I am doing something stupid on my end which makes 
        # this look messy.
        char = file.read(1)
        while char == ' ' or char == '\n':
            if char == '\n' and General.peek(file) != ' ' and General.peek(file) != '\n':
                # if a newline is NOT followed by a space (and not another newline), then the newline is part
                # of the high data, so we need to start reading the real data in
                break

            char = file.read(1)

        # go back one so we get to the beginning of the high data
        file.seek(-1,1)

        # It is possible that there are no high pixels in the image. When this
        # happens, we arrive immediately at the "CCPR ..." line. 
        # When this happens, then exit the function without
        # adding any high pixels to the image. 
        peek = General.peekline(file)
        
        # This little bit is incase there is no peak data but there is a newline preceding the CCP4 line.
        # in this case, we would need to look at the second line to find the CCP4 stuff.
        if peek == '\n': peek = General.peeksecondline(file)

        if peek in ["CCP4 packed image, X: %04d, Y: %04d\n" % (self.size,self.size), 
                    "\nCCP4 packed image, X: %04d, Y: %04d\n" % (self.size,self.size)]:
            file.close()
            return
        
        nRecords = int(self._high/8.0 +.875) 
        nPairsPerRecord = 8
        nBytesPerRecord=64

        # read all the data we need
        next = file.read(nBytesPerRecord*nRecords)
        
        # unpack it. The 2 is because there are 2 value for each pair
        # The '<' character tells python whether to read in as big or 
        # little endian. I am not exactly sure which one I am using but 
        # it is the only one that will read the data in properly. Hopefully, 
        # no Mar data I am fed will use the old convention because my could 
        # would break. Nevertheless, I am pretty sure that my error handling 
        # will mean that it crashes which is better then doing the wrong thing.
        highVals = struct.unpack('<'+str(nRecords*nPairsPerRecord*2)+'i',next)

        if file.readline() !='\n': # we should have read to the end of the line
            raise Exception('Error: the program was unable to read the high pixels from the mar345 image because after reading all the high pixels, it did not find a newline character.')

        if file.readline()!='CCP4 packed image, X: %04d, Y: %04d\n' % (self.size,self.size):
            raise Exception('Error: the program was unable to read the high pixels from the mar345 image because it did not find the "CCCP4 packed image X: XXXX, Y: XXXX" line directly after the high data.')

        file.close()

        for loop in range(nRecords*nPairsPerRecord):
            location = highVals[2*loop]
            value = highVals[2*loop+1]
            
            if location == 0 and value == 0:
                # These records are padded w/ blank pairs. So if you come across one, just skip it
                continue

            if location < 0 or location >= self.size*self.size:
                raise Exception('Error: the program was unable to read the high pixels from the mar345 image. The current high value is supposed to be placed in location %d, but values can only be put from %d to %d' % (location,0,self.size*self.size-1))
            if value < 65536:
                raise Exception('Error: the program was unable to read the high pixels from the mar345 image. All high values must be >= 2^16, but the value read is %d' % value)

            
            # This is the transpose of where the data is 'really' stored because we already transposed
            # the data in the wrapped C code.
            column = int(location/self.size)
            row = location % self.size
            
            # here, the data that is overloaded should be either the maximum value (2^16-1), or -1 if the value
            # has not yet been properly converted form its signed representation to its true unsigned representation.
            if self.data[row][column] != 65535 and self.data[row][column] !=-1:
                raise Exception('Error: the program was unable to read the high pixels from the mar345 image. The high value that is being replaced should be either 65535 or -1. Instead, it is %i ' % (self.data[row][column],) )

            self.data[row][column] = value
