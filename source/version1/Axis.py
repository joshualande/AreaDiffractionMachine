from Tkinter import *
import PmwFreeze as Pmw

from General import frange
import ColorMaps

from math import pow,log10,fmod,ceil


def roundUp(a,b):
    """ Rounds a up to the smallest possible multiple of b larger then a. 
        A discussion of this formula can be found at ;
            http://www.issociate.de/board/post/245622/round_up_to_nearest....html
    """
    return a+(-1*a) % b

def roundDown(a,b):
    """ Round a down to largest possible multiple of b smaller then a. """
    return a-a%b

class Axis:

    def getNiceRange(self,lowestValue,highestValue):

        interval = (highestValue - lowestValue)
        niceStep = pow(10,ceil(log10(interval/10)))

        lowestNiceValue = roundUp(lowestValue,niceStep)
        highestNiceValue = roundDown(highestValue,niceStep)

        if (highestNiceValue-lowestNiceValue)/niceStep < 2:
            niceStep = niceStep / 5
            lowestNiceValue= roundUp(lowestValue,niceStep)
            highestNiceValue = roundDown(highestValue,niceStep)

        elif (highestNiceValue-lowestNiceValue)/niceStep < 5:
            niceStep = niceStep / 2
            lowestNiceValue = roundUp(lowestValue,niceStep)
            highestNiceValue = roundDown(highestValue,niceStep)

        return lowestNiceValue,highestNiceValue,niceStep


    def makeVerticleAxis(self):
        for id in self.allIDs:
            self.axis.delete(id)

        if self.lowestValue == None or self.highestValue == None:
            return

        lowestValueToDisplay,highestValueToDisplay,stepSizeToDisplay=self.getNiceRange(self.lowestValue,self.highestValue)

        if self.side == "left":
            self.allIDs.append( self.axis.create_line(self.width,0,self.width,self.height) )
        else:
            self.allIDs.append( self.axis.create_line(0,0,0,self.height) )
        for currentValueToDisplay in frange(lowestValueToDisplay,highestValueToDisplay+stepSizeToDisplay/100,stepSizeToDisplay):

            canvasValue = (currentValueToDisplay-self.lowestValue)/(self.highestValue-self.lowestValue)*(self.height-1)
            # don't display numbers too close to the edge
            if canvasValue < 10 or canvasValue > (self.height-1) - 10: continue

            #if canvasValue < 2: canvasValue = 2 # tk bug 

            if self.side == "left": 
                self.allIDs.append( self.axis.create_line(self.width*3.0/4,canvasValue,self.width,canvasValue) )
            else: 
                self.allIDs.append( self.axis.create_line(0,canvasValue,self.width/4.0,canvasValue) )

            if self.side == "left":
                anchor = 'e'

                self.allIDs.append( self.axis.create_text(self.width*(3.0/4-1.0/16),canvasValue,fill="black",anchor=anchor,text="%g" % currentValueToDisplay) )
            else:
                anchor = 'w'
                self.allIDs.append( self.axis.create_text(self.width*(1.0/4+1.0/16),canvasValue,fill="black",anchor=anchor,text="%g" % currentValueToDisplay) )
            

    def makeHorizontalAxis(self):
        for id in self.allIDs:
            self.axis.delete(id)

        if self.lowestValue == None or self.highestValue == None:
            return

        lowestValueToDisplay,highestValueToDisplay,stepSizeToDisplay=self.getNiceRange(self.lowestValue,self.highestValue)

        if self.side == "bottom":
            self.allIDs.append( self.axis.create_line(0,0,self.width,0) )
        else:
            self.allIDs.append( self.axis.create_line(0,self.height,self.width,self.height) )
        for currentValueToDisplay in frange(lowestValueToDisplay,highestValueToDisplay+stepSizeToDisplay/100,stepSizeToDisplay):

            canvasValue = (currentValueToDisplay-self.lowestValue)/(self.highestValue-self.lowestValue)*(self.width-1)
            # don't display numbers too close to the edge
            if canvasValue < 10 or canvasValue > (self.width-1) - 10: continue

            #if canvasValue < 2: canvasValue = 2 # tk bug 

            if self.side == "bottom": 
                self.allIDs.append( self.axis.create_line(canvasValue,0,canvasValue,self.height/4.0) )
            else: 
                self.allIDs.append( self.axis.create_line(canvasValue,self.height,canvasValue,self.height*3.0/4) )

            anchor = 'c'

            if self.side == "bottom":
                self.allIDs.append( self.axis.create_text(canvasValue,self.height*2.0/3,fill="black",anchor=anchor,text="%g" % currentValueToDisplay) )
            else:
                self.allIDs.append( self.axis.create_text(canvasValue,self.height*1.0/3,fill="black",anchor=anchor,text="%g" % currentValueToDisplay) )
            

    def __init__(self,widget,lowestValue,highestValue,width,height,side):
        """ To Draw nothing on the canvas yet, set highestValue = lowestValue = None """

        if not side in ("left","right","top","bottom"):
            raise Exception("Argument side must have the value 'left', right', 'top', or 'bottom'.")

        self.allIDs = []
        self.lowestValue = lowestValue
        self.highestValue = highestValue
        self.width = width
        self.height = height
        self.side = side
        # setting the highlightthickeness to 0 is crutial to getting the axis to display right
        self.axis=Canvas(widget,width=self.width,height=self.height,
                cursor='crosshair',
                background = widget.cget("bg"), # set to bg color (this should be the default behavior)
                borderwidth=0,
                highlightthickness=0)

        if side in ("left","right"):
            self.makeVerticleAxis()
        elif side in ("top","bottom"):
            self.makeHorizontalAxis()
         

    def config(self,lowestValue=None,highestValue=None,width=None,height=None):
        """ To remove everything and leave the canvas empty, set highestValue=lowestValue = None """
        if width != None:
            self.width = width
            self.axis.config(width=self.width)
        if height != None: 
            self.height = height
            self.axis.config(height=self.height)

        self.lowestValue = lowestValue
        self.highestValue = highestValue

        if self.side in ("left","right"):
            self.makeVerticleAxis()
        elif self.side in ("top","bottom"):
            self.makeHorizontalAxis()


    def grid(self,**args):
        self.axis.grid(args)
        

    def pack(self,**args):
        self.axis.pack(args)


