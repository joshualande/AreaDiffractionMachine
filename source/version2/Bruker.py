from Exceptions import UserInputException
import Numeric 

class Bruker:
    """ An object for reading in Bruker data. 

        I figured out how to read in this data after
        examining some IDL code to read in Bruker data found at:
        http://cars9.uchicago.edu/software/idl/detectors.html
    """
    
    filename = None
    data = None
    size = None
    headerPixelLength=None
    headerPixelHeight=None
    headerWavelength=None
    headerDistance=None
    headerCenterX,headerCenterY=None,None
    
    def __init__(self,filename):

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

        npixelb = int(header['NPIXELB:'])
        ncol =    int(header['NCOLS  :'])
        nrow =    int(header['NROWS  :'])
        self.headerDistance = float(header['DISTANC:'])
        self.headerWavelength = float(header['WAVELEN:'].split()[0])
        temp = header['CENTER :'].split()
        self.headerCenterX = float(temp[0])
        self.headerCenterY = float(temp[1])

        self.size = max(ncol,nrow)

        datastring = file.read(ncol*nrow*npixelb)

        spill = file.read()
        file.close()

        if npixelb == 1:
            temp = Numeric.fromstring(datastring, Numeric.UInt8)
            temp.shape = nrow,ncol
        elif npixelb == 2:
            temp = Numeric.fromstring(datastring, Numeric.UInt16)
            temp.shape = nrow,ncol
        elif npixelb == 4:
            data = Numeric.fromstring(datastring, Numeric.UInt32)
            data.shape = nrow,ncol

            # clip any data that is too big to fit into a signed int.
            mask1 = data <= 2147483647
            mask2 = data > 2147483647
            temp = data*mask1 + (pow(2,31)-1)*mask2
        else:
            raise Exception("...")

        # pad values if necessary and convert to Int32
        self.data = Numeric.zeros((self.size,self.size),Numeric.Int32)
        self.data[0:temp.shape[0],0:temp.shape[1]] = temp
        self.data = Numeric.transpose(self.data)

        if int(header['NOVERFL:']) != 0:
            print 'Warning, this program is not properly \
reading in any of the overflow pixels in the image'
