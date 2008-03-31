
def test():
    import doctest

    print 'testing CalibrationData...'
    import CalibrationData
    doctest.testmod(CalibrationData,verbose=0,report=1)

    print 'testing QData...'
    import QData
    doctest.testmod(QData,verbose=0,report=1)

    print 'Testing Transform...'
    import Transform
    doctest.testmod(Transform,verbose=0,report=1)

    print 'Testing General...'
    import General
    doctest.testmod(General,verbose=0,report=1)

    print 'Testing Reduce...'
    import Reduce
    doctest.testmod(Reduce,verbose=0,report=1)
        
if __name__ == "__main__":
    test()
 
