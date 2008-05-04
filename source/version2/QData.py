import Numeric
import math
from Exceptions import UserInputException

class QData:
    r"""This class provides the ability to store a list of Q and delta Q
        values. Each Q and delta Q value defines a Q range from Q-delta Q 
        to Q+delta Q. The object enforces that none of the Q ranges overlap.
        This object provides several useful functions for
        dealing with this Q data. To input Q values, you can use the 
        function addQPair() where the 2 inputs are Q and delta Q.
        In particular, fromFile() allows you to
        read in the Q data from a data file in the following format:
        +-------------------+
        |Q  dQ              |
        |1  .1              |
        |2  .15             |
        |3  .1              |
        +-------------------+
        Alternately, the first line can be of the form "Q   delta Q".
        fromFile() will reset any already stored Q values from the object.
        Furthermore, this object is capable of dealing with D where
        D is defined as D=2*pi/Q. You can use addDPair() to add D and
        delta D values and if a data file's first line is "D    dD", then
        this object will read in D values instead. The object does the
        conversions so that you always get Q values out of the object.
        To convert dD to dQ values, we use the formula dQ = 2*pi*dD/D^2
        as can be derived by differentiation.

        Other useful objects include next(), which will return array with
        a Q pair. next() will loop through all the Q pairs in order,
        returning the lowest Q value first. getAllQPairs() will return
        a list of lists of Q values. isInQRange(Q) takes in a Q value
        and returns 1 if that Q values falls within the range of one of
        the pairs and 0 otherwise. 
        >>> data = QData()
        >>> data.addQPair(2.02,.3)
        >>> data.addQPair(1.01,0.2)
        >>> data.addQPair(1.5,0.1)
        >>> data.length()
        3
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.0100000000,0.2000000000
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.5000000000,0.1000000000
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        2.0200000000,0.3000000000
        >>> data.next()
        ''
        >>> next = data.next() # make sure it goes back to the beginning
        >>> len(next) 
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.0100000000,0.2000000000
        >>> for pair in data.getAllQPairs():
        ...     print "%.10f,%.10f" % (pair[0],pair[1])
        1.0100000000,0.2000000000
        1.5000000000,0.1000000000
        2.0200000000,0.3000000000
        >>> for Q in data.getAllQValues():
        ...     print "%.10f" % Q
        1.0100000000
        1.5000000000
        2.0200000000
        >>> import tempfile
        >>> tempFile = tempfile.mktemp()
        >>> file = open(tempFile,'w')
        >>> file.write('q\tdelta q #comments\n')
        >>> file.write('2.02\t0.3\n')
        >>> file.write('#2.02\t0.3\n')
        >>> file.write('1.01\t0.2\n')
        >>> file.write('1.5\t0.1\n')
        >>> file.close()
        >>> data = QData(tempFile)
        >>> data.length()
        3
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.0100000000,0.2000000000
        >>> data = QData()
        >>> data.getAllQPairs()
        []
        >>> data.fromFile(tempFile)
        >>> data.length()
        3
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.0100000000,0.2000000000
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.5000000000,0.1000000000
        >>> next = data.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        2.0200000000,0.3000000000
        >>> data.next()
        ''
        >>> next = data.next() # make sure it goes back to the beginning
        >>> len(next) 
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        1.0100000000,0.2000000000
        >>> data.isInQRange(2.31)
        1
        >>> data.isInQRange(2.33)
        0
        >>> data.isInQRange(0.805)
        0
        >>> data.isInQRange(0.811)
        1
        >>> data.addQPair(5,10)
        Traceback (most recent call last):
          File "C:\Program Files\Python21\lib\doctest.py", line 499, in _run_examples_inner
            exec compile(source, "<string>", "single") in globs
          File "<string>", line 1, in ?
          File "QData.py", line 259, in addQPair
            raise UserInputException("Error, cannot complete fucntion addQPair because the input pair (%f,%f) overlaps the pair (%f,%f)" % (Q,dQ,QLoop,dQLoop))
        UserInputException: 'Error, cannot complete fucntion addQPair because the input pair (5.000000,10.000000) overlaps the pair (1.010000,0.200000)'
        >>> data2 = QData()
        >>> data2.getAllQPairs()
        []
        >>> data2.addDPair(1.0,.1)
        >>> data2.addDPair(2.0,.2)
        >>> next = data2.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        3.1415926536,0.3141592654
        >>> next = data2.next()
        >>> len(next)
        2
        >>> print "%.10f,%.10f" % (next[0],next[1])
        6.2831853072,0.6283185307
        >>> data2.next()
        ''
        >>> data2.addDPair(0.5,10)
        Traceback (most recent call last):
          File "C:\Program Files\Python21\lib\doctest.py", line 499, in _run_examples_inner
            exec compile(source, "<string>", "single") in globs
          File "<string>", line 1, in ?
          File "QData.py", line 274, in addDPair
            self.addQPair(Q,dQ)
          File "QData.py", line 262, in addQPair
            raise UserInputException("Error, cannot complete function addQPair because the input pair (%f,%f) overlaps the pair (%f,%f)" % (Q,dQ,QLoop,dQLoop))
        UserInputException: 'Error, cannot complete function addQPair because the input pair (12.566371,251.327412) overlaps the pair (3.141593,0.314159)'
        """

    QList = []
    current = ''

    def __init__(self,fileName=''):
        self.QList = []
        if fileName!='':
            self.fromFile(fileName)
        current = ''

        
    def writeCommentString(self,file):
        """ Writes to a 'file' a comment string which contains \
the values of the diffraction data. """

        file.write("#   %14s%18s\n" % ("Q","Delta Q"))
        for Q,dQ in self.QList:
            file.write("#   %14.10f    %14.10f\n" % (Q,dQ))


    def __str__(self):
        string = "%14s%18s\n" % ("Q","Delta Q")
        for Q,dQ in self.QList:
            string += "%14.10f    %14.10f\n" % (Q,dQ)
        return string


    def fromFile(self,filename):
        self.QList = []
        self.current = ''

        file = open(filename,'rU')

        originalLine = file.readline()
        line = originalLine.split('#')[0].lower()

        # any blank lines should be ignored
        while line == '':
            originalLine = file.readline()
            line = originalLine.split('#')[0].lower()

        words = line.split()
        # remove possible comments

        # Q delta Q, it will be split into ["Q","delta","Q"], so
        # we want to restructure it so that it looks like 
        # ["Q","delta Q"] for easy parsing later.
        if len(words) == 3 and words[1] == "delta":
            words = [ words[0], words[1]+' '+words[2] ]

        if len(words) != 2:
            raise UserInputException('%s is not a proper QData file. \
The first line of the file is "%s" but it should be of the form \
"Q dQ" or "D dD".' % (filename,originalLine) )

        if words[0] == "q":
            if words[1] != "dq" and words[1] != "delta q":
                raise UserInputException('%s is not a proper QData file. \
The first line of the file is "%s" but it should be of the form \
"Q    dQ" or "D   dD".' % (filename,originalLine) )

            line = file.readline()
            while line:
                line = line.split('#')[0]
                if line == '': # if it was a comment line, go on
                    line = file.readline()
                    continue

                words = line.split()
                if len(words)!=2:
                    raise UserInputException('%s is not a proper QData file. \
One of the lines of data does not have exactly 2 numbers (one for the value, \
and one for the uncertainty).' % filename)

                self.addQPair(float(words[0]),float(words[1]) )

                line = file.readline()
            
            # parse in data

        elif words[0] == "d":
            if words[1] != "dd" and words[1] != "delta d":
                raise UserInputException('%s is not a proper QData file. The \
first line of the file is "%s" but it should be of the form "Q    dQ" or \
"D   dD".' % (filename,line) )

            line = file.readline()
            while line:
                # parse
                line = line.split('#')[0]
                if line == '': # if it was a comment line, go on
                    line = file.readline()
                    continue

                words = line.split()
                if len(words)!=2:
                    raise UserInputException('%s is not a proper QData file. \
One of the lines of data does not have exactly 2 numbers (one for the value, \
and one for the uncertainty).' % filename)

                self.addDPair( float(words[0]),float(words[1]) )
                line = file.readline()

        else:
            raise UserInputException('%s is not a proper QData file. The first \
line of the file is "%s" but it should be of the form "Q    dQ" or \
"D   dD".' % (filename,line) )


    def next(self):
        """ This function can be used for iterating through all 
        the Q,dQ pairs. """
        if self.current == '':
            raise UserInputException('Function next() cannot be \
called because no Q values have been entered into the array')

        if self.current >= len(self.QList):
            self.current = 0
            return ''

        val = self.QList[self.current]
        self.current+=1
        return val

    def getAllQPairs(self):
        return self.QList

    def getAllQValues(self):
        list = []
        for Q,dQ in self.QList:
            list.append(Q)
        return list



    def addQPair(self,Q,dQ=0):
        """ Input a pair of Q and delta Q values into the list of Q values. 
            If no delta Q value is given, delta Q's default value is 0.
            Q ranges can not overlap, so if an overlapping Q range is given,
            then an error is raised and the value is not added. """
        if Q<0: 
            raise UserInputException("Error, cannot complete function addQPair because Q<0.")

        # test if Q ranges overlap
        for QLoop, dQLoop in self.getAllQPairs():
            if (QLoop+dQLoop> Q-dQ and QLoop-dQLoop < Q+dQ):
                raise UserInputException("Error, cannot complete fucntion addQPair because the input pair (%f,%f) overlaps the pair (%f,%f)" % (Q,dQ,QLoop,dQLoop))

    
        self.QList.append([Q,dQ])
        self.QList.sort() # sort list so greater Q values are lower in list.
        self.current = 0

    def addDPair(self,D,dD=0):
        """ If input is D and delta D instead of Q and delta Q, then do the right thing.
            If no dD value is given, then dD is defaulted to 0. """
        Q = 2.0*math.pi/D
        dQ = 2.0*math.pi*dD/(D*D) # is this the right conversion formula???
        self.addQPair(Q,dQ)

    def isInQRange(self,Q):
        """ This function looks to see if a given Q value is in the
            range of any of Q ranges inside the object. If it is, 1 
            is returned. Otherwise, 0 is returned. """
        if Q<0: 
            raise UserInputException("Error, cannot complete function addQPair because Q<0.")
        for loop in self.QList:
            if Q<loop[0]+loop[1] and Q>loop[0]-loop[1]:
                return 1
        return 0

    def length(self):
        """ Returns the total number of Q pairs in the object. """
        return len(self.QList)






def test():
    import doctest
    import QData
    doctest.testmod(QData,verbose=1)
        
if __name__ == "__main__":
    test()
