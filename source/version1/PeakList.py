import Numeric

class PeakList:
    r""" An object for dealing with peaks to the diffraction data.
        This function should just keep things easy. The main
        reason that this is nice is that it takes care of ignoring
        all the peaks that are masked. """

    def __init__(self):
        self.peakList = []

    def addPeak(self,x,y,Q,qFit,chi,width):
        """ Adds a peak to the peak list. """
        self.peakList.append([x,y,Q,qFit,chi,width])


    def getMaskedPeakList(self,maskedPixelInfo):
        """ Returns all the diffraction peaks that
            are not masked. """

        maskedPeakList = []

        for peak in self.peakList:
            xPeak,yPeak,Qreal,Qfit,chi,width = peak

            # make sure not to include any peaks inside the image
            if maskedPixelInfo.doPolygonMask and \
                    maskedPixelInfo.isInPolygons(xPeak,yPeak):
                continue
            maskedPeakList.append(peak)

        return maskedPeakList


    def getMaskedPeakArrays(self,maskedPixelInfo,data):
        """ Returns nice Numeric data strucure to store all of the peaks.
            Each attribute gets its own numeric array, same index means
            same peak."""

        # it is more conveniet to call the getMaskedPeakList()
        # function first so that we can eaisly calculate how
        # many masked peaks there are before creating the arrays.
        maskedPeakList = self.getMaskedPeakList(maskedPixelInfo)

        length = len(maskedPeakList)
        xValues = Numeric.zeros( (length), Numeric.Float64 )
        yValues = Numeric.zeros( (length), Numeric.Float64 )
        qReal = Numeric.zeros( (length), Numeric.Float64 )
        chi = Numeric.zeros( (length), Numeric.Float64 )
        width = Numeric.zeros( (length), Numeric.Float64 )
        intensity = Numeric.zeros( (length), Numeric.Float64 )

        for peakIndex in range(len(maskedPeakList)):
            xPeakLoop,yPeakLoop,QrealLoop,QfitLoop,chiLoop,widthLoop = maskedPeakList[peakIndex]
            xValues[peakIndex] =  xPeakLoop
            yValues[peakIndex] = yPeakLoop
            qReal[peakIndex] = QrealLoop
            chi[peakIndex] = chiLoop
            width[peakIndex] = widthLoop
            intensity[peakIndex] = data[int(xPeakLoop)][int(yPeakLoop)]

        return xValues,yValues,qReal,chi,width,intensity

