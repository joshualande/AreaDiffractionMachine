from Exceptions import UserInputException
import General
import Image
import Numeric 
from Numeric import choose, less, equal, alltrue
import re

class ESRF:
    """ An object for reading in the ESRF Data Format (.edf) 
        This file format as discussed on the Area Diffraction
        Machine discussion group: 
http://groups.google.com/group/area-diffraction-machine/browse_thread/thread/ab6fdfa81f619634
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
            file = open(filename,'r')
        except IOError:
            file.close()
            raise UserInputException('%s does not exist' % filename)

        header = ""

        current = file.read(1)
        while current != "}":
            if current == None:
                raise UserInputException("""Cannot read the ESRF Data \
Format file %s because the program can find no } curley bracket that 
ends the header file.""" % filename)
            header += current
            current = file.read(1)

        # I think that there is a newline after the '}' 
        # that has to be read in and ignored before
        # we get to the data.
        file.read(1)    
            
        # get out the DataType header field
        pattern = r"""DataType\s*=\s*(\w+)\s*;"""
        regexp= re.compile(pattern, re.DOTALL | re.IGNORECASE )
        datatype = regexp.findall(header)
        if len(datatype) != 1:
            raise UserInputException("Not found...")
        datatype = datatype[0]
        if datatype.lower() == "unsignedlong":
            depth = 4
            typecode = Numeric.UInt32
        elif datatype.lower() == "unsignedshort":
            depth = 2
            typecode = Numeric.UInt16
        else:
            raise UserInputException("")
        
        # get out the Dim_1 header field
        pattern = r"""Dim_1\s*=\s*(\w+)\s*;"""
        regexp= re.compile(pattern, re.DOTALL | re.IGNORECASE )
        dim_1 = regexp.findall(header)
        if len(dim_1) != 1:
            raise UserInputException("Not found...")
        try:
            height = int(dim_1[0]) 
        except:
            raise UserInputException("")

        # get out the Dim_2 header field
        pattern = r"""Dim_2\s*=\s*(\w+)\s*;"""
        regexp= re.compile(pattern, re.DOTALL | re.IGNORECASE )
        dim_2 = regexp.findall(header)
        if len(dim_2) != 1:
            raise UserInputException("")
        try:
            width = int(dim_2[0]) 
        except:
            raise UserInputException("Dim_1 not an integer...")

        # get out the size header field
        pattern = r"""Size\s*=\s*(\w+)\s*;"""
        regexp= re.compile(pattern, re.DOTALL | re.IGNORECASE )
        size = regexp.findall(header)
        if len(size) != 1:
            raise UserInputException("")
        try:
            size = int(size[0])
        except:
            raise UserInputException("")

        if height*width*depth != size:
            raise UserInputException("")
            
        # get out the data    
        datastring=file.read(width*height*depth)
        file.close()
        if len(datastring) < width*height*depth:
            raise Exception("""Cannot read the ESRF Data \
Format file %s because the file does not have enough data \
inside of it. """ % filename)

        self.size = max(width,height)

        # since the values might be too big, make sure overloaded
        # pixels throw an error
        temp = Numeric.fromstring(datastring,typecode)
        temp.shape = width,height

        temp2 = temp.astype(Numeric.Int32)

        if typecode == Numeric.UInt32:

            # make sure to clip any pixel which won't fit into 
            # the array. This probably will never be a problem,
            # but it best to code it up anyway. The reason to do 
            # this check here after the conversion to regular
            # integers is because Numeric objects holding UInt32 
            #data act really
            # weird and you can't get the data out of it to
            # do comparisons. This is because python does not
            # have native support for unsigned integers. 
            # Anyway, after doing the 
            # conversion to Ints, any of the too big data gets
            # stored as negative values so they are easy enough
            # to find and clip. If any values are negative,
            # print an error and make them equal to 2^31-1
            if not alltrue(alltrue(Numeric.greater_equal(temp2,0))):
                print """Warning, some of the data stored in the ESRF \
file %s has an intensity larger then 2^31-1 which is too big for this \
program to hold. Any of these values were clipped to have a value of \
2^31-1.""" % filename

            # make all the values less than 0 equal to 2^31 - 1
            # This techniqure is documented in:
            #   http://numpy.scipy.org/numpy.pdf
            # basically, it says that whenever a pix has intensity
            # less than 0, set it equal to 2^31-1. Otherwise,
            # set it equal to the value in temp2.
            temp2 = choose(less(temp2,0), (temp2, pow(2,31)-1)) 

        # pad values if necessary - create an array to put everything in
        self.data = Numeric.zeros((self.size,self.size),Numeric.Int32)

        # copy the data into the padded array
        self.data[0:temp2.shape[0],0:temp2.shape[1]] = temp2
        self.data = Numeric.transpose(self.data)


