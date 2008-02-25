from Exceptions import UserInputException
import Image
import Numeric 

class Tiff:
    """ An object for dealing with tiff data. """
    
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
            file = open(filename,'r')
            file.close()
        except IOError:
            raise UserInputException('%s does not exist' % filename)

        img = Image.open(filename)
        self.filename = filename

        self.size = max(img.size[0],img.size[1])

        print 'file loaded, about the convert'
        print 'mode = ',img.mode

        img = img.convert('I') #convert to int
        temp = Numeric.fromstring(img.tostring(), Numeric.Int32)

        # I am not exactly sure why PI and Numeric's tostring and 
        # fromstring method are transposed relative to eachother,
        # but this code is what works
        temp.shape = img.size[1],img.size[0]

        # pad values if necessary
        self.data = Numeric.zeros((self.size,self.size),Numeric.Int32)
        self.data[0:temp.shape[0],0:temp.shape[1]] = temp
        self.data = Numeric.transpose(self.data)
