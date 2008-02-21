""" Here are some general routines that make my life easier. 
    There is no particular reason to put them anywhere else. """

import os
import Numeric

from Exceptions import UserInputException

def getStringFromList(list):
    """ Returns a string made up out of a list by removing 
        traling and leading white space from each of the 
        list items and putting a comma between them. 
            
            >>> getStringFromList( ('a', '   b ', 'c    ') )
            'a, b, c'
        """
    string = ''
    for index in range(len(list)-1):
        string+=list[index].strip()+', '
    string +=list[len(list)-1].strip()
    return string


def getListFromString(string):
    """ Returns a list forma  string of items split by commas.
        It will also remove anyt trailing and leading white
        spcae from each of the list items. 

            >>> getListFromString('a, b, c')
            ['a', 'b', 'c']
        """
    list = string.split(',')
    for index in range(len(list)):
        list[index] = list[index].strip()
    return list


def maxListIndex(list):
    """ Returns the index of the largest item in a python list. 

            >>> maxListIndex([0,1,5,2,1])
            2
            >>> maxListIndex([0])
            0
            >>> maxListIndex([10,0,5,-10])
            0
            >>> maxListIndex([])
            Traceback (most recent call last):
                ...
            Exception: Cannot find the max index of the list because there is no data in the list.
    """
    if len(list) < 1:
        raise Exception("Cannot find the max index of the list because there is no data in the list.")
    index = 0
    for loop in range(1,len(list)):
        if list[loop] > list[index]: 
            index = loop

    return index
        

def avgList(list):
    """ Returns the average value of a python list. 

            >>> print "%.5f" % avgList([1,2,3,4,0])
            2.00000
            >>> print "%.5f" % avgList([1,3])
            2.00000
    """
    return 1.0*sumList(list)/len(list)


def sumList(data):
    """ Returns the sum of a python list. 
        
            >>> sumList( [1, 2, 3, 4] )
            10
            >>> print "%.5f" % sumList( (1.1, 2.2, 3.3) )
            6.60000
    """
    sum = 0
    for loop in data:
        sum += loop

    return sum


def maxArray(data):
    """ Returns the largest item in a numeric array. 

            >>> array = Numeric.array( [[1, 2, 5],[ 3, 7, 2]] )
            >>> maxArray(array)
            7
            >>> array[1,1] = 1
            >>> print array
            [[1 2 5]
             [3 1 2]]
            >>> maxArray(array)
            5
    """
    if len(data.shape) != 2:
        raise Exception('maxArray() must be called with a 2 dimensional array.')
    max = 0
    rows,columns = data.shape
    for rowLoop in range(rows):
        for columnLoop in range(columns):
            if data[rowLoop][columnLoop] > max: 
                max=data[rowLoop][columnLoop]
    return max

def avgVal(data):
    """ Calculates the average of all the data in a 2 dimensional numeric array. 

            >>> import Numeric
            >>> data = Numeric.array([[1,2,3],[4,0,5]])
            >>> print "%.5f" % avgVal(data)
            2.00000
            >>> data = Numeric.array([[1,3]])
            >>> print "%.5f" % avgVal(data)
            2.00000
    """
    return Numeric.sum(Numeric.sum(data))/(data.shape[0]*data.shape[1])


def frange(start, end=None, inc=1.0):
    """ A range function, that does accept float increments.

            >>> frange(1,3,1)
            [1.0, 2.0, 3.0]

        frange() must have a nonzero increment:

            >>> frange(1,3,0)
            Traceback (most recent call last):
                ...
            Exception: The increment to frange() must be > 0

        With no increment given, frange() will default to 0:

            >>> frange(1,3)
            [1.0, 2.0, 3.0]
            >>> frange(1,3.9)
            [1.0, 2.0, 3.0]
            >>> frange(2,3)
            [2.0, 3.0]

        You can change the increment values to frange()

            >>> frange(1,4,1.5)
            [1.0, 2.5, 4.0]

        With 1 argument, frange() starts at 0.0 with an increment of 1.0
            
            >>> frange(3)
            [0.0, 1.0, 2.0, 3.0]
    """

    if inc == 0.0:
        raise Exception("The increment to frange() must be > 0")
    if end == None:
        end = start + 0.0
        start = 0.0
    L = []

    start=float(start)
    end=float(end)
    inc=float(inc)
    next=start
    while 1:
        if inc > 0 and next > end: break
        elif inc < 0 and next < end: break
        L.append(next)
        next+=inc

    return L

