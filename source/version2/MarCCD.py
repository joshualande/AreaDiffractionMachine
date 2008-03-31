from Exceptions import UserInputException
import MarCCDWrap
import Numeric
import Image
from Tiff import Tiff

class MarCCD:
    """ An object for dealing with MarCCD data. Read the header
        from wraped C code and use PIL code to get data. """

    filename = None
    data = None
    size  = None
    headerPixelLength=None
    headerPixelHeight=None
    headerWavelength=None
    headerDistance=None
    headerCenterX,headerCenterY=None,None
    
    def __init__(self,filename):

        self.filename = filename

        try:
            file = open(self.filename,'r')
            file.close()
        except IOError:
            raise UserInputException('%s does not exist' % self.filename)

        # first read header

        try:
            width,height,self.headerDistance,self.headerPixelLength, \
                    self.headerPixelHeight,self.headerWavelength = \
                    MarCCDWrap.get_header(self.filename)
        except:
            raise UserInputException("Unable to open MarCCD data file %s." % self.filename)
            
        # since marCCD data is just tiff data, we can just open the
        # file as though it is a tiff image and get the data and
        # dimensions out of it.
        temp = Tiff(self.filename)
        self.data = temp.data
        self.size = temp.size
        
