from Exceptions import UserInputException
import Numeric 
import General


class Bruker:
    """ An object for reading in Bruker data. 

        I figured out how to read in this data after
        examining some IDL code to read in Bruker data found at:
        http://cars9.uchicago.edu/software/idl/detectors.html

        Also, Aure Gourrier was kind enough to post on the mailing group
        a description that he found of the Bruker file format

        http://groups.google.com/group/area-diffraction-machine/browse_thread/thread/66532a51d0f0dfb0 """
    
    filename = None
    data = None
    size = None
    headerPixelLength=None
    headerPixelHeight=None
    headerWavelength=None
    headerDistance=None
    headerCenterX,headerCenterY=None,None
    
    def __init__(self,filename):

        # Whether or not to look for the overload pixels
        doOverflow = 1 

        try:
            file = open(filename,'rb')
            file.close()
        except IOError:
            raise UserInputException('%s does not exist' % filename)

        self.filename = filename
        file = open(filename,'rb')

        header = {}

        for n in range(96):
            a=file.read(8)
            b=file.read(72)
            header[a]=b

        try:
            npixelb = int(header['NPIXELB:'].split()[0])
        except:
            raise Exception("Cannot read in the Bruker data file \
%s because the header field NPIXELB can not be parsed." % filename)

        if npixelb != 1 and npixelb != 2 and npixelb != 4:
            raise Exception("Cannot read in the Bruker data file \
%s because the The header field NPIXELB must equal 1, 2 or \
4." % npixelb)

        try:
            ncol = int(header['NCOLS  :'].split()[0])
        except:
            raise Exception("Cannot read in the Bruker data file \
%s because the header field NCOLS can not be parsed." % filename)

        try:
            nrow = int(header['NROWS  :'].split()[0])
        except:
            raise Exception("Cannot read in the Bruker data file \
%s because the header field NROWS can not be parsed." % filename)

        try:
            self.headerDistance = General.splitAverage(header['DISTANC:'])
        except:
            print "Cannot read the DISTANC header field from \
%s" % filename

        # sometimes, there are multiple wavelengths in this field
        # I am not sure what they are for, but we will just average
        # them and hope for the best.
        try:
            self.headerWavelength = General.splitAverage(header['WAVELEN:'])
        except:
            print "Cannot read the WAVELEN header field from \
%s" % filename

        try:
            self.headerCenterX = float(header['CENTER :'].split()[0])
            self.headerCenterY = float(header['CENTER :'].split()[1])
        except:
            print "Cannot read the center header fields from \
%s" % filename

        self.size = max(ncol,nrow)

        try:
            noverfl = int(header['NOVERFL:'].split()[0])
        except:
            raise Exception("Cannot read in the Bruker data file \
%s because the header field NOVERFL can not be parsed." % filename)

        datastring = file.read(ncol*nrow*npixelb)

        if npixelb == 1:
            temp = Numeric.fromstring(datastring, Numeric.UInt8)
            temp.shape = nrow,ncol

            if (noverfl != General.num_equals(temp,255)):
                print "Warning, cannot read in the overflow \
pixels in Bruker file %s because the header field NOVERFL \
(%s) does not match the number of pixels in the data with value \
equal to exactly 255 (%s). All overloaded pixels must be set in \
the data to 255)." % (filename,noverfl,General.num_equals(temp,255))

                doOverflow = 0

        elif npixelb == 2:
            temp = Numeric.fromstring(datastring, Numeric.UInt16)
            temp.shape = nrow,ncol

            if (noverfl != General.num_equals(temp,65535)):
                print "Warning, cannot read in the overflow \
pixels in Bruker file %s because the header field NOVERFL \
(%s) does not match the number of pixels in the data with value \
equal to exactly 65535 (%s). All overloaded pixels must be set in \
the data to 65535)." % (filename,noverfl,General.num_equals(temp,65535))

                doOverflow = 0

        elif npixelb == 4:
            data = Numeric.fromstring(datastring, Numeric.UInt32)
            data.shape = nrow,ncol

            # clip any data that is too big to fit into a signed int.
            mask1 = data <= 2147483647
            mask2 = data > 2147483647
            temp = data*mask1 + (pow(2,31)-1)*mask2

            # don't look for overflow pixels since they would be too
            # big to fit the data.
            if nooverfl != 0:
                print "No overflow pixels will be looked for in the \
Bruker file %s because the values would be too big to store in the \
data." %filename

            doOverflow = 0
                
        # convert to integers
        temp = temp.astype(Numeric.Int32)
        
        if noverfl != 0 and doOverflow:
            # loop over all overflow pixels
            for loop in range(noverfl):

                try:
                    intensity = int(file.read(9))
                    pixelOffset = int(file.read(7))

                except Exception, e:
                    raise Exception("Cannot read in all the \
overloaded pixels in the Bruker file %s because the overload \
pixels are not stored as ASCII at the bottom of the file as \
they should be." % filename)

                # make sure to use integer division
                row = int(pixelOffset)/int(ncol)
                column = pixelOffset % ncol

                if row >= nrow:
                    raise Exception("Cannot read in all the \
overload pixels in the Bruker file %s because one of the pixel \
offset numbers for an overloaded pixel would lead to putting the \
overloaded pixel outside of the data array." % filename)

                if npixelb == 1:
                    if temp[row][column] != 255:
                        raise Exception("Cannot read in all the \
overload pixels in the Bruker file %s because one of the pixel \
offset numbers for an overloaded pixel would lead to replacing \
a pixel whose intensity is not equal to 255 (as the replace \
pixels' intensity must be)." % filename)

                    temp[row][column] = intensity

                elif npixelb == 2:
                    if temp[row][column] != 65535:
                        raise Exception("Cannot read in all the \
overload pixels in the Bruker file %s because one of the pixel \
offset numbers for an overloaded pixel would lead to replacing \
a pixel whose intensity is not equal to 65535 (as the replace \
pixels' intensity must be)." % filename)

                    temp[row][column] = intensity

                # if npixelb = 4, then we don't look
                # for overloaded pixels b/c we can't
                # store them in our array.
                        
        file.close()

        # pad values if necessary and convert to Int32
        self.data = Numeric.zeros((self.size,self.size),Numeric.Int32)
        self.data[0:temp.shape[0],0:temp.shape[1]] = temp
        self.data = Numeric.transpose(self.data)

