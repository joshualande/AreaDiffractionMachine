from Exceptions import UserInputException
import General
import Image
import Numeric 
from Numeric import choose, less, equal, alltrue, less_equal
import re

import EdfFile

class ESRF:
    """ An object for reading in the ESRF Data Format (.edf) 
        This file format as discussed on the Area Diffraction
        Machine discussion group: 

        http://groups.google.com/group/area-diffraction-machine/
        browse_thread/thread/ab6fdfa81f619634

        I am making the EdfFile object do all the hard work.
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
            f = EdfFile.EdfFile(filename)
        except:
            raise UserInputException("""Unable to read in the file \
%s because the Object EdfFile that I am using to read in edf data \
raised an error when trying to read in the file. This probably means \
that there is something wrong \
with the file that you are trying to open""" % filename)

        data = f.GetData(0)

        if not alltrue(alltrue(less_equal(data,2147483647))):
            print """Warning, some of the data stored in the \
file %s has an intensity larger then 2^31-1 which is too big for this \
program to hold. Any of these large values were clipped to have a value 
of 2^31-1.""" % filename
        

        # clip any data that is too big
        mask1 =  data <= 2147483647
        mask2 =  data > 2147483647
        masked_data = data*mask1 + (pow(2,31)-1) * mask2
        masked_data = masked_data.astype(Numeric.Int32)

        self.size = max(masked_data.shape[0],masked_data.shape[1])

        # pad values if necessary - create an array to put everything in
        self.data = Numeric.zeros((self.size,self.size),Numeric.Int32)

        # copy the data into the padded array
        self.data[0:masked_data.shape[0],0:masked_data.shape[1]] = masked_data
        self.data = Numeric.transpose(self.data)
