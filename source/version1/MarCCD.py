from Exceptions import UserInputException
import MarCCDWrap
import Numeric
import Image

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

        try:
            file = open(filename,'r')
            file.close()
        except IOError:
            raise UserInputException('%s does not exist' % filename)

        # first read header

        try:
            width,height,self.headerDistance,self.headerPixelLength, \
                    self.headerPixelHeight,self.headerWavelength = \
                    MarCCDWrap.get_header(filename)
        except:
            raise UserInputException("Unable to open MarCCD data file %s." % filename)

        if (width != height):
            raise UserInputException("Cannot open %s because the header is not formated properly" % filename)

        if self.headerDistance <= 0:
            self.headerDistance = None
        if self.headerWavelength <= 0:
            self.headerWavelength = None

        self.size = width

        self.filename = filename

        img = Image.open(filename)

        img = img.convert('I') #convert to int
        self.data = Numeric.fromstring(img.tostring(), Numeric.Int)
        self.data.shape = self.size,self.size

