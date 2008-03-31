import time

import Numeric
from PolygonWrap import insideWhichPolygon
from General import numeric_array_equals
from Exceptions import UserInputException

class MaskedPixelInfo:
    """ This is just a helper class to hold information about what
        type of pixel masking should be performed. It has information
        relating to both threshold masking and polygon masking. 
        It also holds helper functions related to this masking. 
        
        The format that the threshold masking should be stored in 
        is fairly straight forward. Inside of this object is stored
        information on whether to ignore pixels above a certain 
        value (the greater than pixel mask) and whether to store pixels
        below a certain value (the less than pixel mask). To store this
        information, the object holds the following information:

          doGreaterThanMask    - A boolean value for whether or not 
                                 to do the greater than pixel mask
                                 when analyzing diffraction data.
                                 Technically, this stores an integer
                                 with value 1 or 0 since this is 
                                 an old version of Python.
          greaterThanMask      - The value that pixels can't be 
                                 greater than.
          greaterThanMaskColor - The color that these too high pixels 
                                 should be colored. The format of 
                                 this value is a string which 
                                 Tkinter() can read.
          doLessThanMask       - A boolean value for whether or not
                                 to do the less than pixel mask.
          lessThanMask         - The value that pixels can't be less
                                 than.
          lessThanMaskColor    - The color of these pixels.


        These objects should be accessed directly without any 
        getter and setter methods (because I am too lazy for
        my own good). But there are also two convenience functions
        for them. They are

            getLessThanMaskColorRGB()    - Returns the RGB integer 
                                           values (from 0 to 255) 
                                           for the less than 
                                           mask's color as a tuple.
            getGreaterThanMaskColorRGB()  - Returns the corresponding 
                                           values for the greater 
                                           than mask's color.
        
        The information about polygon masking is a bit more complicated
        and obfuscated. But first off, we have

            doPolygonMask    - A boolean for whether or not to
                               do the polygon mask when analyzing 
                               diffraction data.
            polygonMaskColor - The color that these polygon masks will
                               be drawn as.

        and there is a corresponding getPolygonMaskColorRGB() which
        does just what you would expect.
        
        But the actual polygons are stored in a weird manner.
        They are stored in 4 Numeric arrays. And yes, there can be
        multiple polygons stored inside this data.

            polygonsX              - The x coordinates of all the points
                                     of all the polygons. So the 
                                     coordinates for each polygon
                                     are just placed next to each other.
                                     So the total number of items is
                                     this array is just the total number
                                     of nodes for all the polygons
            polygonsY              - The same for the y coordinates.
            polygonBeginningsIndex - An array containing the index in
                                     polygonsX or polygonsY where the
                                     particular polygon begins. The
                                     number of items in this array
                                     is just the number of polygons.
            polygonNumberOfItems   - An array containing the number of 
                                     vertices (or itmes) in a particular 
                                     polygon. The polygonBeginningsIndex
                                     and polygonNumberOfItems index are
                                     syncronized so that the same index
                                     into these arrays gets the index
                                     and number of items for the same
                                     polygon.

        By the way, the reason I did this was because I needed to 
        be able to pass these polygons into C code so that I could
        quickly use them to do data analysis. And C dosen't allow for
        very flexible file formats, so I figured this was the easiest
        and most transparent way to do things. Also, I am using
        a particular C algorithm to test if a point is inside of 
        one of these polygons which required the data be separated
        into x and y arrays.

        To make things a little clearer, here is a simple example:
        First, we will create one of these objects. Note that
        you have to pass in some Tkinter object to this class. 
        Any will do.

            >>> from Tkinter import Label
            >>> # You just have to pass in some Tk widget
            >>> o = MaskedPixelInfo(Label()) 

        Now we can add polygons to the object. The polygon that
        you pass must be of the form [x1,y1, x2,y2, ... ]
        So here we are adding a polygon with the coordinates
        (0,0), (30,30), and (30,0). 
            
            >>> o.addPolygon([0,0,30,30,30,0])
            >>> print o.polygonsX 
            [  0.  30.  30.]
            >>> print o.polygonsY 
            [  0.  30.   0.]
            >>> print o.polygonBeginningsIndex 
            [0]
            >>> print o.polygonNumberOfItems 
            [3]

        We can now add another polygon with the coordinates
        (100,100), (100, 200), (200, 200), (200, 100). 

            >>> o.addPolygon([100,100,100,200,200,200,200,100]) 
            >>> print o.polygonsX 
            [   0.   30.   30.  100.  100.  200.  200.]
            >>> print o.polygonsY 
            [   0.   30.    0.  100.  200.  200.  100.]
            >>> print o.polygonBeginningsIndex 
            [0 3]
            >>> print o.polygonNumberOfItems 
            [3 4]

        Here, we see that that we have put into our object 2 polygons,
        one of them with the coordinates [(0,0), (30,30), (30,0)] and
        the other with coordinates [(100,100), (100, 200), (200, 200), 
        (200, 100)]. The polygonsX holds all the x coordinates. The
        polygonsY holds all the y coordinates. The polygonBeginningsIndex 
        and polygonNumberOfItems that the first polygon begins at index 0
        and has 3 items and that the second starts at index 3 and holds
        4 items. This is exactly what we expect.

        We can do some useful this with these polygons using this object's
        functions. First, numPolyogns() returns
            
            >>> print o.numPolygons()
            2

        We also have a function which returns a polygon that inhabits 
        a particular area. It returns the polygon in list form if it
        finds it. If it dose not find it, it returns None.

            >>> o.getPolygon(150, 150)
            [100.0, 100.0, 100.0, 200.0, 200.0, 200.0, 200.0, 100.0]
            >>> print o.getPolygon(10000, 10000)
            None

        If the point has several polygons overlapping it, the function
        will return the polygon earliest in the list. We can also remove
        the polygon inhabiting a particular point. It whatever polygon
        is gotten at that particular point will also be removed by a
        corresponding call to removePolygon(). If removePolygon finds
        a polygon to remove, it returns 1. If it dose not, it will 
        return 0.

            >>> o.removePolygon(10000, 10000)
            0
            >>> o.removePolygon(150,150)
            1
            >>> print o.polygonsX 
            [  0.  30.  30.]
            >>> print o.polygonsY 
            [  0.  30.   0.]
            >>> print o.polygonBeginningsIndex 
            [0]
            >>> print o.polygonNumberOfItems 
            [3]
        
        See how we got rid of that square polygon and are back to the 
        first one. , We can call removePolygons to delete all the polygons
        in the object. Once we do this, the polygon arrays will be empty
            
            >>> o.removePolygons()
            >>> print o.polygonsX 
            zeros((0,), 'd')
            >>> print o.polygonsY 
            zeros((0,), 'd')
            >>> print o.polygonBeginningsIndex 
            zeros((0,), 'l')
            >>> print o.polygonNumberOfItems 
            zeros((0,), 'l')

        """

    # The threshold masking variables

    # any Tk widget will do. We just need a witdget
    # so that the winfo_rgb() function can be called on
    # it to convert to RGB values.
    widget = None

    doLessThanMask = None
    lessThanMask = None
    lessThanMaskColor = None

    doGreaterThanMask = None
    greaterThanMask = None
    greaterThanMaskColor = None

    # The polygon masking variables

    doPolygonMask = None
    polygonMaskColor = None

    polygonsX = Numeric.array([ ],Numeric.Float)
    polygonsY = Numeric.array([ ],Numeric.Float)
    polygonBeginningsIndex = Numeric.array([ ],Numeric.Int)
    polygonNumberOfItems = Numeric.array([ ],Numeric.Int)

    def getPolygon(self,x,y):
        """ Returns the polygon that fills the coordinate x, y. 
            What is returned is a list of the form 
            (x1, y1, x2, y2, ...). If there is no polyon, 
            None is returned. If there are multiple polygons, 
            the polygon with the lowest index (first polygon in 
            the list) is returned. """

        whichPolygon = insideWhichPolygon(self.polygonsX,
                self.polygonsY,self.polygonBeginningsIndex,
                self.polygonNumberOfItems,x,y)

        # note inside any polygon
        if whichPolygon == -1:
            return None

        index = self.polygonBeginningsIndex[whichPolygon]
        numberOfItems = self.polygonNumberOfItems[whichPolygon]

        polygon = []

        # pull out just the interesting polygon and flatten it
        # so it can easily be displayed
        for i in range(numberOfItems):
            polygon += self.polygonsX[index+i],self.polygonsY[index+i]

        return polygon

    def removePolygon(self,x,y):
        """ Removes the polygon that fills the coordinate x, y
            If there are multiple polygons, the polygon with
            the lowest index (first polygon in the list) is 
            returned. Returns 1 if a polygon was acutally removed.
            0 is returned otherwise. """
            

        whichPolygon = insideWhichPolygon(self.polygonsX,self.polygonsY,
                self.polygonBeginningsIndex,self.polygonNumberOfItems,x,y)

        # No polygon to delete, so do nothing
        if whichPolygon == -1:
            return 0

        index = self.polygonBeginningsIndex[whichPolygon]
        numberOfItems = self.polygonNumberOfItems[whichPolygon]

        oldSize = self.polygonsX.shape[0]
        newSize = oldSize - numberOfItems

        newPolygonsX = Numeric.zeros( (newSize,) ,Numeric.Float)
        newPolygonsY = Numeric.zeros( (newSize,) ,Numeric.Float)

        # remove the offending polygon
        newPolygonsX[0:index] = self.polygonsX[0:index]
        newPolygonsX[index:] = self.polygonsX[index+numberOfItems:]

        newPolygonsY[0:index] = self.polygonsY[0:index]
        newPolygonsY[index:] = self.polygonsY[index+numberOfItems:]

        oldNumberOfPolygons = self.polygonNumberOfItems.shape[0]
        newNumberOfPolygons = oldNumberOfPolygons-1

        newPolygonBeginningsIndex = Numeric.zeros( (newNumberOfPolygons,) ,Numeric.Int)
        newPolygonNumberOfItems = Numeric.zeros( (newNumberOfPolygons,) ,Numeric.Int)

        newPolygonBeginningsIndex[0:whichPolygon]  = \
                self.polygonBeginningsIndex[0:whichPolygon]

        # note that the indicies of the items after the offending
        # polygon need to be modified to affect the new array
        newPolygonBeginningsIndex[whichPolygon:]  = \
                (self.polygonBeginningsIndex[whichPolygon+1:]-numberOfItems)

        newPolygonNumberOfItems[0:whichPolygon]  = \
                self.polygonNumberOfItems[0:whichPolygon]

        newPolygonNumberOfItems[whichPolygon:]  = \
                self.polygonNumberOfItems[whichPolygon+1:]

        self.polygonsX = newPolygonsX 
        self.polygonsY = newPolygonsY 
        self.polygonBeginningsIndex = newPolygonBeginningsIndex 
        self.polygonNumberOfItems = newPolygonNumberOfItems 

        return 1

    def numPolygons(self):
        """ Returns the number of polygons stored in this
            object. """
        return self.polygonNumberOfItems.shape[0] 


    def removePolygons(self):
        """ Remove all the polygons from the object. """

        self.polygonsX = Numeric.array([ ],Numeric.Float)
        self.polygonsY = Numeric.array([ ],Numeric.Float)
        self.polygonBeginningsIndex = Numeric.array([ ],Numeric.Int)
        self.polygonNumberOfItems = Numeric.array([ ],Numeric.Int)

    def addPolygon(self,polygon):
        """ Adds a polygon to the objects. The polygon should be 
            a list of the form (x1,y1,x2,y2, ...) """
        if len(polygon) % 2 != 0:
            raise Exception("Cannot add polygon because the number of x cordinates and y cordinates are not equal.")

        # No reason to add a polygon with no area
        if len(polygon) <= 4:
            return

        polygonLength = len(polygon)/2

        oldsize=self.polygonsX.shape[0]

        # resize the list of x coordinates
        self.polygonsX=Numeric.resize(self.polygonsX, 
                (oldsize + polygonLength,) )
        # add in the x coordinates
        for i in range(polygonLength):
            self.polygonsX[oldsize + i]=polygon[2*i + 0]

        # do the same with the y coordinates
        self.polygonsY=Numeric.resize(self.polygonsY, 
                (oldsize + polygonLength,) )

        for i in range(polygonLength):
            self.polygonsY[oldsize+i]=polygon[2*i + 1]

        self.polygonBeginningsIndex=Numeric.resize(self.polygonBeginningsIndex, 
                (self.polygonBeginningsIndex.shape[0] + 1,) )
        self.polygonBeginningsIndex[-1] = oldsize

        self.polygonNumberOfItems=Numeric.resize(self.polygonNumberOfItems, 
                (self.polygonNumberOfItems.shape[0] + 1,) )
        self.polygonNumberOfItems[-1] = polygonLength



    def __init__(self,widget):
        self.widget = widget

    def __ne__(self,other):
        return not self.__eq__(other)

    def array_equals(first,second):
        # this is horribly inefficient (and probably not general), 
        # but I can't find a better way to do this comparison
        return first.tolist() == second.tolist()

    def __eq__(self,other):
        """ Test the equality of the masked pixel info.
            If one of the arrays is really None, the equality 
            is false. Otherwise, equality holds if all the 
            lessThanMask and greaterThanMask parameters and all
            the pixel mask parameters are the same. """

        # sometimes None is passed as the other item, 
        # in which case we just say they are not equal
        if type(self) == type(None) or type(other) == type(None):
            return 0

        # check all the threshold masking parameters
        if self.doLessThanMask != other.doLessThanMask or \
                self.lessThanMask != other.lessThanMask or \
                self.lessThanMaskColor != other.lessThanMaskColor or \
                self.doGreaterThanMask != other.doGreaterThanMask or \
                self.greaterThanMask != other.greaterThanMask or \
                self.greaterThanMaskColor != other.greaterThanMaskColor: 
            return 0

        # if there are no polygons, it dose not matter if the color of
        # them or whether to 'do them' is different. So we just 
        # call the objects equal anyway by convention
        if self.numPolygons() == 0 and other.numPolygons() == 0:
            return 1

        # otherwise, we have to check if all the other 
        if  not numeric_array_equals(self.polygonsX,other.polygonsX) or \
            not numeric_array_equals(self.polygonsY,other.polygonsY) or \
            not numeric_array_equals(self.polygonBeginningsIndex,other.polygonBeginningsIndex) or \
            not numeric_array_equals(self.polygonNumberOfItems,other.polygonNumberOfItems) or \
            self.polygonMaskColor != other.polygonMaskColor or \
            self.doPolygonMask != other.doPolygonMask:
            return 0

        return 1

    def getLessThanMaskColorRGB(self):
        """ Returns the RGB values for the less than
            mask color as a tuple. Each of r,g,b is
            an integer from 0 to 255. """
        if self.lessThanMaskColor == None:
            raise Exception("Cannot calculate the RGB value of the less than mask because no less than mask color has been set.")
        return self.widget.winfo_rgb(self.lessThanMaskColor)


    def getGreaterThanMaskColorRGB(self):
        """ Returns the RGB values for the greater than
            mask color as a tuple. Each of r,g,b is
            an integer from 0 to 255. """
        if self.greaterThanMaskColor == None:
            raise Exception("Cannot calculate the RGB value of the greater than mask because no greater than mask color has been set.")
        (r,g,b) = self.widget.winfo_rgb(self.greaterThanMaskColor)
        return (r/256,g/256,b/256)

    def getPolygonMaskColorRGB(self):
        """ Returns the RGB values for the polygon 
            mask color as a tuple. Each of r,g,b is
            an integer from 0 to 255. """
        if self.polygonMaskColor == None:
            raise Exception("Cannot calculate the RGB value of the polygon mask because no polygon mask color has been set.")
        (r,g,b) = self.widget.winfo_rgb(self.polygonMaskColor)
        return (r/256,g/256,b/256)


    def loadPolygonsFromFile(self,filename):
        """ This function reads in one or more polygons
            from a file and stores them in the object
            along with any other polygons already
            stored in the object. """

        print 'file = ',filename

        file = open(filename,'r')

        currentPolygon = []

        line = file.readline()
        while line:
            # remove comments from the line  
            line = line.split('#')[0]
            line = line.strip()

            # Any blank or comment lines signify a new polygon
            if line == '':
                # add in the previous polygon (if possible) and start a new one.

                if currentPolygon != []:
                    # if a polygon was stored from before 
                    # then add the polygon to the file

                    if len(currentPolygon) <= 4:
                        # if we found less then 3 polygon coordinates before a break,
                        # raise an error because all polygons need 3 coordinates
                        raise UserInputExcpetion('"%s" is not a valid polygon file because one of the polygon has fewer then 3 coordinates.' % (filename))

                    self.addPolygon(currentPolygon)

                    currentPolygon = [] # reset polygon 

            else:
                # otherwise, read the next pair of coordinates in
                pair = line.split()
                if len(pair) != 2:
                    raise UserInputException('"%s" is not a valid line in the polygon file %s. Polygon lines should only have the x coordinate followed by the y coordinate with only spaces between them.' % (line,filename))

                try:
                    currentPolygon += (float(pair[0]), float(pair[1]))
                except:
                    raise UserInputException('"%s" is not a valid line in the polygon file %s. Polygon lines need to have valid numbers for the x and y coordinate.' % (line,filename))

            line = file.readline()


        # there could be one final polygon to store in the file

        if currentPolygon != []:

            if len(currentPolygon) <= 4:
                # if we found less then 3 polygon coordinates before a break,
                # raise an error because all polygons need 3 coordinates
                raise UserInputExcpetion('"%s" is not a valid polygon file because one of the polygon has fewer then 3 coordinates.' % (filename))

            self.addPolygon(currentPolygon)

            currentPolygon = [] # reset polygon

    def savePolygonsToFile(self,filename):
        if self.numPolygons() < 1: 
            raise UserInputException("Cannot save polygons to a file until there are polygons to save.")
        file = open(filename,'w')
        file.write("# Polygon(s) drawn on "+time.asctime()+"\n")
        for i in range(self.polygonBeginningsIndex.shape[0]):
            index = self.polygonBeginningsIndex[i] 
            size = self.polygonNumberOfItems[i] 

            for j in range(size):
                file.write(str(self.polygonsX[index+j])+
                        '\t'+str(self.polygonsY[index+j])+'\n')
            file.write('\n')

    def printPolygons(self):
        """ A convenience function for debugging. """

        print 'polygonsX = ',self.polygonsX 
        print 'polygonsY = ',self.polygonsY 
        print 'beginning index = ',self.polygonBeginningsIndex 
        print 'number of items = ',self.polygonNumberOfItems 
    
    def writePolygonCommentString(self):
        string = "# Polygon(s) used in the analysis:\n"

        for i in range(self.polygonBeginningsIndex.shape[0]):
            index = self.polygonBeginningsIndex[i]
            size = self.polygonNumberOfItems[i]
            for j in range(size):
                string = string + "#   "+str(self.polygonsX[index+j]) + \
                        '\t'+str(self.polygonsY[index+j])+'\n'
            string += '#\n'
        return string                



def test():
    import doctest
    import MaskedPixelInfo
    doctest.testmod(MaskedPixelInfo,verbose=0)

if __name__ == "__main__":
    test()
