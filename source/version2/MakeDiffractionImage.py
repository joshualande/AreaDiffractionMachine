import os
import PIL
import Image
import ImageDraw
import Numeric
from General import frange,avgVal
import Transform
import DrawWrap


def getDiffractionImage(data,lowerBound,upperBound,logScale,
        colorMaps,colorMapName,maskedPixelInfo,
        doScaleFactor,scaleFactor,
        setMinMax,minIntensity,
        maxIntensity,invert=None):

    mode = "RGB"

    if maskedPixelInfo.doLessThanMask:
        (lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB) = \
                maskedPixelInfo.getLessThanMaskColorRGB()
        lessThanMask = maskedPixelInfo.lessThanMask
    else:
        # We can just send the function a bunch of junk since it won't be used
        (lessThanMaskColorR,lessThanMaskColorG,lessThanMaskColorB) = (0,0,0) 
        lessThanMask = -1

    if maskedPixelInfo.doGreaterThanMask:
        (greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB) = \
                maskedPixelInfo.getGreaterThanMaskColorRGB()
        greaterThanMask = maskedPixelInfo.greaterThanMask
    else:
        (greaterThanMaskColorR,greaterThanMaskColorG,greaterThanMaskColorB) = (0,0,0)
        greaterThanMask = -1

    if maskedPixelInfo.doPolygonMask:
        (polygonMaskColorR,polygonMaskColorG,polygonMaskColorB) = \
                maskedPixelInfo.getPolygonMaskColorRGB()
        polygonsX = maskedPixelInfo.polygonsX
        polygonsY = maskedPixelInfo.polygonsY
        polygonBeginningsIndex = maskedPixelInfo.polygonBeginningsIndex
        polygonNumberOfItems = maskedPixelInfo.polygonNumberOfItems

    else:
        (polygonMaskColorR,polygonMaskColorG,polygonMaskColorB) = (0,0,0) 
        polygonsX = Numeric.array([])
        polygonsY = Numeric.array([])
        polygonBeginningsIndex = Numeric.array([])
        polygonNumberOfItems = Numeric.array([])

    palette = colorMaps.getPalette(colorMapName,invert=invert)
    string = DrawWrap.getDiffractionImageString(data,lowerBound,
            upperBound, 
            logScale, 
            palette, 
            maskedPixelInfo.doLessThanMask,
            lessThanMask, 
            lessThanMaskColorR, 
            lessThanMaskColorG,
            lessThanMaskColorB, 
            maskedPixelInfo.doGreaterThanMask,
            greaterThanMask, 
            greaterThanMaskColorR,
            greaterThanMaskColorG, 
            greaterThanMaskColorB,
            maskedPixelInfo.doPolygonMask,
            polygonsX,
            polygonsY,
            polygonBeginningsIndex,
            polygonNumberOfItems,
            polygonMaskColorR,
            polygonMaskColorG,
            polygonMaskColorB,
            doScaleFactor,
            scaleFactor,
            setMinMax,
            minIntensity,
            maxIntensity)

    img = Image.fromstring(mode,(data.shape[0],data.shape[1]),string)
    img = img.rotate(90)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    return img


def addPeaksDiffractionImage(image,peakList,maskedPixelInfo,color):
    draw = ImageDraw.Draw(image)

    halflength = 15
    for x,y,qReal,qFit,chi,width in peakList.getMaskedPeakList(maskedPixelInfo):
        draw.line((x-halflength,y-halflength) + (x+halflength,y+halflength),fill=color)
        draw.line((x+halflength,y-halflength) + (x-halflength,y+halflength),fill=color)


def addConstantQLineDiffractionImage(image,Q,calibrationData,color):
    draw = ImageDraw.Draw(image)

    polygon = []
    for chi in frange(0,360,3):
        x,y = Transform.getXY(calibrationData,Q,chi)
        polygon += [x,y]

    draw.polygon(polygon, outline=color)