if __name__ == "__main__":

    root = Tk()
    Pmw.initialise(root)

    class Main:

        def changeScale(self):
            self.lowestValue =self.lowestValue*3
            self.highestValue = self.highestValue*7

            self.axis1.config(lowestValue=self.lowestValue,highestValue=self.highestValue)
            self.axis2.config(lowestValue=self.lowestValue,highestValue=self.highestValue)
            self.axis3.config(lowestValue=self.lowestValue,highestValue=self.highestValue)
            self.axis4.config(lowestValue=self.lowestValue,highestValue=self.highestValue)

            self.button.config(text = "%f,%f" % (self.lowestValue,self.highestValue) )


        def __init__(self,root):
            self.button = Button(root,text="change Scale",command=self.changeScale)
            self.button.grid(row=0,column=0)

            self.lowestValue = 10
            self.highestValue = 100

            self.axis1=Axis(root, lowestValue = self.lowestValue, 
                    highestValue = self.highestValue, 
                    width = 600, height = 50,side = "top")
            self.axis1.grid(row=1,column=0)

            self.axis2=Axis(root, lowestValue = self.lowestValue, 
                    highestValue = self.highestValue, 
                    width = 600, height = 50,side = "bottom")
            self.axis2.grid(row=2,column=0)


            self.axis3=Axis(root, lowestValue = self.lowestValue, 
                    highestValue = self.highestValue, 
                    width = 50, height = 600,side = "left")
            self.axis3.grid(row=3,column=0)


            self.axis4=Axis(root, lowestValue = self.lowestValue, 
                    highestValue = self.highestValue, 
                    width = 50, height = 600,side = "right")
            self.axis4.grid(row=3,column=1)

    Main(root)

    root.mainloop()