# these functions came from the following message board discussion:
# http://www.thescripts.com/forum/thread20420.html
# I think they are fair game to use. They have also been slightly modified
def peek(file, cnt=1):
    data = file.read(cnt)
    file.seek(cnt * -1, 1)
    return data

def peekline(file):
    pos = file.tell()
    data = file.readline()
    file.seek(pos, 0)
    return data


def peeksecondline(file):
    pos = file.tell()
    # read the first line
    file.readline() 
    # then, return the second line
    data = file.readline()
    file.seek(pos, 0)
    return data

def numeric_array_equals(first,second):
    """ Tests if two numeric arrays are equal where
        equality is defined as all the elements of both
        arrays being the same. This algorith is 
        horribly inefficient (and probably not very 
        general, but I can't find a better way to do 
        this comparison. """
    return first.tolist() == second.tolist()


def splitPaths(string):
    """ Takes in a string of file names and folder names that are
        separated by spaces and returns a list of file names. This
        would seem like a stupid function because split() would do
        the job just as well, but this function is special in that
        it can deal with filenames with spaces in them. If some of
        the file names are not real files existing in teh computer, 
        an exception is raised. 

        Note that there is a 'bug' in the algorithm where it will not
        recognize real files with spaces at the end of the file.
        But seriously, I have never seen a file seriously do this.
        
        These doctests are too unix-ish and will fail on a windows machine.
        But they are good enough to convince me the function works for now.

            >>> import tempfile
            >>> dir = tempfile.mkdtemp() 
            >>> os.popen("touch '%s/a file.txt'" % dir).close()
            >>> os.popen("touch '%s/a nother file'" % dir).close()
            >>> os.popen("mkdir '%s/temp folder/'" % dir).close()
            >>> os.popen("touch '%s/temp folder/some final file'" % dir).close()
            >>> string = '   %s  %s/ %s/a file.txt %s/a nother file  %s/temp folder %s/temp folder/ %s/temp folder/some final file' % (dir,dir,dir,dir,dir,dir,dir)
            >>> split = splitPaths(string)
            >>> expected = ['%s' % dir, '%s/' % dir, '%s/a file.txt' % dir, '%s/a nother file' % dir, '%s/temp folder' % dir, '%s/temp folder/' % dir, '%s/temp folder/some final file' % dir]
            >>> split == expected
            True
    """ 

    # split on newline into chunks separated by spaces
    list = string.strip().split(' ')
    filesOrDirectories = []

    # loop through all the chunks of the string
    while len(list)>0:
        filename = list.pop(0)
        
        # if there were several spaces between a filename, some of the 'chunks'
        # will be blank characters, so we should just ignore them and move 
        # along
        if filename == '':
            continue
        # If the current chunk is not a valid path name, append the next chunk 
        while not os.path.exists(filename):
            if len(list) < 1:
                raise UserInputException("'%s' cannot be split into a bunch of file names becaues the name '%s' (or possibly some earlier chunks of it) does does not exist." % (filename,filename))
            # add the next item, remembering that the split removed 
            # the space so we have to explicitly add it back in.
            filename = filename + ' ' + list.pop(0)

        # add the valid path we found
        filesOrDirectories.append(filename)

    return filesOrDirectories 


def test():
    import doctest
    import General
    doctest.testmod(General,verbose=0)
        
if __name__ == "__main__":
    test()
 
