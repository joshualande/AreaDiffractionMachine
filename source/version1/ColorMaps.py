import copy
import Numeric


""" An object to deal with color maps. """
class ColorMaps:

    palettes = None
    
    def __init__(self,filename):
        self.readFile(filename)

    def getColorMapNames(self):
        temp = self.palettes.keys()
        temp.sort()
        return temp
        
    def getPalette(self,name,invert=None):
        if not self.palettes.has_key(name):
            raise Exception("Error finding color map. %s does not exist" % name)

        # to invert image, simply map 0 to 255, 1 to 254, etc by reversing the array
        if invert:
            temp = self.palettes[name]
            # this is the numeric python way of reversing an array
            return temp[temp.shape[0]::-1]

        return self.palettes[name]

    def readFile(self,colorMapFile):
        """ Reads in a color map file and stores the values for later. """
        self.palettes={}

        file=open(colorMapFile,'rU')

        name=file.readline()
        while name != '':

            if name == '\n':
                name = file.readline()
                continue

            name = name.lower().split('\n')[0] # lower case

            self.palettes[name] = Numeric.zeros((256*3),Numeric.Int8)
            for i in range(256):
                line = file.readline()

                if line == '':
                    raise Exception("%s is not a valid color map. There must be 256 lines associated with each map" % colorMapFile)

                each=line.split()
                if len(each) != 3:
                    raise Exception("%s is not a valid color map because each line for each color map must have 3 numbers. The problematic line is %s." % (colorMapFile,line) )
                r = int(float(each[0])*255)
                g = int(float(each[1])*255)
                b = int(float(each[2])*255)
                if r<0 or g<0 or b<0 or r>255 or g>255 or b>255:
                    raise Exception("%s is not a valid color map because each number must be from 0 to 1." % colorMapFile)

                self.palettes[name][3*i] = r
                self.palettes[name][3*i+1] = g
                self.palettes[name][3*i+2] = b

            name = file.readline()
            
