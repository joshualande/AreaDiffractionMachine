from Tkinter import *
import PmwFreeze as Pmw
from math import pow,log10,fmod,ceil,exp

from General import frange

def roundUp(a,b):
    """ Rounds a up to the smallest possible 
        multiple of b larger then a. 
        A discussion of this formula 
        can be found at :
        http://www.issociate.de/board/post/245622/round_up_to_nearest....html
    """
    return a+(-1*a) % b

def roundDown(a,b):
    """ Round a down to largest possible 
        multiple of b smaller then a. """
    return a-a%b

class Axis:
    """ This object creates a Tk object which is a plot axis. 
        It acts just like other tk objects. You have to give it
        a widget that you want to put it in. You can have to
        pack() or grid() it in place.

    def __init__(self,widget,lowestValue,highestValue,width,height,side,flip=0,logscale = 0):
    
    """

    title = None

    def getNiceRange(self,lowestValue,highestValue):

        if self.logscale:
            lowestNiceValue = roundDown(log10(lowestValue),1)
            highestNiceValue = roundUp(log10(highestValue),1)
            return lowestNiceValue,highestNiceValue,1

        interval = (highestValue - lowestValue)
        niceStep = pow(10,ceil(log10(interval/10.0)))

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


    def addVerticleLine(self,canvasValue,currentValueToDisplay=None):

        if self.flip:
            # possibly flip the numbers
            canvasValue = self.height-1 - canvasValue

        # don't display numbers too close to the edge
        if canvasValue < 10 or \
                canvasValue > (self.height-1) - 10: 
            return

        if self.side == "left": 
            self.allIDs.append(self.axis.create_line(
                    self.width*5.0/6.0,
                    canvasValue,self.width,canvasValue) )
        else: 
            self.allIDs.append(self.axis.create_line(
                    0,canvasValue,self.width/6.0,canvasValue) )

        if currentValueToDisplay != None:
            if self.side == "left":
                anchor = 'e'
                self.allIDs.append(
                        self.axis.create_text(self.width*(3.0/4),
                        canvasValue,fill="black",
                        anchor=anchor,text="%g" % currentValueToDisplay) )
            else:
                anchor = 'w'
                self.allIDs.append(
                        self.axis.create_text(self.width*(1.0/4),
                        canvasValue,fill="black",
                        anchor=anchor,text="%g" % currentValueToDisplay) )


    def makeVerticleAxis(self):
        for id in self.allIDs:
            self.axis.delete(id)

        if self.lowestValue == None or self.highestValue == None:
            return

        lowestValueToDisplay,highestValueToDisplay,stepSizeToDisplay=\
                self.getNiceRange(self.lowestValue,self.highestValue)

        if self.side == "left":
            self.allIDs.append(self.axis.create_line(
                    self.width-1,0,self.width-1,self.height) )
        else:
            self.allIDs.append(self.axis.create_line(0,0,0,self.height) )
        for currentValueToDisplay in frange(lowestValueToDisplay,
                highestValueToDisplay+stepSizeToDisplay/100,stepSizeToDisplay):

            if self.logscale:
                # if log scale, then currentValueToDisplay is given 
                # as the log of it,
                canvasValue=(currentValueToDisplay-log10(self.lowestValue))/\
                        (log10(self.highestValue)-\
                        log10(self.lowestValue))*(self.height-1)
                currentValueToDisplay = pow(10,currentValueToDisplay)

                self.addVerticleLine(canvasValue,currentValueToDisplay)

                for loop in range(2,10):
                    # minor tic marks, don't add numbers!
                    # going into loop, remember that current val is now
                    # the acutal value to display
                    logMinorValue = log10(loop*currentValueToDisplay)

                    canvasValue=(logMinorValue-log10(self.lowestValue))/\
                            (log10(self.highestValue)-\
                            log10(self.lowestValue))*(self.height-1)

                    self.addVerticleLine(canvasValue)

            else:
                # otherwise, calculate the canvasValue regularly
                canvasValue = (currentValueToDisplay-self.lowestValue)/\
                        (self.highestValue-self.lowestValue)*(self.height-1)

                self.addVerticleLine(canvasValue,currentValueToDisplay)
                        



        if self.title != None:
            if self.side == "left":
                self.allIDs.append(self.axis.create_text(
                        0,self.height/2.0,fill="black",
                        anchor="w",text=self.title))
            else:
                self.allIDs.append(self.axis.create_text(
                        self.width,self.height/2.0,
                        fill="black",anchor="e",text=self.title))


    def makeHorizontalAxis(self):
        for id in self.allIDs:
            self.axis.delete(id)

        if self.lowestValue == None or self.highestValue == None:
            return

        lowestValueToDisplay,highestValueToDisplay,stepSizeToDisplay=\
                self.getNiceRange(self.lowestValue,self.highestValue)

        if self.side == "bottom":
            self.allIDs.append(self.axis.create_line(0,1,self.width,1) )
        else:
            self.allIDs.append(self.axis.create_line(
                    0,self.height,self.width,self.height) )

        for currentValueToDisplay in frange(lowestValueToDisplay,
                highestValueToDisplay+stepSizeToDisplay/100,
                stepSizeToDisplay):

            canvasValue = (currentValueToDisplay-self.lowestValue)/\
                    (self.highestValue-self.lowestValue)*(self.width-1)
            if self.flip:
                # possibly flip the numbers
                canvasValue = self.width-1-canvasValue

            # don't display numbers too close to the edge
            if canvasValue<10 or canvasValue>(self.width-1)-10: 
                continue

            if canvasValue < 2: canvasValue = 2 # tk bug (I think)

            if self.side == "bottom": 
                self.allIDs.append( self.axis.create_line(
                        canvasValue,0,canvasValue,self.height/6.0) )
            else: 
                self.allIDs.append( self.axis.create_line(
                        canvasValue,self.height,
                        canvasValue,self.height*5.0/6.0) )

            anchor = 'c'

            if self.side == "bottom":
                self.allIDs.append(self.axis.create_text(
                        canvasValue,self.height*1.0/3,
                        fill="black",anchor=anchor,
                        text="%g" % currentValueToDisplay))
            else:
                self.allIDs.append(self.axis.create_text(
                        canvasValue,self.height*2.0/3,fill="black",
                        anchor=anchor,text="%g" % currentValueToDisplay))
            
        if self.title != None:
            if self.side == "bottom":
                self.allIDs.append(self.axis.create_text(
                        (self.width-1.0)/2.0,self.height*2.0/3.0,
                        fill="black",anchor="c",text=self.title))
            else:
                self.allIDs.append(self.axis.create_text(
                        (self.width-1.0)/2.0,self.height*1.0/3.0,
                        fill="black",anchor="c",text=self.title))


    def __init__(self,widget,lowestValue,highestValue,width,
            height,side,flip=0,logscale = 0):
        """ To Draw nothing on the canvas yet, 
            set highestValue = lowestValue = None.
            The variable flip (if ture) will cause the numbers 
            to be drawn in the reverse order"""

        if not side in ("left","right","top","bottom"):
            raise Exception("Argument side must have the value \
'left', right', 'top', or 'bottom'.")

        if logscale and side in ("top","bottom"):
            raise Exception("Can only apply the log scale to the \
vertical axis.")

        self.allIDs = []
        self.lowestValue = lowestValue
        self.highestValue = highestValue
        self.width = width
        self.height = height
        self.side = side
        self.flip = flip 
        self.logscale = logscale

        # setting the highlightthickeness to 0 is crucial to getting 
        # the axis to display right
        self.axis=Canvas(widget,width=self.width,height=self.height,
                cursor='crosshair',
                background = widget.cget("bg"), 
                # set to bg color (this should be the default behavior)
                borderwidth=0,
                highlightthickness=0)

        if side in ("left","right"):
            self.makeVerticleAxis()
        elif side in ("top","bottom"):
            self.makeHorizontalAxis()
         

    def config(self,lowestValue=None,highestValue=None,width=None,
            height=None,logscale=None,title=None):
        """ To remove everything and leave the canvas empty, set 
            highestValue=lowestValue=None """
        if width != None:
            self.width = width
            self.axis.config(width=self.width)

        if height != None: 
            self.height = height
            self.axis.config(height=self.height)

        self.lowestValue = lowestValue
        self.highestValue = highestValue

        if title != None:
            self.title = title

        if logscale != None:
            self.logscale = logscale

        if self.side in ("left","right"):
            self.makeVerticleAxis()
        elif self.side in ("top","bottom"):
            self.makeHorizontalAxis()


    def grid(self,**args):
        self.axis.grid(args)
        

    def pack(self,**args):
        self.axis.pack(args)


if __name__ == "__main__":
    """ Below is some simple testing code. It just
        makes one big TK window and draws a
        bunch of axis on top of it."""

    root = Tk()
    Pmw.initialise(root)

    class Main:

        def changeScale(self):
            self.lowestValue =self.lowestValue*3
            self.highestValue = self.highestValue*7

            self.axis1.config(
                    lowestValue=self.lowestValue,
                    highestValue=self.highestValue)
            self.axis2.config(
                    lowestValue=self.lowestValue,
                    highestValue=self.highestValue)
            self.axis3.config(
                    lowestValue=self.lowestValue,
                    highestValue=self.highestValue)
            self.axis4.config(
                    lowestValue=self.lowestValue,
                    highestValue=self.highestValue)

            self.button.config(text = "%f,%f" % \
                    (self.lowestValue,self.highestValue) )


        def __init__(self,root):
            self.button = Button(root,text="change Scale",
                    command=self.changeScale)
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

