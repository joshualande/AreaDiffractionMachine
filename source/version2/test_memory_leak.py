from Reduce import Reduce
from ColorMaps import ColorMaps
from Numeric import zeros,Float64
from Cake import Cake

counter = 0
maps = ColorMaps('colormaps.txt')

filename = "/home/jolande/data/LaB623_14_03.mar2300"


object = Reduce(filename)
cal = object.calibrationDataFromHeader()
cal.setAlpha(0)
cal.setBeta(0)
cal.setRotation(0)


while 1:
    counter += 1
    print counter

    #object.getCakeImage(cal,0,5,1000,0,360,1000,0,0,None,None,maps,'bone',0,1)
    #array = zeros( (1000,1000), Float64)
    #object.saveCakeData('/home/jolande/data/temp.dat',cal,0,5,1000,0,360,1000,0,0)
    
    #data = Cake(object.diffractionData.data,cal,0,5,1000,0,360,1000,0,0)
    #image = data.getImage(0,1,0,maps,'bone',0)

    object.getDiffractionImage(maps,'bone')

    #object.integrateQI(cal,0,5,10000000,0,0,0,0,0,'')
