import Tkinter
from Tkinter import *
import PmwFreeze as Pmw
import Tix
from string import *
from math import *
from Numeric import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
from tkColorChooser import askcolor
import os
import os.path
import re
import Image
import ImageTk
import ImageFile
import webbrowser
from MaskedPixelInfo import MaskedPixelInfo 

#because py2exe is dumb...
import JpegImagePlugin    
import PpmImagePlugin
import PngImagePlugin
import TiffImagePlugin
import WmfImagePlugin
import GifImagePlugin
import BmpImagePlugin
import EpsImagePlugin
import PdfImagePlugin
Image._initialized = 1

#blatant fix...  
Image.SAVE["JPEG"]=JpegImagePlugin._save
Image.EXTENSION[".jpg"]="JPEG"
Image.SAVE["PPM"]=PpmImagePlugin._save
Image.EXTENSION[".ppm"]="PPM"
Image.SAVE["PNG"]=PngImagePlugin._save
Image.EXTENSION[".png"]="PNG"
Image.SAVE["TIFF"]=TiffImagePlugin._save
Image.EXTENSION[".tif"]="TIFF"
Image.EXTENSION[".tiff"]="TIFF"
Image.SAVE["WMF"]=WmfImagePlugin._save
Image.EXTENSION[".wmf"]="WMF"
Image.SAVE["GIF"]=GifImagePlugin._save
Image.EXTENSION[".gif"]="GIF"
Image.SAVE["BMP"]=BmpImagePlugin._save
Image.EXTENSION[".bmp"]="BMP"
Image.SAVE["EPS"]=EpsImagePlugin._save
Image.EXTENSION[".eps"]="EPS"
Image.SAVE["PDF"]=PdfImagePlugin._save
Image.EXTENSION[".pdf"]="PDF"


# Below are packages special to this program
import QData
import ColorMaps
from Exceptions import UserInputException,UnknownFiletypeException
from DiffractionData import DiffractionData
import Transform
from CalibrationData import CalibrationData
import General
from MacroMode import MacroMode
from Axis import Axis
import LinePlot


root=Tkinter.Tk()

# This is here to fix a bug in py2app. You can read about it here:
# http://www.thescripts.com/forum/thread543994.html
try:
    if (sys.platform != "win32") and hasattr(sys, 'frozen'):
        root.tk.call('console', 'hide')
except:
    # if this dose not work for some reason, don't worry about it
    # and run the program anyway
    pass

Pmw.initialise(root)

filepath=os.getcwd()+os.sep


def removeAllItemsFromMenu(menu):
    """ Code taken from: 
        http://osdir.com/ml/python.tkinter/2006-07/msg00018.html """
    if menu.index("last") is not None:
        menu.delete(0,menu.index("last"))


# lame function for updating status bars
def setstatus(n,format):
    n.config(text=format)
    n.update_idletasks()

# Another lame function to set the check box to a string value
def setcheckbox(checkbox,value):
    if value=='select':
        checkbox.select()
    if value=='deselect':
        checkbox.deselect()

class FancyErrors:

    VERBOSE = 0

    def __init__(self,status):
        # I think this is how Linux/Windows exceptions are formatted
        patternstring = r"""UserInputException: ['"](.*)['"]"""
        self.pattern = re.compile(patternstring, re.DOTALL)

        # I think this is how Mac exceptions are formatted
        otherpatternstring = \
                r"""<class 'Exceptions.UserInputException'>: ['"](.*)['"]"""
        self.otherpattern = re.compile(otherpatternstring, re.DOTALL)

        self.status=status

    def write(self,string):
        setstatus(self.status,'Error...')
        # Try to remove the recording macro text box, 
        # this will only work if an error was thrown when
        # recording a macro. If that dosen't happen, then
        # simply ignore any errors raised
        try:
            self.macrostatus.pack_forget() # remove from screen
            setstatus(self.macrostatus,'')
        except:
            pass

        match = self.pattern.search(string)
        # see if the current exception is a windows/linux 
        # style UserInputException. If so, then print out 
        # just the exception
        if match:
            message = match.groups()[0]
            box=tkMessageBox.showerror('Error',message)
        else:
            # see if the current exception is a mac style
            # UserInputException. If so, then print out 
            # just the exception
            othermatch = self.otherpattern.search(string)
            if othermatch:

                if self.VERBOSE: print string

                message = othermatch.groups()[0]
                box=tkMessageBox.showerror('Error',message)
            else:
                # otherwise, dump out the whole exception 
                # in an ugly manner
                print string
                box=tkMessageBox.showerror('UNKNOWN ERROR',string)
        setstatus(self.status,'Ready')


def programabout(master):
    Pmw.aboutversion('1')
    Pmw.aboutcopyright(
            'Copyright Joshua Lande and Samuel Webb, \
2007\nStanford Synchrotron Radiation Laboratory')

    Pmw.aboutcontact("""email: joshualande@gmail.com or \
samwebb@slac.stanford.edu
web: areadiffractionmachine.googlecode.com""")

    # imlogo=Image.open("smak_sm.jpg")
    # imlogo.load()
    # logo=ImageTk.PhotoImage(imlogo)
    # logo.paste(imlogo)
    about=Pmw.AboutDialog(master,
            applicationname='The Area Diffraction Program')#,icon_image=logo)
    # about.component('icon').image=logo

class PreferencesDisplay:
    """ Creates a window that allows the user to specify some
        customization for the program. """
    def __init__(self,master,defaultDir,selectDefaultFolder,setDefaultFolder):
        self.main=Pmw.MegaToplevel(master)
        self.main.title("Preferences")
        self.main.userdeletefunc(func=self.main.withdraw)

        filebar = Frame(self.main.interior(), relief=SUNKEN,bd=2)

        self.defaultFolderEntry=Pmw.EntryField(filebar,
                entry_width=68,labelpos=W,
                label_text="Default Folder:")
        self.defaultFolderEntry.pack(side=LEFT,padx=5,pady=1,fill=X)

        #get file name from directory
        b=Button(filebar,
                bitmap="@"+filepath+"xbms"+os.sep+"openfolder.xbm",
                height=21,width=50,command=selectDefaultFolder,
                bg='lightyellow') 
        b.pack(side=LEFT,padx=2,pady=2)

        #load data file and display
        b=Button(filebar,text="Set",bg='darkgreen',fg='snow',
                command=setDefaultFolder) 
        b.pack(side=LEFT,padx=2,pady=2)
        filebar.pack(side=TOP,padx=2,pady=2,fill=X)       
   
class Display:
    """ XRD Display Class. """
    def __init__(self,master,imageWidth,imageHeight,
            axisSize,ufunc,colorMaps,title,invertVar,
            logScaleVar):

        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.axisSize=axisSize

        self.ufunc=ufunc
        self.main=Pmw.MegaToplevel(master)
        self.main.title(title)
        self.main.userdeletefunc(func=self.main.withdraw)
        nf=self.main.interior()
        nf.config(borderwidth=2)
        nf.grid_rowconfigure(0,weight=1)
        nf.grid_columnconfigure(0,weight=1)

        self.graphframe = Frame(nf)
        self.graphframe.grid(row=0,column=0,sticky=N+W+E+S)

        self.imframe=Canvas(self.graphframe,bg='black',
                borderwidth=0,highlightthickness=0,
                height=imageHeight,
                width=imageWidth, cursor='crosshair')
        self.imframe.grid(row=0,column=0,sticky=N+W)

        # add the 2 axis
        self.rightAxis = Axis(self.graphframe,
                lowestValue = None, highestValue = None,
                height = imageHeight, 
                width = axisSize, side = "right")
        self.rightAxis.grid(row=0,column=1,sticky=N+W)

        self.bottomAxis = Axis(self.graphframe,
                lowestValue = None, highestValue = None,
                width = imageWidth, 
                height = axisSize, side = "bottom")
        self.bottomAxis.grid(row=1,column=0,sticky=N+W)

        fr=Frame(nf)
        fr.grid(row=0,column=1,sticky=N+E)
        lab=Label(fr,text='Low',width=3,anchor=N+E)
        lab.pack(side=TOP,fill='both')
        self.intenvarlo=DoubleVar()
        self.intenvarlo.set(0.00)
        self.intensitylo=Scale(fr,variable=self.intenvarlo,
                width=10,from_=1.0, to=0.00,orient=VERTICAL,
                resolution=0.001,length=250,command=DISABLED)
        self.intensitylo.pack(side=TOP,fill=Y)

        fr=Frame(nf)
        fr.grid(row=0,column=2,sticky=N+E)
        lab=Label(fr,text='Hi',width=3,anchor=N+E)
        lab.pack(side=TOP,fill='both')
        self.intenvarhi=DoubleVar()
        self.intenvarhi.set(.05)
        self.intensityhi=Scale(fr,variable=self.intenvarhi,
                width=10,from_=1.0, to=0.001,orient=VERTICAL,
                resolution=0.001,length=250,command=DISABLED)
        self.intensityhi.pack(side=TOP,fill=Y)

        # bind to letting go of the scale to redrawing the image
        self.intensitylo.bind(sequence="<ButtonRelease>",
                func=self.updateimageNoComplain)
        self.intensityhi.bind(sequence="<ButtonRelease>",
                func=self.updateimageNoComplain)

        #coordinates
        botfr=Frame(nf)        
        self.xcoord=Label(botfr,text="X=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
        self.ycoord=Label(botfr,text="Y=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
        self.qcoord=Label(botfr,text="Q=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='blue')
        self.dcoord=Label(botfr,text="D=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='blue')
        self.ccoord=Label(botfr,text="chi=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='blue')
        self.icoord=Label(botfr,text="I=      ",
                width=15,bd=2,relief=RIDGE,anchor=W,fg='darkgreen')
        self.icoord.pack(side=RIGHT,fill=X)
        self.ccoord.pack(side=RIGHT,fill=X)
        self.dcoord.pack(side=RIGHT,fill=X)
        self.qcoord.pack(side=RIGHT,fill=X)
        self.ycoord.pack(side=RIGHT,fill=X)
        self.xcoord.pack(side=RIGHT,fill=X)
        botfr.grid(row=2,column=0,columnspan=3,sticky=E+S)

        #colormap selection
        another=Frame(nf)
        another.grid(row=1,column=0,columnspan=3,sticky=S+W)
        self.colmap=Pmw.ScrolledListBox(another,
                        items=colorMaps.getColorMapNames(),
                        labelpos='w',label_text='Colormaps',
                        listbox_height=3,
                        selectioncommand=self.updateimageNoComplain,
                        listbox_background=another.cget("bg"), 
                        # this should be the default
                        listbox_exportselection=0)
        self.colmap.setvalue('bone')
        self.colmap.pack(side=LEFT,fill='both')
        self.colinvert = Checkbutton(another,text="Invert? ", 
                variable=invertVar,
                command=self.updateimageNoComplain)
        self.colinvert.pack(side=LEFT,fill='both')
        self.collog = Checkbutton(another,text="Log Scale? ", 
                variable=logScaleVar,
                command=self.updateimageNoComplain)
        self.collog.pack(side=LEFT,fill='both')
        #update button
        b=Button(another,text='Update Image',width=15,
                bg='darkgreen',fg='snow',command=self.updateimage)
        b.pack(side=LEFT,padx=60,fill=X)


    def updateimageNoComplainNoShow(self,*args):
        """ Calls the supplied update function without 
            rasing an error if anything bad happends.
            This is useful when you want to try to redraw the window
            without throwing any obnoxious errors. Also, this
            function will not show the current window but
            the updates will still be visible if the window is already
            displayed. """
        try:
            self.ufunc()
        except:
            setstatus(self.status,'Ready')

    def updateimageNoComplain(self,*args):
        # don't raise an error message if anything goes wrong. 
        try:
            self.ufunc()
            self.main.show()
        except:
            setstatus(self.status,'Ready')


    def updateimageNoComplainWithdrawIfError(self,*args):
        # don't raise an error message if anything goes wrong. 
        try:
            self.ufunc()
            self.main.show()
        except:
            self.main.withdraw()
            setstatus(self.status,'Ready')

    def updateimage(self,*args):
        self.ufunc()
        self.main.show()


class GraphDisplay:
    """ Graph Display Class """

    xUpdateName='X'
    yUpdateName='Y'

    def __init__(self,master,title,logScaleVar):
        self.logScaleVar = logScaleVar

        self.main=Pmw.MegaToplevel(master)
        self.main.title(title)
        self.main.userdeletefunc(func=self.main.withdraw)
        h=self.main.interior()

        # make the window expand properly
        h.grid_rowconfigure(0,weight=1)
        h.grid_columnconfigure(0,weight=1)

        self.graph=LinePlot.LinePlot(h,plotbackground='white',
                height=350,width=550)
        self.graph.bind(sequence="<ButtonPress>",   
                func=self.mouseDown)
        self.graph.bind(sequence="<ButtonRelease>", 
                func=self.mouseUp  )
        self.graph.bind(sequence="<Motion>", 
                func=self.coordreport)
        self.graph.bind(sequence="<Leave>", 
                func=self.nocoordreport)
        self.graph.legend_configure(hide=1)
        self.graph.grid(row=0,column=0,sticky=N+W+E+S,padx=10,pady=10)

        #zoom stack
        self.zoomstack=[]

        #coordinates
        botfr=Frame(h)        
        self.xcoord=Label(botfr,text="%s=      " % self.xUpdateName,
                width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
        self.ycoord=Label(botfr,text="%s=      " % self.yUpdateName,
                width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
        self.ycoord.pack(side=RIGHT,fill=X)
        self.xcoord.pack(side=RIGHT,fill=X)

        self.collog = Checkbutton(botfr,text="Log Scale? ",
                variable=self.logScaleVar,
                command=self.changeLogScale)
        self.collog.pack(side=RIGHT,fill=X)

        botfr.grid(row=1,column=0,sticky=E,padx=10)

    def changeLogScale(self,event=None):
        # Change the logscaleness of the graph
        self.graph.yaxis_configure(logscale=self.logScaleVar.get())


    def nocoordreport(self,event=None):
        xtext=self.xUpdateName+"="
        ytext=self.yUpdateName+"="
        setstatus(self.xcoord,xtext)
        setstatus(self.ycoord,ytext)


    def coordreport(self,event):
        (x,y)=self.graph.invtransform(event.x,event.y)
        xtext=self.xUpdateName+"="+str(x)
        ytext=self.yUpdateName+"="+str(y)
        xtext=xtext[:12]
        ytext=ytext[:12]
        setstatus(self.xcoord,xtext)
        setstatus(self.ycoord,ytext)
    

    def zoom(self, x0, y0, x1, y1):
        #add last to zoomstack
        a0=self.graph.xaxis_cget("min")
        a1=self.graph.xaxis_cget("max")
        b0=self.graph.yaxis_cget("min")
        b1=self.graph.yaxis_cget("max")        

        # Bound the zooming parameters to be reasonable
        if y0 < self.yMin: y0 = self.yMin
        if y1 > self.yMax: y1 = self.yMax
        if x0 < self.xMin: x0 = self.xMin
        if x1 > self.xMax: x1 = self.xMax

        self.zoomstack.append((a0,a1,b0,b1))
        #configure
        self.graph.xaxis_configure(min=x0, max=x1)
        self.graph.yaxis_configure(min=y0, max=y1)

    def mouseDrag(self,event):
        global x0, y0, x1, y1
        (x1, y1) = self.graph.invtransform(event.x, event.y)             
        try:
            self.graph.marker_configure("marking rectangle", 
                coords = (x0,y0,x1,y0,x1,y1,x0,y1,x0,y0))
        except:
            # it doesn't matter if this dose not work
            pass
        self.coordreport(event)
    

    def mouseUp(self,event):
        """ Right click, zoom in.
            Left click, zoom out. """
        
        global dragging
        global x0, y0, x1, y1        
        if dragging:
            self.graph.unbind(sequence="<Motion>")
            self.graph.bind(sequence="<Motion>", 
                    func=self.coordreport)
            if event.num==1:
                self.graph.marker_delete("marking rectangle")           
                # make sure the coordinates are sorted
                x0,x1=min(x0,x1),max(x0,x1)
                y0,y1=min(y0,y1),max(y0,y1)

                if x0 == x1 or y0 == y1:
                    return

                self.zoom(x0, y0, x1, y1) # zoom in
            else:
                self.rescaleplot() # zoom out
                           

    def mouseDown(self,event):
        global dragging, x0, y0, x1, y1
        dragging = 0
        if self.graph.inside(event.x, event.y):
            dragging = 1
            (x0, y0) = self.graph.invtransform(event.x, event.y)
            (x1, y1) = (x0, y0)
            # if right click = zoom in, draw the rectangle
            if event.num==1:
                self.graph.marker_create("line", 
                        name="marking rectangle", dashes=(2, 2))
            self.graph.bind(sequence="<Motion>",  
                    func=self.mouseDrag)        

    def rescaleplot(self):
        #get last off stack
        if self.zoomstack==[]:
            # if there is no previous zoom, just to an auto scale
            self.graph.xaxis_configure(min='',max='')
            self.graph.yaxis_configure(min='',max='')
            return
        limit=self.zoomstack.pop()
        self.graph.xaxis_configure(min=limit[0],max=limit[1])
        self.graph.yaxis_configure(min=limit[2],max=limit[3])

    def makegraph(self,xd,yd,xLabel,yLabel,xUpdateName,
            yUpdateName,cmd='NEW',pc=None,
            dontConnectDataPointsWithValue=None):
        if len(xd) != len(yd):
            raise Exception("Cannot make graph because the \
number of x and y data points must be equal")
        if upper(cmd)=='NEW':
            #clear graphs
            glist=self.graph.element_names()
            if glist != ():
                for g in glist:
                    self.graph.element_delete(g)
            if self.zoomstack==[]:
                self.graph.xaxis_configure(min='',max='')
                self.graph.yaxis_configure(min='',max='')
        #default color scheme order
        colors=['red','blue','darkgreen','orange','black',\
                'green','purple4','cyan','steel blue',\
                'yellow4','peru']
        cnum=len(colors)
        #determine color if not given
        if pc==None:
            #determine number of elements
            gnum=len(self.graph.element_names())
            pc=colors[int(fmod(gnum,cnum))]
        #plot

        if dontConnectDataPointsWithValue != None:
            # create a new data series for each of 
            # the series of data points between the 
            # undesirable ones
            currentxd = []
            currentyd = []
            for current in range(len(yd)):
                if yd[current] == dontConnectDataPointsWithValue:
                    # ignore the current data point b/c it 
                    # is the bad one if there is a series 
                    # to put in the graph, do so
                    if currentxd != [] and currentyd != []:
                        self.graph.line_create(
                                'graph'+str(current),
                                xdata=tuple(currentxd),
                                ydata=tuple(currentyd),
                                symbol='',color=pc)
                    currentxd = []
                    currentyd = []
                else:
                    currentxd.append(xd[current])
                    currentyd.append(yd[current])

            if currentxd != [] and currentyd != []:
                self.graph.line_create('graph'+str(current),
                        xdata=tuple(currentxd),
                        ydata=tuple(currentyd),symbol='',color=pc)

        else:
            self.graph.line_create('graph',xdata=tuple(xd),
                    ydata=tuple(yd),symbol='',color=pc,pixels=7)

        self.xMax = max(xd)
        self.xMin = min(xd)
        self.yMax = max(yd)
        self.yMin = min(yd)

        # make sure as to not trip up log scaling by 
        # puting 0 as the y axis range.
        if self.yMin < 0:
            self.yMin = .001 

        self.graph.xaxis_configure(title=xLabel)
        self.graph.yaxis_configure(title=yLabel)

        self.xUpdateName=xUpdateName
        self.yUpdateName=yUpdateName

        self.nocoordreport()

    
    def reset(self): 
        xUpdateName='X'
        yUpdateName='Y'
        self.nocoordreport()

        glist=self.graph.element_names()
        if glist != ():
            for g in glist:
                self.graph.element_delete(g)

        self.zoomstack==[]
        self.graph.xaxis_configure(min='',max='')
        self.graph.yaxis_configure(min='',max='')
  
class FieldBox:
    """ Entryfield-Checkbutton Classes """

    def __init__(self,master,name='',validate=None,noCheckBox=0):
        w=15
        bf=Frame(master)
        bf.pack(side=TOP,padx=2,pady=0,anchor=W)
        self.ef=Pmw.EntryField(bf,entry_width=w,labelpos='w',
                label_text=name+': ',validate=validate)
        self.ef.pack(side=LEFT,padx=5,pady=1)
        if not noCheckBox:
            # put a check box unless explicitly told not to
            self.fixedvar=IntVar()
            self.cb=Checkbutton(bf,variable=self.fixedvar,text='')
            self.cb.pack(side=LEFT,padx=10,pady=1)
        else: 
            pass

    
class BoxButton:
    def __init__(self,master,func,colorFunc,name):
        bf=Frame(master)
        bf.pack(side=TOP,padx=2,pady=0,fill=X)
        self.checkvar=IntVar()
        self.cb=Checkbutton(bf,variable=self.checkvar,text=name,command=func)
        self.cb.pack(side=LEFT,padx=2,pady=1)
        self.button=Button(bf,text='Color',command=colorFunc)
        self.button.pack(side=RIGHT,padx=2,pady=1)

        
class Main:
    """ Main Class """

    fullPathName = os.path.abspath(os.path.dirname(sys.argv[0]))
    standardQFolder = fullPathName+os.sep+"StandardQ"

    colorMaps = None
    diffractionData = None
    QData = None
    peakList = None
    calibrationData = []

    # The color of the Q lins that get drawn on the 
    # diffraction data
    qLinesColor = StringVar()
    qLinesColor.set("red")

    # The color of the dQ lines that get drawn on 
    # the diffraction data
    dQLinesColor = StringVar()
    dQLinesColor.set("green")

    # The color of the peaks
    peakLinesColor = StringVar()
    peakLinesColor.set("orange")


    # info about the pixel masking,
    # make sure to put a small and silly widget
    # inside of it because the object might get 
    # deep copied some time later
    maskedPixelInfo = MaskedPixelInfo(widget = Label())

    # the color that these pixels will be displayed as
    greaterThanMaskColor = StringVar()
    greaterThanMaskColor.set("pink")

    # The color that these pixels will be displayed as
    lessThanMaskColor = StringVar()
    lessThanMaskColor.set("pink")

    # The color of the possibly masked pixels
    polygonMaskColor = StringVar()
    polygonMaskColor.set('green')


    # fitting parameters 
    numberOfChiStore = None
    stddevStore = None

    axisSize = 40

    # stuff to help out the diffraction image
    diffractionImageSize = 560
    diffractionImageID = None
    allQLineIDsDiffractionImage = []
    allPeakListIDsDiffractionImage = []
    # This is a list of zoom levels for the 
    # diffraction image of the form:
    # ( {'x':val,'y':val}, {'x':val,'y':val} )
    # This is a list of two pixels specifying 
    # the corners of the zoom.
    diffractionImageZoomPixels = []


    # Create a checkbutton menu item.
    eVorLambda = StringVar()
    lasteVorLambda = StringVar()

    # stuff to help out the cake image
    cake = None
    cakeImageWidth=560
    cakeImageHeight=560
    cakeImageID = None
    allQLineIDsCakeImage = []
    allPeakListIDsCakeImage = []
    # This is a list of cake ranges of the form
    # {'qOrTwoThetaLower':val,'qOrTwoThetaUpper':val,
    #  'chiLower',val,'chiUpper',val}
    cakeRange = []

    Qor2Theta = StringVar()
    lastQor2Theta = StringVar()

    # the integrated intensity object
    # this can hold either Q-I or Chi-I data
    integrate = None
    
    # lots of check buttons

    useOldPeakList=IntVar()
    useOldPeakList.set(1)

    doPolarizationCorrectionCake = IntVar()
    doPolarizationCorrectionCake.set(0)

    doPolarizationCorrectionIntegrate = IntVar()
    doPolarizationCorrectionIntegrate.set(0)

    invertVarDiffraction = IntVar()
    invertVarDiffraction.set(0)

    logVarDiffraction = IntVar()
    logVarDiffraction.set(0)

    invertVarCake = IntVar()
    invertVarCake.set(0)

    logVarCake = IntVar()
    logVarCake.set(0)

    logVarIntegration = IntVar()
    logVarIntegration.set(0)


    constrainWithRangeOnRight = IntVar()
    constrainWithRangeOnRight.set(0)

    constrainWithRangeOnLeft = IntVar()
    constrainWithRangeOnLeft.set(0)

    # allows all the macro magic
    macroMode = None

    # Not recording macros
    macroLines = None

    # The current polygon that is being drawn on the diffraction image
    currentPolygon = None
    currentPolygonID = None

    defaultDir = None 

    def __init__(self,master):
        self.colorMaps = ColorMaps.ColorMaps('colormaps.txt')
        self.xrdwin=xrdwin=master
        xrdwin.title("""The Area Diffraction Machine""")
        #Displays

        self.maindisp=Display(self.xrdwin,colorMaps=self.colorMaps,
                imageWidth=self.diffractionImageSize,
                imageHeight=self.diffractionImageSize,
                axisSize=self.axisSize,
                ufunc=self.drawDiffractionImage,
                title="Diffraction Data",
                invertVar=self.invertVarDiffraction,
                logScaleVar=self.logVarDiffraction)
        self.maindisp.main.withdraw()

        self.cakedisp=Display(self.xrdwin,colorMaps=self.colorMaps,
                imageWidth=self.cakeImageWidth,
                imageHeight=self.cakeImageHeight,
                axisSize=self.axisSize,
                ufunc=self.doCake,
                title="Cake Data",
                invertVar=self.invertVarCake,
                logScaleVar=self.logVarCake)
        self.cakedisp.main.withdraw()

        self.integratedisp=GraphDisplay(self.xrdwin,
                title='Integration Data',
                logScaleVar=self.logVarIntegration)
        self.integratedisp.main.withdraw()

        self.preferencesdisplay=PreferencesDisplay(self.xrdwin,
                self.defaultDir,self.selectDefaultFolder,
                self.setDefaultFolder)
        self.preferencesdisplay.main.withdraw()

        # set the default from the folder.
        self.defaultFolderFromFile()


        #The Menu bar
        menubar= Menu(xrdwin)
        self.menubar = menubar
        root.config(menu=menubar)

        # The file menu
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label='Data File',
                command=self.selectDiffractionFiles) 
        filemenu.add_separator()

        # THE 'opened file(s)' menu should go here
        self.openedfilesmenu = Menu(filemenu, tearoff=0)
        filemenu.add_cascade(label='Opened File(s)',
                menu=self.openedfilesmenu)
        self.openedfilesmenu.add_command(label='None',
                command=DISABLED)

        filemenu.add_separator()

        filemenu.add_command(label='Preferences',
                command=self.preferencesdisplay.main.show)

        filemenu.add_separator()
        self.saveDiffractionImageMenuItem=filemenu.add_command(
                label='Save Image',
                command=self.saveDiffractionImage)
        filemenu.add_command(label='Save Caked Image',
                command=self.saveCakeImage)
        filemenu.add_separator()
        filemenu.add_command(label='Save Caked Data',
                command=self.saveCakeData)

        calibrationmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Calibration",
                menu=calibrationmenu)

        calibrationmenu.add_command(label='Get From Header',
                command=self.calibrationDataFromHeader)
        calibrationmenu.add_command(label='Load From File',
                command=self.calibrationDataLoad)
        calibrationmenu.add_command(label='Previous Values',
                command=self.calibrationDataUndo)
        calibrationmenu.add_command(label='Save To File',
                command=self.calibrationDataSave)
        calibrationmenu.add_separator()

        self.qmenu = Menu(calibrationmenu, tearoff=0)
        calibrationmenu.add_cascade(label='Standard Q',
                menu=self.qmenu)
        self.addStandardQ(self.qmenu)

        calibrationmenu.add_separator()

        calibrationmenu.add_radiobutton(
                label = 'Work in eV',
                command = self.changeEVorLambda,
                variable = self.eVorLambda)

        calibrationmenu.add_radiobutton(
                label = "Work in Lambda",
                command = self.changeEVorLambda,
                variable = self.eVorLambda)

        calibrationmenu.add_separator()
        calibrationmenu.add_command(label='Do Fit',
                command=self.doFit)        
        calibrationmenu.add_command(label='Save Last Fit',
                command=self.saveLastFit)
        calibrationmenu.add_command(label='Make/Save Peak List',
                command=self.savePeakList)

        maskingmenu = Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Masking",menu=maskingmenu)
        maskingmenu.add_command(label='Clear Mask',
                command=self.removePolygons)
        maskingmenu.add_command(label='Save Mask',
                command=self.savePolygonsToFile)
        maskingmenu.add_command(label='Load Mask',
                command=self.loadPolygonsFromFile)

        cakemenu = Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Cake",menu=cakemenu)
        cakemenu.add_command(label='Do Cake',
                command=self.cakedisp.updateimage)
        cakemenu.add_command(label='Auto Cake',
                command=self.autoCake)
        cakemenu.add_separator()
        cakemenu.add_command(label='Last Cake',
                command=self.undoZoomCakeImage)
        cakemenu.add_separator()
        cakemenu.add_command(label='Save Caked Image',
                command=self.saveCakeImage)   
        cakemenu.add_command(label='Save Caked Data',
                command=self.saveCakeData)

        integratemenu = Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Integrate",menu=integratemenu)

        integratemenu.add_command(label='Integrate Q-I Data',
                command=self.integrateQOrTwoThetaI)
        integratemenu.add_command(label='Integrate Chi-I Data',
                command=self.integrateChiI)
        integratemenu.add_separator()
        integratemenu.add_command(label='Save Integration Data',
                command=self.saveIntegratedIntensity)
        integratemenu.add_separator()

        integratemenu.add_radiobutton(
                label = 'Work in 2theta',
                command = self.changeQor2Theta,
                variable = self.Qor2Theta)

        integratemenu.add_radiobutton(
                label = "Work in Q",
                command = self.changeQor2Theta,
                variable = self.Qor2Theta)

        self.macromenu = Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Macro",menu=self.macromenu)

        self.macromenu.add_command(label='Start Record Macro',
                command=self.startRecordMacro)
        self.macromenu.add_command(label='Stop Record Macro',
                command=self.stopRecordMacro,state=DISABLED)

        self.macromenu.add_separator()
        self.macromenu.add_command(label='Run Saved Macro',
                command=self.runMacro)

        self.macromenu.add_separator()
        self.macromenu.add_command(label='Set As Initialization',
                command=self.setAsInitializationMacro,state=DISABLED)

        # this name="help" syntax makes the help menu 
        # show up in the right place on the mac, where 
        # there is already a default help part of the menu 
        # bar. I leared about how to do this here:
        # http://coding.derkeiler.com/Archive/Python/comp.lang.python/2006-10/msg02418.html
        helpmenu = Menu(menubar,tearoff=0,name="help")
        menubar.add_cascade(label="Help",menu=helpmenu)

        helpmenu.add_command(label='About',command=self.callprogramabout)
        helpmenu.add_separator()
        helpmenu.add_command(label='Help',command=self.showclickhelp)

        #notebook interior for major tabs
        self.xrdnb=Pmw.NoteBook(xrdwin)
        self.xrdnb.configure(hull_background='#d4d0c8')
        self.xrdnb.recolorborders()          
        self.xrdnb.pack(fill="both",expand=1)

        calpage=self.xrdnb.add('Calibration')
        ################ Calibrate Page
        #load file
        filebar = Frame(calpage, relief=SUNKEN,bd=2)

        #load data file and display
        self.fileentry=Pmw.EntryField(filebar,label_text="Data File:",
                labelpos=W,validate=None,entry_width=68,command=DISABLED) 
        self.fileentry.pack(side=LEFT,padx=5,pady=2,fill=X)

        # this is stolen from Sam's code (sixPack) and is 
        # used to get pretty file pictures on the buttons.
        filepath=os.getcwd()+os.sep

        #get file name from directory
        b=Button(filebar,bitmap="@"+filepath+"xbms"+os.sep+"openfolder.xbm",
                height=21,width=50,command=self.selectDiffractionFiles,
                bg='lightyellow') 
        b.pack(side=LEFT,padx=2,pady=2)

        #load data file and display
        b=Button(filebar,text="Load",bg='darkgreen',fg='snow',
                command=self.loadDiffractionFile) 
        b.pack(side=LEFT,padx=2,pady=2)
        filebar.pack(side=TOP,padx=2,pady=2,fill=X)       

        #background file (dark current)
        filebar=Frame(calpage, relief=SUNKEN,bd=2)

        #load dark current and subtract-display
        self.dcfileentry=Pmw.EntryField(filebar, 
                label_text="Dark Current:",labelpos=W,validate=None,
                entry_width=68,command=DISABLED,) 
        self.dcfileentry.pack(side=LEFT,padx=5,pady=2,fill=X)

        self.dcfileentry.component('entry').config(state=DISABLED)
        self.dcfileentry.component('label').config(state=DISABLED)

        #get file name from directory
        b=Button(filebar, bitmap="@"+filepath+"xbms"+os.sep+"openfolder.xbm",
                height=21,width=50,
                command=DISABLED,bg='lightyellow',state=DISABLED) 
        b.pack(side=LEFT,padx=2,pady=2)

        #load dark current and subtract-display
        b=Button(filebar,text="Load",bg='darkgreen',fg='snow',
                command=DISABLED,state=DISABLED) 
        b.pack(side=LEFT,padx=2,pady=2)

        # DO NOT DISPLAY THE DARK CURRENT: INPUTS,
        # THIS SHOULD BE CHANGED AT SOME POINT
        # filebar.pack(side=TOP,padx=2,pady=2,fill=X)


        #Qdata
        filebar=Frame(calpage, relief=SUNKEN,bd=2)
        self.qfileentry=Pmw.EntryField(filebar, label_text="Q Data:",
                labelpos=W,validate=None,
                entry_width=68,command=DISABLED) #load q data
        self.qfileentry.pack(side=LEFT,padx=5,pady=2,fill=X)

        #get file name from directory
        b=Button(filebar, bitmap="@"+filepath+"xbms"+os.sep+"openfolder.xbm",
                height=21,width=50,command=self.selectQDataFile,
                bg='lightyellow') 
        b.pack(side=LEFT,padx=2,pady=2)

        #load Q data 
        b=Button(filebar,text="Load",bg='darkgreen',fg='snow',command=self.loadQData) 
        b.pack(side=LEFT,padx=2,pady=2)

        filebar.pack(side=TOP,padx=2,pady=2,fill=X)
        Pmw.alignlabels([self.fileentry,self.dcfileentry,self.qfileentry])

        #Load/Save/Previous/Header
        l=Label(calpage,text='Calibration Settings',relief=RAISED,bd=2)
        l.pack(side=TOP,padx=0,pady=2,fill=X)
        cv=Frame(calpage)
        cv.pack(side=TOP,padx=2,pady=2,fill='both')
        w=20
        b=Pmw.ButtonBox(cv,label_text="Calibration Values",
                labelpos='n',orient='vertical')
        b.add('Get From Header',command=self.calibrationDataFromHeader,
                bg='darkgreen',fg='white',width=w)
        self.getFromHeaderButton = b.component('Get From Header')
        b.add('Load From File',command=self.calibrationDataLoad,
                bg='royalblue3',fg='white',width=w)
        self.loadFromFileButton = b.component('Load From File')
        b.add('Previous Values',command=self.calibrationDataUndo,
                bg='goldenrod4',fg='white',width=w)
        self.previousValuesButton = b.component('Previous Values')
        b.add('Save To File',command=self.calibrationDataSave,
                bg='firebrick4',fg='white',width=w)
        self.saveCalibrationButton = b.component('Save To File')
        b.pack(side=LEFT,padx=15,pady=2,fill=X)
        #Calibration Values/Fixed
        cvl=Frame(cv)
        cvl.pack(side=LEFT,padx=15,pady=2,fill='both')
        lf=Frame(cvl)
        lf.pack(side=TOP,padx=2,pady=1)
        l=Label(lf,text='      Parameter          Fixed?')
        l.pack(side=LEFT,anchor='w',fill='both')
        self.centerX=FieldBox(cvl,name='xc',validate={'validator':'real'})
        self.centerY=FieldBox(cvl,name='yc',validate={'validator':'real'})
        self.distance=FieldBox(cvl,name='d',validate={'validator':'real'})
        self.energyOrWavelength=FieldBox(cvl,validate={'validator':'real'})
        self.alpha=FieldBox(cvl,name=u"\u03B1",
                validate={'validator':'real','min':-90,'max':90})
        self.beta=FieldBox(cvl,name=u"\u03B2",
                validate={'validator':'real','min':-90,'max':90})
        self.rotation=FieldBox(cvl,name=u"R",
                validate={'validator':'real','min':-360,'max':360})
        # pixelLength & pixelHeight don't get checkboxes
        self.pixelLength=FieldBox(cvl,name='pl',
                validate={'validator':'real','min':0},noCheckBox=1)
        self.pixelHeight=FieldBox(cvl,name='ph',
                validate={'validator':'real','min':0},noCheckBox=1)

        Pmw.alignlabels([self.centerX.ef,self.centerY.ef, \
                self.distance.ef,self.energyOrWavelength.ef, \
                self.alpha.ef,self.beta.ef,self.rotation.ef, \
                self.pixelLength.ef,self.pixelHeight.ef])

        #Update and Draw Q,dQ,Peaks
        cvr=Frame(cv)
        cvr.pack(side=LEFT,padx=15,pady=2,fill=X)

        self.drawQ=BoxButton(cvr,name='Draw Q Lines?', 
                func=self.updatebothNoComplain,colorFunc=self.getQColor)
        self.drawdQ=BoxButton(cvr,name='Draw dQ Lines?',
                func=self.updatebothNoComplain,colorFunc=self.getdQColor)
        self.drawPeaks=BoxButton(cvr,name='Draw Peaks?',
                func=self.updatebothNoComplain,colorFunc=self.getPeaksColor)

        self.updateDiffractionImageButton=Button(cvr,text='Update',
                fg='snow',bg='darkgreen',width=w,
                command=self.maindisp.updateimage)
        self.updateDiffractionImageButton.pack(side=TOP,padx=2,pady=20)
        #Do fit
        l=Label(calpage,text='Fit Settings',relief=RAISED,bd=2)
        l.pack(side=TOP,padx=0,pady=2,fill=X)
        ff=Frame(calpage)
        ff.pack(side=TOP,padx=2,pady=2,fill='both')
        ffl=Frame(ff)
        ffl.pack(side=LEFT,padx=40,pady=2)

        b=Pmw.ButtonBox(ffl,labelpos='n',orient='vertical')
        b.add('Do Fit',command=self.doFit,
                bg='darkgreen',fg='snow',width=w)
        self.doFitButton = b.component('Do Fit')
        b.add('Save Last Fit',command=self.saveLastFit,
                bg='royalblue3',fg='snow',width=w)
        self.saveLastFitButton = b.component('Save Last Fit')
        b.add('Make/Save Peak List',command=self.savePeakList,
                bg='goldenrod4',fg='snow',width=w)
        self.makeSavePeakListButton = b.component('Make/Save Peak List')
        b.pack(side=LEFT,padx=15,pady=2,fill=X)

        #Peak list opts
        ffm=Frame(ff)
        ffm.pack(side=LEFT,padx=40,pady=2)

        self.useOldPeakListButton = Checkbutton(ffm, 
                text="Use Old Peak List (if possible)?", 
                variable=self.useOldPeakList)
        self.useOldPeakListButton.pack(side=TOP,padx=5,pady=2)
        self.numberOfChiInput = Pmw.EntryField(ffm,labelpos = 'w',
                label_text = "Number Of Chi?",
                value = '360', entry_width=4,
                validate={'validator':'numeric','min':0,'max':9999})
        self.numberOfChiInput.pack(side=TOP,padx=5,pady=2)
        self.stddev = Pmw.EntryField(ffm,entry_width=10, 
                labelpos = 'w', value = '5',
                label_text ="Stddev?",
                validate={'validator':'real','min':0 } )
        self.stddev.pack(side=TOP,padx=5,pady=2)

        ################ Mask Page
        maskpage=self.xrdnb.add('Masking')
        l=Label(maskpage,text='Masking Options',relief=RAISED,bd=2)
        l.pack(side=TOP,padx=0,pady=2,fill=X)
        
        w=15

        # Threshold masking options

        g=Pmw.Group(maskpage,tag_text='Threshold Masking')
        g.pack(side=TOP,padx=5,pady=10,fill='both')

        temp = Frame(g.interior())
        temp.pack(side=TOP,anchor=CENTER)

        self.doGreaterThanMask=BoxButton(temp,name='Do Greater Than Mask?',
                func=self.updatebothNoComplain,
                colorFunc=self.getGreaterThanMaskColor)

        self.greaterThanMask=Pmw.EntryField(temp,
                labelpos='w',label_text="(Pixels Can't Be) Greater Than Mask:",
                value='',entry_width=w,validate={'validator':'real','min':0})
        self.greaterThanMask.pack(side=TOP)

        self.doLessThanMask=BoxButton(temp,name='Do Less Than Mask?',
                func=self.updatebothNoComplain,
                colorFunc=self.getLessThanMaskColor)

        self.lessThanMask=Pmw.EntryField(temp,
                labelpos='w',label_text="(Pixels Can't Be) Less Than Mask:",
                value='',entry_width=w,
                validate={'validator':'real','min':0})
        self.lessThanMask.pack(side=TOP)

        Pmw.alignlabels([self.greaterThanMask,self.lessThanMask])

        # Polygon Masking Options

        g=Pmw.Group(maskpage,tag_text='Polygon Masking')
        g.pack(side=TOP,padx=5,pady=10,fill='both')

        temp = Frame(g.interior())
        temp.pack(side=TOP,anchor=CENTER)

        left = Frame(temp)
        left.pack(side=LEFT,anchor=CENTER)

        right = Frame(temp)
        right.pack(side=LEFT,anchor=CENTER,padx=80)

        self.doPolygonMask=BoxButton(left,name='Do Polygon Mask?',
                func=self.updatebothNoComplain,
                colorFunc=self.getPolygonMaskColor)

        self.addRemovePolygonRadioSelect =Pmw.RadioSelect(left,
                buttontype = 'button', selectmode = 'multiple',orient='vertical',
                command = self.toggleAddRemovePolygonMaskBindings)

        self.addRemovePolygonRadioSelect.pack(side=TOP,anchor=W,padx=10)
        self.addRemovePolygonRadioSelect.add('Add Polygon') # create the button
        self.addRemovePolygonRadioSelect.add('Remove Polygon')
        self.addPolygonButton = \
                self.addRemovePolygonRadioSelect.component('Add Polygon')
        self.addPolygonButton.config(fg='snow',bg='darkgreen',width=w)
        self.removePolygonButton = \
                self.addRemovePolygonRadioSelect.component('Remove Polygon')
        self.removePolygonButton.config(fg='snow',bg='goldenrod4',width=w)

        self.clearMask=Button(right,text='Clear Mask',width=w,
                fg='snow',bg='firebrick4',command=self.removePolygons)
        self.clearMask.pack(side=TOP,pady=5,anchor=W)

        self.saveMask=Button(right,text='Save Mask',width=w,
                fg='snow',bg='darkgreen',command=self.savePolygonsToFile)
        self.saveMask.pack(side=TOP,pady=5,anchor=W)

        self.loadMask=Button(right,text='Load Mask',width=w,
                fg='snow',bg='royalblue',command=self.loadPolygonsFromFile)
        self.loadMask.pack(side=TOP,pady=5,anchor=W)

        ################ Cake Page
        cakepage=self.xrdnb.add('Cake')
        l=Label(cakepage,text='Caking Settings',relief=RAISED,bd=2)
        l.pack(side=TOP,padx=0,pady=2,fill=X)

        w=20

        self.autoCakeButton=Button(cakepage,text='AutoCake',width=w,
                fg='snow',bg='darkgreen',command=self.autoCake)
        self.autoCakeButton.pack(side=TOP,padx=5,pady=10)

        g=Pmw.Group(cakepage,tag_text='Cake Parameters')
        g.pack(side=TOP,padx=5,pady=10,fill='both')

        width=15

        self.qOrTwoThetaLowerCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Q Lower?",
                value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':999}) 
        self.qOrTwoThetaLowerCake.pack(side=TOP,padx=2,pady=1)

        self.qOrTwoThetaUpperCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Q Upper?",
                value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':999}) 
        self.qOrTwoThetaUpperCake.pack(side=TOP,padx=2,pady=1)

        self.numQOrTwoThetaCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Number Of Q?",
                value = '', entry_width=width,
                validate={'validator':'numeric','min':0,'max':99999}) 
        self.numQOrTwoThetaCake.pack(side=TOP,padx=2,pady=1)

        self.chiLowerCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Chi Lower?",
                value = '', entry_width=width,
                validate={'validator':'real','min':-360,'max':360}) 
        self.chiLowerCake.pack(side=TOP,padx=2,pady=1)

        self.chiUpperCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Chi Upper?",
                value = '', entry_width=width,
                validate={'validator':'real','min':-360,'max':360}) 
        self.chiUpperCake.pack(side=TOP,padx=2,pady=1)

        self.numChiCake=Pmw.EntryField(g.interior(),
                labelpos = 'w', label_text = "Number Of Chi?",
                value = '', entry_width=width,
                validate={'validator':'numeric','min':0,'max':99999}) 
        self.numChiCake.pack(side=TOP,padx=2,pady=1)

        Pmw.alignlabels([self.qOrTwoThetaLowerCake,self.qOrTwoThetaUpperCake, \
                self.numQOrTwoThetaCake,self.chiLowerCake, \
                self.chiUpperCake,self.numChiCake])

        ffm = Frame(cakepage)
        ffm.pack(side=TOP,anchor=CENTER,pady=10)

        self.doPolarizationCorrectionCakeButton = Checkbutton(ffm, 
                text="Do Polarization Correction?", 
                variable=self.doPolarizationCorrectionCake,
                command=self.cakedisp.updateimageNoComplainWithdrawIfError)
        self.doPolarizationCorrectionCakeButton.pack(side=TOP,anchor=W)

        self.PCake = Pmw.EntryField(ffm,labelpos = 'w', label_text = "P?",
                value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':1})
        self.PCake.pack(side=TOP,anchor=W)

        w=15
        b=Pmw.ButtonBox(cakepage,orient='horizontal')
        b.pack(side=TOP,padx=10,pady=10)
        b.add('Do Cake',fg='snow',bg='darkgreen',width=w,
                command=self.cakedisp.updateimage)
        self.doCakeButton=b.component('Do Cake')
        b.add('Last Cake',fg='snow',bg='goldenrod4',width=w,
                command=self.undoZoomCakeImage)
        self.lastCakeButton=b.component('Last Cake')
        b.add('Save Image',fg='snow',bg='royalblue',width=w,
                command=self.saveCakeImage)
        self.saveCakeImageButton=b.component('Save Image')
        b.add('Save Data',fg='snow',bg='firebrick4',width=w,
                command=self.saveCakeData)
        self.saveCakeDataButton=b.component('Save Data')

        ################ Integrate Page
        intpage=self.xrdnb.add('Integrate')
        l=Label(intpage,text='Integration Settings',relief=RAISED,bd=2)
        l.pack(side=TOP,padx=0,pady=2,fill=X)

        f=Frame(intpage)
        f.pack(side=TOP,padx=2,pady=5)

        #apply the label automatically depending on 
        # if in Q or 2theta mode
        qg=Pmw.Group(f,tag_text='') 
        self.QOrTwoThetaIntegrationLabel = qg
        qg.pack(side=LEFT,padx=5,pady=5,fill='both')
        cg=Pmw.Group(f,tag_text='Chi-I Integration')
        cg.pack(side=LEFT,padx=5,pady=5,fill='both')
        w=20
        #Q-I side
        self.autoIntegrateQOrTwoThetaIButton=Button(qg.interior(),
                text='AutoIntegrate',width=w,fg='snow',
                bg='darkgreen',command=self.autoIntegrateQOrTwoThetaI)
        self.autoIntegrateQOrTwoThetaIButton.pack(side=TOP,padx=5,pady=5)

        self.QOrTwoThetaLowerIntegrate=Pmw.EntryField(qg.interior(),
                labelpos = 'w', label_text = "Q Lower?",
                value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':999}) 
        self.QOrTwoThetaLowerIntegrate.pack(side=TOP,padx=2,pady=1)

        self.QOrTwoThetaUpperIntegrate=Pmw.EntryField(qg.interior(),
                labelpos = 'w', label_text = "Q Upper?",
                value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':999}) 
        self.QOrTwoThetaUpperIntegrate.pack(side=TOP,padx=2,pady=1)

        self.numQOrTwoThetaIntegrate=Pmw.EntryField(qg.interior(),
                labelpos = 'w', label_text = "Number Of Q?",
                value = '', entry_width=width,
                validate={'validator':'numeric','min':0,'max':99999}) 
        self.numQOrTwoThetaIntegrate.pack(side=TOP,padx=2,pady=1)

        Pmw.alignlabels([self.QOrTwoThetaLowerIntegrate, \
                self.QOrTwoThetaUpperIntegrate,self.numQOrTwoThetaIntegrate])

        self.constrainWithRangeOnRightButton = Checkbutton(qg.interior(), 
                text='Constrain With Range On Right?', 
                wraplength=120,
                justify=LEFT,
                variable = self.constrainWithRangeOnRight,
                command=self.resetIntegrationDisplay)
        self.constrainWithRangeOnRightButton.pack(side=TOP,
                padx=20,pady=5,anchor=W)

        self.integrateQOrTwoThetaIButton=Button(qg.interior(),
                text='Integrate',fg='snow',bg='darkgreen',
                width=width,command=self.integrateQOrTwoThetaI)        
        self.integrateQOrTwoThetaIButton.pack(side=TOP,padx=5,pady=5)
        
        #Chi-I side
        self.autoIntegrateChiIButton=Button(cg.interior(),
                text='AutoIntegrate',width=w,fg='snow',
                bg='darkgreen',command=self.autoIntegrateChiI)
        self.autoIntegrateChiIButton.pack(side=TOP,padx=5,pady=5)

        self.chiLowerIntegrate=Pmw.EntryField(cg.interior(),
                labelpos = 'w', label_text = "Chi Lower?",
                value = '', entry_width=width,
                validate={'validator':'real','min':-360,'max':360}) 
        self.chiLowerIntegrate.pack(side=TOP,padx=2,pady=1)

        self.chiUpperIntegrate=Pmw.EntryField(cg.interior(),
                labelpos = 'w', label_text = "Chi Upper?",
                value = '', entry_width=width,
                validate={'validator':'real','min':-360,'max':360}) 
        self.chiUpperIntegrate.pack(side=TOP,padx=2,pady=1)

        self.numChiIntegrate=Pmw.EntryField(cg.interior(),
                labelpos = 'w', label_text = "Number Of Chi?",
                value = '', entry_width=width,
                validate={'validator':'numeric','min':0,'max':99999}) 
        self.numChiIntegrate.pack(side=TOP,padx=2,pady=1)

        Pmw.alignlabels([self.chiLowerIntegrate,self.chiUpperIntegrate, \
                self.numChiIntegrate])        

        self.constrainWithRangeOnLeftButton = Checkbutton(cg.interior(), 
                text='Constrain With Range On Left?', 
                wraplength=120,
                justify=LEFT,
                variable = self.constrainWithRangeOnLeft,
                command=self.resetIntegrationDisplay)
        self.constrainWithRangeOnLeftButton.pack(side=TOP,padx=20, \
                pady=5,anchor=W)

        self.integrateChiIButton=Button(cg.interior(),
                text='Integrate',fg='snow',bg='darkgreen',
                width=w,command=self.integrateChiI)
        self.integrateChiIButton.pack(side=TOP,padx=5,pady=5)
        
        ffm = Frame(intpage)
        ffm.pack(side=TOP,anchor=CENTER,pady=10)
        
        self.doPolarizationCorrectionIntegrateButton = \
                Checkbutton(ffm, text="Do Polarization Correction?", 
                variable=self.doPolarizationCorrectionIntegrate,
                command=self.resetIntegrationDisplay)
        self.doPolarizationCorrectionIntegrateButton.pack(side=TOP,anchor=W)

        self.PIntegrate = Pmw.EntryField(ffm,labelpos = 'w',
                label_text = "P?",value = '', entry_width=width,
                validate={'validator':'real','min':0,'max':1})
        self.PIntegrate.pack(side=TOP,anchor=W)

        self.saveIntegrationDataButton=Button(intpage,
                text='Save Data',fg='snow',bg='firebrick4',
                width=15,command=self.saveIntegratedIntensity)
        self.saveIntegrationDataButton.pack(side=TOP,padx=5,pady=10)
    
        #clean up notebook sizing
        self.xrdnb.setnaturalsize()
        #status bar
        botfr=Frame(xrdwin)
        botfr.pack(side=TOP,fill=X)        
        self.status=Label(botfr,text="",bd=2,
                relief=RAISED,anchor=W,fg='blue')
        self.status.pack(side=LEFT,fill=X,expand=1)
        setstatus(self.status,"Ready")        

        self.macrostatus=Label(botfr,text="",bd=2,
                relief=RAISED,anchor=E,fg='red')

        # let the display functions know about status so 
        # that they can set things properly when they do 
        # the calculation
        self.maindisp.status=self.status
        self.cakedisp.status=self.status

        # this must be called before the calls to the 
        # change functions. Give it this object to work on
        self.macroMode = MacroMode(self,setstatus) 

        # have the titles of self.energyOrWavelength set 
        # to the right thing
        self.changeEVorLambda(to='Work in eV') 

        # have the title of self.energyOrWavelength set 
        # to the right thing
        self.changeQor2Theta(to='Work in Q') 

        Pmw.reporterrorstofile(FancyErrors(self.status))

        # try to run the program initialization macro
        self.runInitializationMacro()
        
 
    def selectDefaultFolder(self):

        defaultDir = tkFileDialog.askdirectory(title='Pick a directory',
                initialdir=self.defaultDir)

        if defaultDir in ['',()]: return 

        # put the filename(s) into the input 
        self.preferencesdisplay.defaultFolderEntry.setvalue(defaultDir)

        # set the default folder
        self.setDefaultFolder()


    def setDefaultFolder(self):

        defaultDir = self.preferencesdisplay.defaultFolderEntry.getvalue()

        # allow empty strings to signify that there is no default folder
        if not os.path.isdir(defaultDir) and defaultDir != '':
            raise UserInputException("Cannot set as the default directory \
because it does not exist.")

        self.defaultDir = defaultDir


        if not os.path.isdir('Preferences'):
            os.mkdir('Preferences')

        # setting to blank = getting rid of the default directory
        if defaultDir == '':
            if os.path.isfile('Preferences/DefaultDirectory.dat'):
                os.remove('Preferences/DefaultDirectory.dat')
            return

        # save this to a file to preserve state
        file = open('Preferences/DefaultDirectory.dat','w')
        file.write(self.defaultDir)
        file.close()

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Default Folder:',
                    '\t %s' % filename)


    def defaultFolderFromFile(self):
        
        if os.path.isfile('Preferences/DefaultDirectory.dat'):
            file = open('Preferences/DefaultDirectory.dat')
            defaultDir = file.readline()
            file.close()

            if os.path.isdir(defaultDir):
                self.preferencesdisplay.defaultFolderEntry.setvalue(defaultDir)
                self.setDefaultFolder()

 
    def addStandardQ(self,qmenu):
        files = os.listdir(self.standardQFolder) 
        for file in files:
            (basename,extension) = os.path.splitext(file)
            # only include standard Q files that end in .dat
            if extension == '.dat':
                # I have to call this funny selectStandardQDataFile() 
                # function so that it will do the macro recording 
                load = (lambda file=file,standardQFolder=self.standardQFolder, \
                        self=self,basename=basename:self.selectStandardQDataFile(
                        basename,standardQFolder+os.sep+file))
                qmenu.add_command(label=basename,command=load)
        
        
    def runInitializationMacro(self):
        # run the initialization macro if it is a file
        if os.path.isfile('Preferences/InitializationMacro.dat'):
            try:
                self.macroMode.runMacroFromFilename('Preferences/InitializationMacro.dat',
                        moveAround=0,VERBOSE=0)
            except Exception, e:
                # just print out the error b/c we are not in 
                # the mainloop where errors can be handled
                # gracefully.
                print "Error running the initialization macro \
Preferences/InitializationMacro.dat: "+str(e)+"\n"


    def resetGui(self):
        """ Reset the Gui to its initial settings, at least mostly.
            
            Here is what should stay after you reset:
            * The calibration data
            * The check boxes should stay however they are pushed
            * Any of the Q or chi range inputs
            * However much the display windows have been stretched
            * The Stddev and number of chi values

            Here is what should be reset:
            * The diffraction file
            * The Q data
            * The peak list
            * The integration graph, 
            * The diffraction graph should look liken when you start
            * The cake graph should look liken when you start
            * All the image and graph displays should be again hidden
        """
        self.diffractionData= None
        self.peakList = None

        self.fileentry.setvalue('')
        self.dcfileentry.setvalue('')
        
        # keep the Q value, at lest for now
        #QData = None
        #self.qfileentry.setvalue('')

        # reset integration page
        self.integrate = None         
        self.integratedisp.main.withdraw()
        self.integratedisp.reset()

        # reset diffraction page
        self.maindisp.main.withdraw()
        self.diffractionImageZoomPixels = []

        if self.diffractionImageID != None:
            self.maindisp.imframe.delete(self.diffractionImageID)
        self.diffractionImageID = None
        
        # delete Q lines diffraction image
        for id in self.allQLineIDsDiffractionImage:
            self.maindisp.imframe.delete(id)
        self.allQLineIDsDiffractionImage = []

        # delete peaks diffraction image
        for id in self.allPeakListIDsDiffractionImage:
            self.maindisp.imframe.delete( id ) 
        self.allPeakListIDsDiffractionImage = []

        # do cake page
        self.cakedisp.main.withdraw()
        self.cake = None
        self.cakeRange = []

        if self.cakeImageID != None:
            self.cakedisp.imframe.delete(self.cakeImageID)
        self.cakeImageID = None

        # delete Q lines cake image
        for id in self.allQLineIDsCakeImage:
            self.cakedisp.imframe.delete(id)
        self.allQLineIDsCakeImage = []

        # delete peaks cake image
        for id in self.allPeakListIDsCakeImage:
            self.cakedisp.imframe.delete( id ) 
        self.allPeakListIDsCakeImage = []

        # rest the menu
        removeAllItemsFromMenu(self.openedfilesmenu)
        self.openedfilesmenu.add_command(label='None',command=DISABLED)


    def changeEVorLambda(self,to=None):
        if to != None:
            self.eVorLambda.set(to)

        # change the labels
        if self.eVorLambda.get() == 'Work in eV':
            self.energyOrWavelength.ef.configure(label_text='E:')
        elif self.eVorLambda.get() == "Work in Lambda":
            self.energyOrWavelength.ef.configure(label_text=u"\u019B:")
        else:
            raise UserInputException("The program must run in \
either units of either eV or wavelength.")

        # if switching from one to the other, convert the numbers
        if self.eVorLambda.get() != self.lasteVorLambda.get():
            if self.energyOrWavelength.ef.getvalue() != '':
                if self.eVorLambda.get() == 'Work in eV':
                    wavelength = float(self.energyOrWavelength.ef.getvalue())
                    self.energyOrWavelength.ef.setvalue(
                            Transform.convertWavelengthToEnergy(wavelength))
                elif self.eVorLambda.get() == 'Work in Lambda':
                    energy = float(self.energyOrWavelength.ef.getvalue())
                    self.energyOrWavelength.ef.setvalue(
                            Transform.convertEnergyToWavelength(energy))
                else:
                    raise UserInputException("The program must \
run in either units of either eV or wavelength.")

        self.lasteVorLambda.set(self.eVorLambda.get())

        # Explicityly record macro. Only do so if in record macro mode
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordOneLine(self.eVorLambda.get())


    def resetIntegrationDisplay(self):
        self.integrate = None         
        self.integratedisp.main.withdraw()
        self.integratedisp.reset()


    def changeQor2Theta(self,to=None):
        if to != None:
            self.Qor2Theta.set(to)

        # change the labels
        if self.Qor2Theta.get() == 'Work in Q':
            self.QOrTwoThetaIntegrationLabel.configure(tag_text='Q-I Integration')
            self.QOrTwoThetaLowerIntegrate.configure(label_text="Q Lower?")
            self.QOrTwoThetaUpperIntegrate.configure(label_text="Q Upper?")
            self.numQOrTwoThetaIntegrate.configure(label_text="Number Of Q?")

            self.qOrTwoThetaLowerCake.configure(label_text="Q Lower?")
            self.qOrTwoThetaUpperCake.configure(label_text="Q Upper?")
            self.numQOrTwoThetaCake.configure(label_text="Number Of Q?")

            # convert any previous cake zoom levels from
            # two theta to Q
            for zoom in self.cakeRange:
                zoom['qOrTwoThetaLower'] = Transform.convertTwoThetaToQ(
                        zoom['qOrTwoThetaLower'],self.calibrationData[-1])
                zoom['qOrTwoThetaUpper'] = Transform.convertTwoThetaToQ(
                        zoom['qOrTwoThetaUpper'],self.calibrationData[-1])

        elif self.Qor2Theta.get() == "Work in 2theta":
            self.QOrTwoThetaIntegrationLabel.configure(tag_text=u"2\u03D1-I Integration")
            self.QOrTwoThetaLowerIntegrate.configure(label_text=u"2\u03D1 Lower?")
            self.QOrTwoThetaUpperIntegrate.configure(label_text=u"2\u03D1 Upper?")
            self.numQOrTwoThetaIntegrate.configure(label_text=u"Number Of 2\u03D1?")

            self.qOrTwoThetaLowerCake.configure(label_text=u"2\u03D1 Lower?")
            self.qOrTwoThetaUpperCake.configure(label_text=u"2\u03D1 Upper?")
            self.numQOrTwoThetaCake.configure(label_text=u"Number Of 2\u03D1?")

            # convert any previous cake zoom levels from
            # two theta to Q
            for zoom in self.cakeRange:
                zoom['qOrTwoThetaLower'] = Transform.convertQToTwoTheta(
                        zoom['qOrTwoThetaLower'],self.calibrationData[-1])
                zoom['qOrTwoThetaUpper'] = Transform.convertQToTwoTheta(
                        zoom['qOrTwoThetaUpper'],self.calibrationData[-1])

        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")

        # re-align the labels
        Pmw.alignlabels([self.QOrTwoThetaLowerIntegrate, \
                self.QOrTwoThetaUpperIntegrate,self.numQOrTwoThetaIntegrate])

        # if switching from one to the other, try to convert the numbers
        if self.Qor2Theta.get() != self.lastQor2Theta.get():
            try:
                # try to update the calibration data first
                self.addUserInputCalibrationDataToObject()

                if self.Qor2Theta.get() == 'Work in Q':

                    if self.qOrTwoThetaLowerCake.getvalue() != '':
                        twoThetaLower = float(self.qOrTwoThetaLowerCake.getvalue())
                        self.qOrTwoThetaLowerCake.setvalue(
                                Transform.convertTwoThetaToQ(
                                twoThetaLower,self.calibrationData[-1]))
                    if self.qOrTwoThetaUpperCake.getvalue() != '':
                        twoThetaUpper = float(self.qOrTwoThetaUpperCake.getvalue())
                        self.qOrTwoThetaUpperCake.setvalue(
                                Transform.convertTwoThetaToQ(
                                twoThetaUpper,self.calibrationData[-1]))

                    if self.QOrTwoThetaLowerIntegrate.getvalue() != '':
                        twoThetaLower = float(self.QOrTwoThetaLowerIntegrate.getvalue())
                        self.QOrTwoThetaLowerIntegrate.setvalue(
                                Transform.convertTwoThetaToQ(
                                twoThetaLower,self.calibrationData[-1]))
                    if self.QOrTwoThetaUpperIntegrate.getvalue() != '':
                        twoThetaUpper = float(self.QOrTwoThetaUpperIntegrate.getvalue())
                        self.QOrTwoThetaUpperIntegrate.setvalue(
                                Transform.convertTwoThetaToQ(
                                twoThetaUpper,self.calibrationData[-1]))

                elif self.Qor2Theta.get() == "Work in 2theta":

                    if self.qOrTwoThetaLowerCake.getvalue() != '':
                        qLower = float(self.qOrTwoThetaLowerCake.getvalue())
                        self.qOrTwoThetaLowerCake.setvalue(
                                Transform.convertQToTwoTheta(
                                qLower,self.calibrationData[-1]))
                    if self.qOrTwoThetaUpperCake.getvalue() != '':
                        qUpper = float(self.qOrTwoThetaUpperCake.getvalue())
                        self.qOrTwoThetaUpperCake.setvalue(
                                Transform.convertQToTwoTheta(
                                qUpper,self.calibrationData[-1]))

                    if self.QOrTwoThetaLowerIntegrate.getvalue() != '':
                        qLower = float(self.QOrTwoThetaLowerIntegrate.getvalue())
                        self.QOrTwoThetaLowerIntegrate.setvalue(
                                Transform.convertQToTwoTheta(
                                qLower,self.calibrationData[-1]))
                    if self.QOrTwoThetaUpperIntegrate.getvalue() != '':
                        qUpper = float(self.QOrTwoThetaUpperIntegrate.getvalue())
                        self.QOrTwoThetaUpperIntegrate.setvalue(
                                Transform.convertQToTwoTheta(
                                qUpper,self.calibrationData[-1]))
                else:
                    raise UserInputException("The program must \
work in either Q or 2theta mode.")
            except Exception, e:
                # if that didn't work, then just make the new vals blank
                self.QOrTwoThetaLowerIntegrate.setvalue('')
                self.QOrTwoThetaUpperIntegrate.setvalue('')

        self.lastQor2Theta.set(self.Qor2Theta.get())

        # reset integration display
        self.resetIntegrationDisplay()

        # update the cake disp
        self.updatebothNoComplain()
        

        # Explicityly record macro. Only do so if in record macro mode
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordOneLine(self.Qor2Theta.get())


    def callprogramabout(self):
        programabout(self.xrdwin)


    def showclickhelp(self):
        # For some reason, on the Mac, the command:
        #  > webbrowser.open('tips_and_tricks.html')
        # crashes, but this seems to do the right thing.
        webbrowser.open(os.path.abspath('tips_and_tricks.html'))


    def getQColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.qLinesColor.set(color)
        self.updatebothNoComplain()


    def getdQColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.dQLinesColor.set(color)
        self.updatebothNoComplain()


    def getPeaksColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.peakLinesColor.set(color)
        self.updatebothNoComplain()


    def getGreaterThanMaskColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.greaterThanMaskColor.set(color)
        self.updatebothNoComplain()

    def getLessThanMaskColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.lessThanMaskColor.set(color)
        self.updatebothNoComplain

    def getPolygonMaskColor(self,color=None):
        if color==None:
            color = askcolor()[1]

        if color != None:
            self.polygonMaskColor.set(color)
        self.updatebothNoComplain


    def getRealDiffractionImageCoordinates(self,x,y):
        """ Returns the real pixel values corresponding 
            to canvas x,y values. """

        if self.diffractionImageZoomPixels==[]:
            minRealX = 0
            minRealY = 0
            maxRealX = self.diffractionData.getSize()-1
            maxRealY = self.diffractionData.getSize()-1
        else:
            current = self.diffractionImageZoomPixels[-1]
            minRealX = min(current[0]['x'],current[1]['x'] )
            maxRealX = max(current[0]['x'],current[1]['x'] )

            minRealY = min(current[0]['y'],current[1]['y'] )
            maxRealY = max(current[0]['y'],current[1]['y'] )

        realRangeX = maxRealX-minRealX
        scaleX = 1.0*realRangeX / (self.diffractionImageSize-1)
        realX = minRealX + scaleX*x

        realRangeY = maxRealY-minRealY
        scaleY = 1.0*realRangeY / (self.diffractionImageSize-1)
        realY = minRealY + scaleY*y

        # make sure coordinates are not too big or small
        size = self.diffractionData.getSize()

        if realX<0: realX=0
        if realX>=size: realX=size-1
        if realY<0: realY=0
        if realY>=size: realY=size-1

        return realX,realY


    def getCanvasDiffractionImageCoordinates(self,realX,realY):
        """ Returns the canvas values x,y corresponding 
            to real pixels. """
        if self.diffractionImageZoomPixels==[]:
            minRealX = 0
            minRealY = 0
            maxRealX = self.diffractionData.getSize()-1
            maxRealY = self.diffractionData.getSize()-1
        else:
            current = self.diffractionImageZoomPixels[-1]
            minRealX = min(current[0]['x'],current[1]['x'] )
            maxRealX = max(current[0]['x'],current[1]['x'] )

            minRealY = min(current[0]['y'],current[1]['y'] )
            maxRealY = max(current[0]['y'],current[1]['y'] )

        realRangeX = maxRealX-minRealX
        scaleX = 1.0*realRangeX / (self.diffractionImageSize-1)

        x = (realX-minRealX)/scaleX

        realRangeY = maxRealY-minRealY
        scaleY = 1.0*realRangeY / (self.diffractionImageSize-1)

        y = (realY-minRealY)/scaleY

        return x,y
   
    def noCoordReportUpdateDiffractionImage(self):
        self.maindisp.xcoord.config(text="X=      ")
        self.maindisp.ycoord.config(text="Y=      ")
        self.maindisp.qcoord.config(text="Q=      ")
        self.maindisp.dcoord.config(text="D=      ")
        self.maindisp.ccoord.config(text="chi=      ")
        self.maindisp.icoord.config(text="I=      ")

    def coordReportUpdateDiffractionImage(self,xInput,yInput):
        """ x,y are dixel distances relative to the canvas. """
        x,y = self.getRealDiffractionImageCoordinates(xInput,yInput)

        intensity = self.diffractionData.theDiffractionData.data[int(x)][int(y)] 
        text=("X="+str(x))[:12] 
        self.maindisp.xcoord.config(text=text)
        text=("Y="+str(y))[:12] 
        self.maindisp.ycoord.config(text=text)
        text=("I="+str(intensity))[:12] 
        self.maindisp.icoord.config(text=text)

        if self.calibrationData and self.calibrationData[-1].allSet():
            Q,chi = Transform.getQChi(self.calibrationData[-1], x,y)
            text=("Q="+str(Q))[:12] 
            self.maindisp.qcoord.config(text=text)
            if Q == 0:
                self.maindisp.dcoord.config(text="D=      ")
            else:
                D=2*math.pi/Q
                text=("D="+str(D))[:12] 
                self.maindisp.dcoord.config(text=text)
            text=("chi="+str(chi))[:12]
            self.maindisp.ccoord.config(text=text)
        else:
            self.maindisp.qcoord.config(text="Q=      ")
            self.maindisp.dcoord.config(text="D=      ")
            self.maindisp.ccoord.config(text="chi=      ")


    def mouseLeaveDiffractionImage(self,event):
        """ Stop reporting cordinates. """
        self.noCoordReportUpdateDiffractionImage()


    def mouseDragNoPressDiffractionImage(self,event):
        """ Display x,y and (possibly) Q,chi cordinates, 
            but do not redraw rectangle. """
        self.coordReportUpdateDiffractionImage(event.x,event.y)
 
    
    def resizeDiffractionImage(self,event):
        """ When the frame holding the graphs gets 
            resized because the image canvas gets 
            streched by the user, redraw the cake image
            and the axis to fill the newly avalible space. """
        
        # resize canvas properly
        if event.width <= self.axisSize or \
                event.height <= self.axisSize:
            return

        self.diffractionImageSize = \
                min(event.width-self.axisSize,
                event.height-self.axisSize)

        self.maindisp.imframe.config(height=self.diffractionImageSize,
                width=self.diffractionImageSize)

        self.maindisp.bottomAxis.config(width=self.diffractionImageSize,
                height=self.axisSize)

        self.maindisp.rightAxis.config(width=self.axisSize,
                height=self.diffractionImageSize)

        # redraw the image
        self.maindisp.updateimageNoComplain()


    def getAllowedRange(self,x0,y0,x1,y1):
        """ Returns the largest square which will fit into x0,y0, 
            which is also fully contained in the image. """

        realX0,realY0 = self.getRealDiffractionImageCoordinates(x0,y0)
        realX1,realY1 = self.getRealDiffractionImageCoordinates(x1,y1)

        size = self.diffractionData.getSize()

        # constrain our cordinates to being in the real image
        if realX0<0: realX0 = 0
        if realX0>size-1: realX0 = size-1

        if realX1<0: realX1 = 0
        if realX1>size-1: realX1 = size-1

        if realY0<0: realY0 = 0
        if realY0>size-1: realY0 = size-1

        if realY1<0: realY1 = 0
        if realY1>size-1: realY1 = size-1

        # turn these values back into a convase range which is real pixels 
        x0,y0 = self.getCanvasDiffractionImageCoordinates(realX0,realY0)
        x1,y1 = self.getCanvasDiffractionImageCoordinates(realX1,realY1)

        # now, figure out wether the x or y range is bigger.
        # use the smaller one to build the largest square which 
        # will fit into our range
        if abs(y1-y0) < abs(x1-x0):
            smallerDifferenceY = y1-y0
            if x1-x0 > 0:
                smallerDifferenceX = abs(y1-y0)
            else:
                smallerDifferenceX = -1*abs(y1-y0)
        else:
            smallerDifferenceX = x1-x0
            if y1-y0 > 0:
                smallerDifferenceY = abs(x1-x0)
            else:
                smallerDifferenceY = -1*abs(x1-x0)

        return x0,y0,x0+smallerDifferenceX,y0+smallerDifferenceY


    def mouseDragZoomDiffractionImage(self,event):
        """ Display x,y and (possibly) Q,chi cordinates and redraw rectangle. """
        global x0, y0, x1, y1, druged
        druged = 1
        (x1, y1) = event.x, event.y

        allowedX0,allowedY0,allowedX1,allowedY1 = \
                self.getAllowedRange(x0,y0,x1,y1)

        # redraw biggest square which will fit in the user selected rectangle
        try:
            self.maindisp.imframe.coords(self.zoomRectangle,allowedX0,
                    allowedY0,allowedX1,allowedY1)
        except:
            # it dosen't matter if this fails
            pass

        self.coordReportUpdateDiffractionImage(x1,y1)
 

    def mouseUpZoomDiffractionImage(self,event):
        global druged
        global x0, y0, x1, y1        

        self.maindisp.imframe.unbind(sequence="<Motion>")
        self.maindisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragNoPressDiffractionImage)
        self.maindisp.imframe.unbind(sequence="<ButtonRelease>")

        # If this was a left click, try to zoom in. Otherwise, zoom out
        if event.num == 1:
            self.maindisp.imframe.delete( self.zoomRectangle )
            # ensure that the user would zoom into a real window

            # the maximum legit zoom range (which stays inside the image and is a square
            allowedX0,allowedY0,allowedX1,allowedY1 = \
                self.getAllowedRange(x0,y0,x1,y1)

            if druged and (abs(allowedX1-allowedX0)>1 and abs(allowedY1-allowedY0)>1):

                realX0,realY0 = self.getRealDiffractionImageCoordinates(
                        allowedX0,allowedY0)
                realX1,realY1 = self.getRealDiffractionImageCoordinates(
                        allowedX1,allowedY1)

                # set the new zoom scale
                self.doZoomDiffractionImage(
                        ({'x':min(realX0,realX1),'y':min(realY0,realY1)}, 
                        {'x':max(realX0,realX1),'y':max(realY0,realY1)}))
        else:
            self.undoZoomDiffractionImage()


    def mouseDownZoomDiffractionImage(self,event):
        global druged, x0, y0, x1, y1
        druged = 0
        (x0, y0) = event.x, event.y
        (x1, y1) = event.x, event.y
        self.maindisp.imframe.bind(sequence="<Motion>",  
                func=self.mouseDragZoomDiffractionImage)        
        self.maindisp.imframe.bind(sequence="<ButtonRelease>", 
                func=self.mouseUpZoomDiffractionImage)

        # if right click = zoom in, draw the rectangle
        if event.num==1:
            self.zoomRectangle = \
                    self.maindisp.imframe.create_rectangle(
                    x0,y0,x0,y0,dash=(2,2), 
                    outline="black" )


    def mouseDragPanDiffractionImage(self,event): 
        global druged, lastX, lastY

        druged = 1
        currentX, currentY = event.x, event.y

        # if we are fully zoomed out, do not bother panning
        if self.diffractionImageZoomPixels==[]:
            return 

        # if the mouse has not moved very much, do nothing
        if abs(currentX-lastX) < 1 and abs(currentY-lastY) < 1:
            return 

        pixel1X = min(self.diffractionImageZoomPixels[-1][0]['x'],
                self.diffractionImageZoomPixels[-1][1]['x'])
        pixel2X = max(self.diffractionImageZoomPixels[-1][0]['x'],
                self.diffractionImageZoomPixels[-1][1]['x'])
        pixel1Y = min(self.diffractionImageZoomPixels[-1][0]['y'],
                self.diffractionImageZoomPixels[-1][1]['y'])
        pixel2Y = max(self.diffractionImageZoomPixels[-1][0]['y'],
                self.diffractionImageZoomPixels[-1][1]['y'])

        # figure out how far, in real image cordinates, the 
        # person has moved the mouse since last time. To do 
        # this, we figure out the ratio of the image moved 
        # over and multiply that by the total real distance 
        # being displayed in the image
        realDifferenceX = ((currentX-lastX)*1.0/ \
                self.diffractionImageSize)*abs(pixel1X-pixel2X)
        realDifferenceY = ((currentY-lastY)*1.0/ \
                self.diffractionImageSize)*abs(pixel1Y-pixel2Y)

        # the image is drawn with different axis on the 
        # screen (negative to postive) then the cordinates 
        # which are given by our event.x and event.y 
        # To account for this, our realDifferenceX and
        # realDifferenceY are the negative of what they 
        # should be, so we subtract them instead
        new1X = pixel1X - realDifferenceX
        new1Y = pixel1Y - realDifferenceY
        new2X = pixel2X - realDifferenceX
        new2Y = pixel2Y - realDifferenceY

        # make sure not to pan off the image. 
        # Do so by forcing it back onto the image
        size = self.diffractionData.getSize()

        # if it overlaps off one edge, it can't overlap 
        # off the other edge. So, we don't have to 
        # worry about one of these conditions undoing another
        # And therefore, we don't have to worry about doing 
        # any elifs and can do only lots of ifs.
        if new1X < 0: 
            diff = abs(new1X)
            new1X += diff
            new2X += diff
        if new2X < 0: 
            diff = abs(new2X)
            new1X += diff
            new2X += diff
        if new1X > (size-1): 
            diff = abs(new1X-(size-1))
            new1X -= diff
            new2X -= diff
        if new2X > (size-1): 
            diff = abs(new2X-(size-1))
            new1X -= diff
            new2X -= diff

        if new1Y < 0: 
            diff = abs(new1Y)
            new1Y += diff
            new2Y += diff
        if new2Y < 0: 
            diff = abs(new2Y)
            new1Y += diff
            new2Y += diff
        if new1Y > (size-1): 
            diff = abs(new1Y-(size-1))
            new1Y -= diff
            new2Y -= diff
        if new2Y > (size-1): 
            diff = abs(new2Y-(size-1))
            new1Y -= diff
            new2Y -= diff

        # store where we are now
        lastX,lastY = currentX,currentY 

        # replace current zoom level
        self.diffractionImageZoomPixels[-1] = \
                ({'x':new1X,'y':new1Y}, {'x':new2X,'y':new2Y})  
        self.maindisp.updateimage()
        self.coordReportUpdateDiffractionImage(x1,y1)


    def mouseUpPanDiffractionImage(self,event):
        global druged
        self.maindisp.imframe.unbind(sequence="<Motion>")
        self.maindisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragNoPressDiffractionImage)
        self.maindisp.imframe.unbind(sequence="<ButtonRelease>")


    def mouseDownPanDiffractionImage(self,event):
        global druged, lastX, lastY
        druged = 0
        (lastX, lastY) = event.x, event.y
        self.maindisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragPanDiffractionImage)
        self.maindisp.imframe.bind(sequence="<ButtonRelease>", 
                func=self.mouseUpPanDiffractionImage)


    def addUserInputCalibrationDataToObject(self):
        # Try to fill the calibration data.
        calibration = CalibrationData()

        val = self.centerX.ef.getvalue()
        fixed = self.centerX.fixedvar.get()
        if val == "": raise UserInputException("The x center \
calibration parameter is not set.")
        try:
            calibration.setCenterX(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The x center calibration \
parameter has not been set.")

        val = self.centerY.ef.getvalue()
        fixed = self.centerY.fixedvar.get()
        if val == "": raise UserInputException("The y center \
calibration parameter is not set.")

        try:
            calibration.setCenterY(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The y center calibration \
parameter has not been set.")

        val = self.distance.ef.getvalue()
        fixed = self.distance.fixedvar.get()
        if val == "": raise UserInputException("The distance \
calibration parameter is not set.")

        try:
            calibration.setDistance(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The distance calibration \
parameter has not been set.")

        val = self.energyOrWavelength.ef.getvalue()
        fixed = self.energyOrWavelength.fixedvar.get()
        if val == "": raise UserInputException("The energy \
calibration parameter is not set.")

        try:
            if self.eVorLambda.get() == 'Work in eV':
                calibration.setEnergy(float(val),fixed=fixed )
            elif self.eVorLambda.get() == "Work in Lambda":
                calibration.setWavelength(float(val),fixed=fixed )
            else:
                raise UserInputException("The program must run in \
either units of either eV or wavelength.")

        except UserInputException, e:
            raise UserInputException("The energy calibration \
parameter has not been set.")

        val = self.alpha.ef.getvalue()
        fixed = self.alpha.fixedvar.get()
        if val == "": raise UserInputException("The alpha calibration \
parameter is not set.")

        try:
            calibration.setAlpha(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The alpha calibration parameter \
has not been set.")

        val = self.beta.ef.getvalue()
        fixed = self.beta.fixedvar.get()
        if val == "": 
            raise UserInputException("The beta calibration parameter \
is not set.")

        try:
            calibration.setBeta(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The beta calibration parameter \
has not been set.")

        val = self.rotation.ef.getvalue()
        fixed = self.rotation.fixedvar.get()
        if val == "": raise UserInputException("The rotation calibration \
parameter is not set.")

        try:
            calibration.setRotation(float(val),fixed=fixed )
        except UserInputException, e:
            raise UserInputException("The rotation calibration parameter \
has not been set.")

        val = self.pixelLength.ef.getvalue()
        # no pixelLenght fixed values to deal with
        try:
            calibration.setPixelLength(float(val))
        except UserInputException, e:
            raise UserInputException("The pixel length calibration parameter \
has not been set.")

        val = self.pixelHeight.ef.getvalue()
        # no pixelHeight fixed values to deal with
        try:
            calibration.setPixelHeight(float(val))
        except UserInputException, e:
            raise UserInputException("The pixel height calibration parameter \
has not been set.")

        # now put our new calibration data into our list
        if self.calibrationData == []:
            self.calibrationData.append(calibration)
        else:
            # replace the old most current one
            self.calibrationData[-1]=calibration


    def putCalibrationDataIntoInputsNoComplainMissingFields(
            self,calibrationData,addFixedVals=1):
        try:
            self.centerX.ef.setentry(
                    calibrationData.getCenterX()['val'])
            if addFixedVals:
                self.centerX.fixedvar.set(
                        calibrationData.getCenterX()['fixed'])
        except:
            pass

        try:
            self.centerY.ef.setentry(
                    calibrationData.getCenterY()['val'])
            if addFixedVals:
                self.centerY.fixedvar.set(
                        calibrationData.getCenterY()['fixed'])
        except:
            pass

        try:
            self.distance.ef.setentry(calibrationData.getDistance()['val'])
            if addFixedVals:
                self.distance.fixedvar.set(calibrationData.getDistance()['fixed'])
        except:
            pass

        try:
            if self.eVorLambda.get() == 'Work in eV':
                self.energyOrWavelength.ef.setentry(
                        calibrationData.getEnergy()['val'])
                if addFixedVals:
                    self.energyOrWavelength.fixedvar.set(
                            calibrationData.getEnergy()['fixed'])
            elif self.eVorLambda.get() == "Work in Lambda":
                self.energyOrWavelength.ef.setentry(
                        calibrationData.getWavelength()['val'])
                if addFixedVals:
                    self.energyOrWavelength.fixedvar.set(
                            calibrationData.getWavelength()['fixed'])
            else:
                raise UserInputException("The program must run in either \
units of either eV or wavelength.")
        except:
            pass

        try:
            self.alpha.ef.setentry(calibrationData.getAlpha()['val'])
            if addFixedVals:
                self.alpha.fixedvar.set(calibrationData.getAlpha()['fixed'])
        except:
            pass

        try:
            self.beta.ef.setentry(calibrationData.getBeta()['val'])
            if addFixedVals:
                self.beta.fixedvar.set(calibrationData.getBeta()['fixed'])
        except:
            pass

        try:
            self.rotation.ef.setentry(calibrationData.getRotation()['val'])
            if addFixedVals:
                self.rotation.fixedvar.set(
                        calibrationData.getRotation()['fixed'])
        except:
            pass

        # no pixelLenght/pixelHeight fixed values to deal with
        try:
            self.pixelLength.ef.setentry(
                    calibrationData.getPixelLength()['val'])
        except:
            pass

        try:
            self.pixelHeight.ef.setentry(
                    calibrationData.getPixelHeight()['val'])
        except:
            pass


    def putCalibrationDataIntoInputs(self):
        if self.calibrationData == [] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Error: Calibration Data \
is not yet set.")

        self.centerX.ef.setentry(
                self.calibrationData[-1].getCenterX()['val'])
        self.centerX.fixedvar.set(
            self.calibrationData[-1].getCenterX()['fixed'])

        self.centerY.ef.setentry(
                self.calibrationData[-1].getCenterY()['val'])
        self.centerY.fixedvar.set(
            self.calibrationData[-1].getCenterY()['fixed'])

        self.distance.ef.setentry(
                self.calibrationData[-1].getDistance()['val'])
        self.distance.fixedvar.set(
            self.calibrationData[-1].getDistance()['fixed'])

        if self.eVorLambda.get() == 'Work in eV':
            self.energyOrWavelength.ef.setentry(
                    self.calibrationData[-1].getEnergy()['val'])
            self.energyOrWavelength.fixedvar.set(
                self.calibrationData[-1].getEnergy()['fixed'])
        elif self.eVorLambda.get() == "Work in Lambda":
            self.energyOrWavelength.ef.setentry(
                    self.calibrationData[-1].getWavelength()['val'])
            self.energyOrWavelength.fixedvar.set(
                self.calibrationData[-1].getWavelength()['fixed'])
        else:
            raise UserInputException("The program must run in \
either units of either eV or wavelength.")

        self.alpha.ef.setentry(self.calibrationData[-1].getAlpha()['val'])
        self.alpha.fixedvar.set(
            self.calibrationData[-1].getAlpha()['fixed'])

        self.beta.ef.setentry(self.calibrationData[-1].getBeta()['val'])
        self.beta.fixedvar.set(
                self.calibrationData[-1].getBeta()['fixed'])

        self.rotation.ef.setentry(self.calibrationData[-1].getRotation()['val'])
        self.rotation.fixedvar.set(
            self.calibrationData[-1].getRotation()['fixed'])

        self.pixelLength.ef.setentry(
                self.calibrationData[-1].getPixelLength()['val'])
        self.pixelHeight.ef.setentry(
                self.calibrationData[-1].getPixelHeight()['val'])
        # no pixelLenght/pixelHeight fixed values to deal with


    # functions to make the gui do the right thing

    def updatebothNoComplain(self):
        """ Try to update both the main display and the 
            cake display. This function does not 'show'
            Only do the updating if the images are already 
            on the screen. """
        self.maindisp.updateimageNoComplainNoShow()
        self.cakedisp.updateimageNoComplainNoShow()


    def calibrationDataSave(self,filename=''):
        """ Save the calibration data to a file. """
        # get the values from the GUI first
        self.addUserInputCalibrationDataToObject()

        if filename in ['',()]:
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Calibration Data")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension 
            # if you don't write it out explicitly, so make 
            # sure to do so automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        if self.eVorLambda.get() == 'Work in eV':
            self.calibrationData[-1].toFile(filename,
                    energyOrWavelength='Energy')
        elif self.eVorLambda.get() == "Work in Lambda":
            self.calibrationData[-1].toFile(filename,
                    energyOrWavelength='Wavelength')
        else:
            raise UserInputException("The program must \
run in either units of either eV or wavelength.")

        # Explicityly record macro. Only do so if in record macro mode
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save To File','\t %s' % filename)

    def calibrationDataUndo(self):
        if len(self.calibrationData) < 2:
            raise UserInputException("No previous calibration \
data exists to undo to.")
        # remove previous calibration data.
        self.calibrationData.pop()
        self.putCalibrationDataIntoInputs()
        self.maindisp.updateimage()


    def calibrationDataLoad(self,filename=''):
        """ The optional filename argument allows this function \
to be called in a macro mode. """

        if filename == '':
            filename = tkFileDialog.askopenfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    initialdir=self.defaultDir,
                    title="Load Calibration Data")

        if filename in ['',()]: return 

        self.calibrationData.append(CalibrationData(filename))
        
        self.putCalibrationDataIntoInputs()

        # Explicityly record macro. Only do so if in record macro mode
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines('Load From File','\t'+filename)


    def calibrationDataFromHeader(self):
        if self.diffractionData == None:
            raise UserInputException("Cannot get the calibration data \
from the image header until an image is loaded.")
        calibrationData=self.diffractionData.calibrationDataFromHeader()
        self.putCalibrationDataIntoInputsNoComplainMissingFields(
                calibrationData,addFixedVals=0)
        self.updatebothNoComplain()

    
    def addPeaksDiffractionImage(self):
        # if there is nothing to do, the job is done
        if not self.drawPeaks.checkvar.get():
            return 

        # no peak list = Don't do anything
        if self.peakList==None: return 

        # delete old lines
        for id in self.allPeakListIDsDiffractionImage:
            self.maindisp.imframe.delete( id ) 
        self.allPeakListIDsDiffractionImage = []

        # update calibration data first
        self.addUserInputCalibrationDataToObject()

        unZoomWidth = 2.5
        if self.diffractionImageZoomPixels == []:
            # if no zoom, use regular width
            halflength = unZoomWidth
        else:
            # otherwise, scale the size of the xs so that they double in size when 
            # you zoom in to 1/4 of the image
            halflength = unZoomWidth*self.diffractionData.getSize() / \
                    (self.diffractionImageZoomPixels[-1][0]['x'] - \
                    self.diffractionImageZoomPixels[-1][1]['x'])

        for x,y,qReal,qFit,chi,width in self.peakList.getMaskedPeakList(self.maskedPixelInfo):
            canvasX,canvasY = self.getCanvasDiffractionImageCoordinates(x,y)

            # add in new lines if they would be visible
            if (canvasX >= 0 and canvasX < self.diffractionImageSize \
                    and canvasY >= 0 and canvasY < self.diffractionImageSize):
                self.allPeakListIDsDiffractionImage.append( self.maindisp.imframe.create_line(
                        canvasX-halflength,canvasY-halflength,canvasX+halflength,
                        canvasY+halflength,fill=self.peakLinesColor.get(),width="1"))
                self.allPeakListIDsDiffractionImage.append( self.maindisp.imframe.create_line(
                        canvasX+halflength,canvasY-halflength,canvasX-halflength,
                        canvasY+halflength,fill=self.peakLinesColor.get(),width="1"))


    def addConstantQLinesDiffractionImage(self):
        # if there is nothing to do, the job is done
        if not self.drawQ.checkvar.get() and not self.drawdQ.checkvar.get():
            return 

        self.addUserInputCalibrationDataToObject()

        if self.QData == None:
            raise UserInputException("Cannot add constant Q lines to the image \
until a QData file is set.")
        if self.calibrationData == [] or not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot add constant Q lines to the image \
until the calibration parameters are set.")
        if self.diffractionData == None:
            raise UserInputException("Cannot add constant Q lines to the image \
until a diffraction image is set.")

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in either Q or \
2theta mode.")
        
        # remove old Q lines
        for id in self.allQLineIDsDiffractionImage:
            self.maindisp.imframe.delete(id)
        self.allQLineIDsDiffractionImage = []

        for Q,dQ in self.QData.getAllQPairs():

            if self.drawQ.checkvar.get():
                list = []
                for chi in General.frange(0,360,3):
                    # get x,y values
                    x,y=Transform.getXY(self.calibrationData[-1],Q,chi)

                    xCanvas,yCanvas = self.getCanvasDiffractionImageCoordinates(x,y)

                    list.append(xCanvas)
                    list.append(yCanvas)
                # draw the current Q line
                self.allQLineIDsDiffractionImage.append(
                        self.maindisp.imframe.create_polygon(
                        list,outline=self.qLinesColor.get(),fill="" ))

            if self.drawdQ.checkvar.get():
                list = []
                for chi in General.frange(0,360,3):
                    # get x,y values
                    x,y=Transform.getXY(self.calibrationData[-1],Q-dQ,chi)

                    xCanvas,yCanvas = self.getCanvasDiffractionImageCoordinates(x,y)

                    list.append(xCanvas)
                    list.append(yCanvas)
                # draw the current dQ line
                self.allQLineIDsDiffractionImage.append(
                        self.maindisp.imframe.create_polygon(
                        list,outline=self.dQLinesColor.get(),fill="" ))

                list = []
                for chi in General.frange(0,360,3):
                    # get x,y values
                    x,y=Transform.getXY(self.calibrationData[-1],Q+dQ,chi)
                   
                    xCanvas,yCanvas = self.getCanvasDiffractionImageCoordinates(x,y)

                    list.append(xCanvas)
                    list.append(yCanvas)

                # draw the current dQ line
                self.allQLineIDsDiffractionImage.append(
                        self.maindisp.imframe.create_polygon(
                        list,outline=self.dQLinesColor.get(),fill="" ))


    def doZoomDiffractionImage(self,zoomLevel):
        """ Set the new zoom level on the stack. Then it draws the image. """
        self.diffractionImageZoomPixels.append(zoomLevel)
        self.maindisp.updateimage()


    def undoZoomDiffractionImage(self,event=None):
        """ Take the current zoom level off the stack, so that the 
            new current zoom level is the old one. Then it draws 
            the image. Only do so if there is still something on 
            the stack. """

        # reset cordinates
        if self.diffractionImageZoomPixels != []:
            self.diffractionImageZoomPixels.pop()
        self.maindisp.updateimage()

    def addMaskedPixelInfoToObject(self,operationString):
        self.maskedPixelInfo.doGreaterThanMask = \
                self.doGreaterThanMask.checkvar.get()
        self.maskedPixelInfo.greaterThanMaskColor = \
                self.greaterThanMaskColor.get()

        if self.maskedPixelInfo.doGreaterThanMask:
            try:
                self.maskedPixelInfo.greaterThanMask = \
                        float(self.greaterThanMask.getvalue())
            except:
                raise UserInputException("Cannot %s until the \
the greater than mask gets set." % operationString)
        else:
            # Can be anything since it won't be used
            self.maskedPixelInfo.greaterThanMask = -1 

        self.maskedPixelInfo.doLessThanMask = self.doLessThanMask.checkvar.get()
        self.maskedPixelInfo.lessThanMaskColor = self.lessThanMaskColor.get()
        if self.maskedPixelInfo.doLessThanMask:
            try:
                self.maskedPixelInfo.lessThanMask = float(self.lessThanMask.getvalue())
            except:
                raise UserInputException("Cannot %s until the \
less than mask gets set." % operationString)
        else:
            # Can be anything since it won't be used
            self.maskedPixelInfo.lessThanMask = -1 

        # get in the polygon info
        self.maskedPixelInfo.doPolygonMask = self.doPolygonMask.checkvar.get()
        self.maskedPixelInfo.polygonMaskColor = self.polygonMaskColor.get()

        if self.maskedPixelInfo.doGreaterThanMask and \
                self.maskedPixelInfo.greaterThanMask < 0:
            raise UserInputException("Cannot %s because the greater \
than mask must be at least 0." % operationString)

        if self.maskedPixelInfo.doLessThanMask and \
                self.maskedPixelInfo.lessThanMask < 0:
            raise UserInputException("Cannot %s because the less \
than mask must be at least 0." % operationString)

        if self.maskedPixelInfo.doLessThanMask and \
                self.maskedPixelInfo.doGreaterThanMask and \
                self.maskedPixelInfo.greaterThanMask < self.maskedPixelInfo.lessThanMask:
            raise UserInputException("Cannot %s because the greater \
than mask must be at least as large as the less than \
mask." % operationString)

    def drawDiffractionImage(self): 
        if self.diffractionData == None:
            raise UserInputException("Cannot draw the image until a \
diffraction image is set.")

        setstatus(self.status,"Drawing...")
        
        try:
            # update calibrationData first. Note that if 
            # the calibration data is not in the inpus, 
            # that is not necessarily a problem. So we should 
            # just try to addd it in and do nothing if it fails.
            # The reason to do so here is because if the image 
            # gets updated, we want any changes to the 
            # calibrationData to be apperent when you
            # move your curser around the image.
            self.addUserInputCalibrationDataToObject()
        except:
            pass

        try:
            lower = float(self.maindisp.intenvarlo.get() )
            upper = float(self.maindisp.intenvarhi.get() )
        except: 
            raise UserInputException("Image Scaling values are not \
valid numbers.")

        if upper <= lower:
            raise UserInputException("Image Scaling values are not valid. \
The upper value must be greater then the lower value.")

        if lower < 0 or lower > 1:
            raise UserInputException("Image Scaling values are not valid. \
The lower bound must be between 0 and 1.")

        if upper < 0 or upper > 1:
            raise UserInputException("Image Scaling values are not valid. \
The upper bound must be between 0 and 1.")

        #for some reason, this is a list
        colorMapName = self.maindisp.colmap.getvalue()[0] 

        logScale = self.logVarDiffraction.get()
        invert = self.invertVarDiffraction.get()

        self.addMaskedPixelInfoToObject(
                operationString="draw the diffraction image")

        if self.diffractionImageZoomPixels==[]:
            self.maindisp.image = self.diffractionData.getDiffractionImage(
                    height=self.diffractionImageSize, 
                    width=self.diffractionImageSize,
                    lowerBound=lower,upperBound=upper,
                    logScale = logScale,invert = invert,
                    colorMaps=self.colorMaps,colorMapName=colorMapName, 
                    maskedPixelInfo = self.maskedPixelInfo)
        else:
            self.maindisp.image = self.diffractionData.getDiffractionImage(
                    height=self.diffractionImageSize, 
                    width=self.diffractionImageSize,
                    pixel1X=self.diffractionImageZoomPixels[-1][0]['x'],
                    pixel1Y=self.diffractionImageZoomPixels[-1][0]['y'],
                    pixel2X=self.diffractionImageZoomPixels[-1][1]['x'],
                    pixel2Y=self.diffractionImageZoomPixels[-1][1]['y'],
                    lowerBound=lower,upperBound=upper,
                    logScale =logScale,invert = invert,
                    colorMaps=self.colorMaps,colorMapName=colorMapName, 
                    maskedPixelInfo = self.maskedPixelInfo)
 
        # keep a copy for reference (weird Tk bug)
        self.maindisp.imageTk = ImageTk.PhotoImage(self.maindisp.image) 
        
        if self.diffractionImageID != None:
            self.maindisp.imframe.delete(self.diffractionImageID)

        self.diffractionImageID = \
                self.maindisp.imframe.create_image(
                0,0,image=self.maindisp.imageTk,anchor=NW)

        if self.diffractionImageZoomPixels==[]:
            self.maindisp.bottomAxis.config(
                    lowestValue=0,
                    highestValue=self.diffractionData.getSize())

            self.maindisp.rightAxis.config(
                    lowestValue=0,
                    highestValue=self.diffractionData.getSize())
        else:
            self.maindisp.bottomAxis.config(
                    lowestValue=self.diffractionImageZoomPixels[-1][0]['x'],
                    highestValue=self.diffractionImageZoomPixels[-1][1]['x'])

            self.maindisp.rightAxis.config(
                    lowestValue=self.diffractionImageZoomPixels[-1][0]['y'],
                    highestValue=self.diffractionImageZoomPixels[-1][1]['y'])

        self.addConstantQLinesDiffractionImage()
        self.addPeaksDiffractionImage()

        if self.currentPolygonID != None:
            # possibly redraw the zoom polygon because the diffraction image
            # might end up covering it up
            self.maindisp.imframe.delete(self.currentPolygonID)
            self.currentPolygonID = self.maindisp.imframe.create_polygon(
                    self.convertPolygonFromImageToCanvasCoordinates(self.currentPolygon),
                    outline='red',fill='')


        setstatus(self.status,"Ready")


    def saveDiffractionImage(self,filename=''):
        if self.diffractionData == None:
            raise UserInputException("Cannot save the diffraction image \
until a diffraction image is loaded.")

        try:
            lower = float(self.maindisp.intenvarlo.get() )
            upper = float(self.maindisp.intenvarhi.get() )
        except: 
            raise UserInputException("Image Scaling values are not \
valid numbers.")

        if upper <= lower:
            raise UserInputException("Image Scaling values are not \
valid. The upper value must be greater then the lower value.")

        if lower < 0 or lower > 1:
            raise UserInputException("Image Scaling values are not \
valid. The lower bound must be between 0 and 1.")

        if upper < 0 or upper > 1:
            raise UserInputException("Image Scaling values are not \
valid. The upper bound must be between 0 and 1.")

        if self.drawQ.checkvar.get() or self.drawdQ.checkvar.get():
            if self.QData == None:
                raise UserInputException("Cannot save image with \
constant Q lines until a q data file is set.")

            self.addUserInputCalibrationDataToObject()

            if self.calibrationData == [] or \
                    not self.calibrationData[-1].allSet():
                raise UserInputException("Cannot add constant Q lines \
to the image until the calibration parameters are set.")

        theCalibrationDataToGive = None
        if self.calibrationData != []: 
            theCalibrationDataToGive = self.calibrationData[-1]

        thePixel1XToGive=None
        thePixel1YToGive=None
        thePixel2XToGive=None
        thePixel2YToGive=None

        if self.diffractionImageZoomPixels != []:
                    thePixel1XToGive=self.diffractionImageZoomPixels[-1][0]['x']
                    thePixel1YToGive=self.diffractionImageZoomPixels[-1][0]['y']
                    thePixel2XToGive=self.diffractionImageZoomPixels[-1][1]['x']
                    thePixel2YToGive=self.diffractionImageZoomPixels[-1][1]['y']

        if filename in ['',()]:
            defaultextension = ".jpg"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('ESRF Data Format','*.edf'),
                        ('JPEG','*.jpg'),('GIF','*.gif'),
                        ('EPS','*.eps'),('PDF','*.pdf'),('BMP','*.bmp'),('PNG','*.png'),
                        ('TIFF','*.tiff'), ('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Diffraction Image")

            if filename in ['',()]: 
                return 
                
            # on the mac, it won't give a default extension 
            # if you don't write it out explicitly, so do so 
            #automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension
        
        setstatus(self.status,'Saving...')

        #for some reason, this is a list
        colorMapName = self.maindisp.colmap.getvalue()[0] 

        logScale = self.logVarDiffraction.get()
        invert = self.invertVarDiffraction.get()

        self.addMaskedPixelInfoToObject(
                operationString="save the diffraction image")

        self.diffractionData.saveDiffractionImage(
                filename = filename,
                pixel1X = thePixel1XToGive,
                pixel1Y = thePixel1YToGive,
                pixel2X = thePixel2XToGive,
                pixel2Y = thePixel2YToGive,
                lowerBound = lower, upperBound=upper,
                logScale = logScale,
                colorMaps=self.colorMaps,colorMapName=colorMapName,
                invert=invert,
                drawQLines = self.drawQ.checkvar.get(),
                drawdQLines = self.drawdQ.checkvar.get(),
                QData = self.QData,
                calibrationData = theCalibrationDataToGive,
                drawPeaks = self.drawPeaks.checkvar.get(),
                peakList = self.peakList,
                qLinesColor = self.qLinesColor.get(),
                dQLinesColor = self.dQLinesColor.get(),
                peakLinesColor = self.peakLinesColor.get(),
                maskedPixelInfo = self.maskedPixelInfo)

        setstatus(self.status,'Done') 

        # Explicityly record macro. Only do so if in record macro mode
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Diffraction Image','\t'+filename)


    def doFit(self):
        setstatus(self.status,"Fitting...")

        self.addUserInputCalibrationDataToObject()

        if self.diffractionData == None:
            raise UserInputException("Cannot do fitting until a \
diffraction image is entered.")

        if self.calibrationData == [] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot do fitting until the \
calibration parameters are set.")

        if self.QData == None:
            raise UserInputException("Cannot do fitting until the \
Q data is set.")

        # get the number of chi values from the screen input.
        try:
            numberOfChi = int(self.numberOfChiInput.getvalue())
        except:
            raise UserInputException("The number of chi slices to \
use has not been set.")

        if numberOfChi < 2:
            raise UserInputException("The number of chi slices \
must be at least 2.")
        
        fit = None

        try:
            stddev = float(self.stddev.getvalue())
        except:
            raise UserInputException("The standard deviation has \
not been set.")

        if stddev < 0:
            raise UserInputException("The standard deviation must \
be greater then 0.")

        if self.calibrationData[-1].allParametersFixed():
            raise UserInputException("Cannot do the fit because none \
of the parameters are allowed to vary.")

        # numberOfChi is the new value, self.numberOfChiStore 
        # was stored from last time. Only use old peak list if 
        # these numbers agree. (IE, if they change the number of 
        # chi values to use, calculate a new peak list. Also, if 
        # you change the stddev input, also calculate a new peak list.
        if self.useOldPeakList.get()==1 and \
                self.peakList != None and \
                numberOfChi == self.numberOfChiStore and \
                stddev == self.stddevStore:
            fit,self.peakList = self.diffractionData.fit(
                    self.calibrationData[-1],
                    self.QData,
                    self.maskedPixelInfo,
                    peakList=self.peakList)
        else:
            fit,self.peakList = self.diffractionData.fit(
                    self.calibrationData[-1],
                    self.QData,
                    self.maskedPixelInfo,
                    numberOfChi=numberOfChi,
                    stddev=stddev)

            self.numberOfChiStore = numberOfChi
            self.stddevStore = stddev

        self.calibrationData.append(fit)
        self.putCalibrationDataIntoInputs()

        setstatus(self.status,'Ready')
        self.updatebothNoComplain()
 
    def saveLastFit(self,filename=''):
        
        if self.diffractionData == None or \
                not self.diffractionData.canSaveLastFit():
            raise UserInputException("No previous fit to save")
             
        if filename in ['',()]:
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Last Fit")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension if you 
            # don't write it out explicitly, so do so automatically 
            # otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        self.diffractionData.lastFitToFile(filename)
        
        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Last Fit','\t'+filename)


    def savePeakList(self,filename=''):

        self.addUserInputCalibrationDataToObject()

        if self.diffractionData == None:
            raise UserInputException("Cannot save the peak list \
until a diffraction image is entered.")
        if self.calibrationData == [] or not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot save the peak list \
until the calibration parameters are set.")
        if self.QData == None:
            raise UserInputException("Cannot save the peak list \
until the Q data is set.")
        
        if filename in ['',()]:
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Peak List")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension if you 
            # don't write it out explicitly, so do so automatically 
            # otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        setstatus(self.status,'Saving peak list')

        # get the number of chi values from the screen input.
        try:
            numberOfChi = int(self.numberOfChiInput.getvalue())
        except:
            raise UserInputException("The number of chi slices to \
use has not been set.")

        if numberOfChi < 2:
            raise UserInputException("The number of chi slices must \
be at least 2.")
       
        try:
            stddev = float(self.stddev.getvalue())
        except:
            raise UserInputException("The standard deviation has \
not been set.")

        if stddev < 0:
            raise UserInputException("The standard deviation must \
be greater then 0.")

        # also, store the peakList for later
        self.peakList = self.diffractionData.savePeakListToFile(
                filename,self.calibrationData[-1],self.QData,
                numberOfChi,self.maskedPixelInfo,stddev=stddev)


        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Make/Save Peak List','\t'+filename)

        setstatus(self.status,'Ready')
        self.updatebothNoComplain()

    def getQChiCakeImageCoordinates(self,x,y):
        """ Returns the q,chi values corresponding to 
            canvas x,y values. """

        if self.cakeRange == []:
                raise UserInputException("Cannot convert canvas \
x,y values to image q,chi values until the image has been caked")

        qOrTwoThetaLowerZoom = min(
                self.cakeRange[-1]['qOrTwoThetaLower'],
                self.cakeRange[-1]['qOrTwoThetaUpper'])
        qOrTwoThetaUpperZoom = max(
                self.cakeRange[-1]['qOrTwoThetaLower'],
                self.cakeRange[-1]['qOrTwoThetaUpper'])

        chiLowerZoom = min(
                self.cakeRange[-1]['chiLower'],
                self.cakeRange[-1]['chiUpper'])
        chiUpperZoom = max(
                self.cakeRange[-1]['chiLower'],
                self.cakeRange[-1]['chiUpper'])

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")
        
        # calculate the real q image
        qOrTwoTheta = qOrTwoThetaLowerZoom + \
                (x*1.0/(self.cakeImageWidth-1))* \
                (qOrTwoThetaUpperZoom-qOrTwoThetaLowerZoom)

        if type == "Q":
            q = qOrTwoTheta
        elif type == "2theta":
            q = Transform.convertTwoThetaToQ(qOrTwoTheta,self.calibrationData[-1])

        chi = chiLowerZoom + (y*1.0/(self.cakeImageHeight-1))*(chiUpperZoom-chiLowerZoom)

        return q,chi


    def getCanvasCakeImageCoordinates(self,q,chi):
        """ Returns the canvas values x,y corresponding to 
            q,chi values. """

        if self.cakeRange == []:
            raise UserInputException("Cannot convert canvas x,y values \
to image q,chi values until the image has been caked")

        qOrTwoThetaLowerZoom = min(
                self.cakeRange[-1]['qOrTwoThetaLower'],
                self.cakeRange[-1]['qOrTwoThetaUpper'])
        qOrTwoThetaUpperZoom = max(
                self.cakeRange[-1]['qOrTwoThetaLower'],
                self.cakeRange[-1]['qOrTwoThetaUpper'])

        chiLowerZoom = min(
                self.cakeRange[-1]['chiLower'],
                self.cakeRange[-1]['chiUpper'])
        chiUpperZoom = max(
                self.cakeRange[-1]['chiLower'],
                self.cakeRange[-1]['chiUpper'])

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")
        
        if type == "Q":
            x = (q-qOrTwoThetaLowerZoom)/ \
                    (qOrTwoThetaUpperZoom-qOrTwoThetaLowerZoom)* \
                    (self.cakeImageWidth-1)
        elif type == "2theta":
            twoTheta = Transform.convertQToTwoTheta(
                    q,self.calibrationData[-1])
            x = (twoTheta-qOrTwoThetaLowerZoom)/ \
                    (qOrTwoThetaUpperZoom-qOrTwoThetaLowerZoom)* \
                    (self.cakeImageWidth-1)

        y = (chi-chiLowerZoom)/(chiUpperZoom-chiLowerZoom)* \
                (self.cakeImageHeight-1)

        return x,y


    def doCake(self):
        setstatus(self.status,'Caking...')

        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.diffractionData==None:
            raise UserInputException("Cannot cake until an \
image is loaded.")
        if self.calibrationData==[] or not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot cake until the \
calibration parameters are set.")
       
        try:
            lower = float(self.cakedisp.intenvarlo.get() )
            upper = float(self.cakedisp.intenvarhi.get() )
        except: 
            raise UserInputException("Image Scaling values are \
not valid numbers.")

        try:
            numQOrTwoTheta = int(self.numQOrTwoThetaCake.getvalue())
        except:
            raise UserInputException("The number of Q (or 2theta) \
values to use when caking has not been set.")

        try:
            qOrTwoThetaLower = float(self.qOrTwoThetaLowerCake.getvalue())
        except:
            raise UserInputException("The lower Q (or 2theta) value \
to use when caking has not been set.")

        try:
            qOrTwoThetaUpper = float(self.qOrTwoThetaUpperCake.getvalue())
        except:
            raise UserInputException("The upper Q (or 2theta) \
value to use when caking has not been set.")

        try:
            numChi = int(self.numChiCake.getvalue())
        except:
            raise UserInputException("The number of chi values \
to use when caking has not been set.")

        try:
            chiLower = float(self.chiLowerCake.getvalue())
        except:
            raise UserInputException("The lower chi value to \
use when caking has not been set.")

        try:
            chiUpper = float(self.chiUpperCake.getvalue())
        except:
            raise UserInputException("The upper chi value \
to use when caking has not been set.")

        doPolarizationCorrection = self.doPolarizationCorrectionCake.get()
        if doPolarizationCorrection:
            try:
                P = float(self.PCake.getvalue())
            except:
                raise UserInputException("The P cake value has not \
been set.")
        else:
            P = 0 # P can be anything since it won't be used.

        self.addMaskedPixelInfoToObject(
                operationString="cake the diffraction data")

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
            title ="Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
            title = u"2\u03D1"
        else:
            raise UserInputException("The program must work \
in either Q or 2theta mode.")

        if chiLower >= chiUpper:
            raise UserInputException("The lower chi value \
must be less then the upper chi value.")

        if (chiUpper - chiLower) > 360:
            raise UserInputException("The chi values must \
have a range no larger then 360 degrees.")

        if type == "Q":

            if qOrTwoThetaLower >= qOrTwoThetaUpper:
                raise UserInputException("The lower Q value \
must be less then the upper Q value.")

            if qOrTwoThetaLower < 0: 
                raise UserInputException("The lower Q value \
must be larger then 0.")

            if qOrTwoThetaUpper > Transform.getMaxQ(self.calibrationData[-1]):
                raise UserInputException("The upper Q value \
must be less then the largest possible Q value.")

        elif type == "2theta":

            if qOrTwoThetaLower >= qOrTwoThetaUpper:
                raise UserInputException("The lower 2theta value \
must be less then the upper 2theta value.")

            if qOrTwoThetaLower < 0: 
                raise UserInputException("The lower 2theta value \
must be larger then 0.")

            if qOrTwoThetaUpper > Transform.getMaxTwoTheta():
                raise UserInputException("The upper 2theta value \
must be less then the largest possible 2theta value.")

        currentRange = {'qOrTwoThetaLower':qOrTwoThetaLower,
                'qOrTwoThetaUpper':qOrTwoThetaUpper,
                'chiLower':chiLower,'chiUpper':chiUpper}

        # store into zoom stack if the zoom range is new
        if self.cakeRange == [] or currentRange != self.cakeRange[-1]:
            self.cakeRange.append(currentRange)

        colorMapName = self.cakedisp.colmap.getvalue()[0]
        logScale = self.logVarCake.get()
        invert = self.invertVarCake.get()

        self.imageCake = self.diffractionData.getCakeImage(
                self.calibrationData[-1],
                qOrTwoThetaLower = self.cakeRange[-1]['qOrTwoThetaLower'],
                qOrTwoThetaUpper = self.cakeRange[-1]['qOrTwoThetaUpper'], 
                numQOrTwoTheta = numQOrTwoTheta,
                chiLower = self.cakeRange[-1]['chiLower'],
                chiUpper = self.cakeRange[-1]['chiUpper'], 
                numChi = numChi,
                doPolarizationCorrection = doPolarizationCorrection,P=P,
                maskedPixelInfo = self.maskedPixelInfo,
                width=self.cakeImageWidth,height=self.cakeImageHeight,
                colorMaps=self.colorMaps,colorMapName=colorMapName,
                lowerBound = lower, upperBound = upper,
                logScale = logScale, invert = invert,
                type = type)
   
        # keep a copy for reference (weird Tk bug)
        self.imageCakeTk = ImageTk.PhotoImage(self.imageCake)

        if self.cakeImageID == None:
            self.cakeImageID = self.cakedisp.imframe.create_image(
                    1,1,image=self.imageCakeTk,anchor=NW)

            # only add bindings to the canvas if we are 
            # drawing the image for the first time.
            self.cakedisp.imframe.bind(sequence="<ButtonPress>",
                    func=self.mouseDownZoomCakeImage)
            self.cakedisp.imframe.bind(sequence="<Motion>",
                    func=self.mouseDragNoPressCakeImage)
            self.cakedisp.imframe.bind(sequence="<Shift-ButtonPress>", 
                    func=self.mouseDownPanCakeImage)

            self.cakedisp.imframe.bind(sequence="<Leave>",
                    func=self.mouseLeaveCakeImage)
            self.cakedisp.graphframe.bind("<Configure>",
                    func=self.resizeCakeImage) 
        else:
            self.cakedisp.imframe.delete(self.cakeImageID)
            self.cakeImageID = self.cakedisp.imframe.create_image(
                    1,1,image=self.imageCakeTk,anchor=NW)

        # (possibly) add some peaks to the image.
        self.addPeaksCakeImage()
        self.addConstantQLinesCakeImage()

        self.cakedisp.bottomAxis.config(
                lowestValue=self.cakeRange[-1]['qOrTwoThetaLower'],
                highestValue=self.cakeRange[-1]['qOrTwoThetaUpper'],
                title=title
        )

        self.cakedisp.rightAxis.config(
                lowestValue=self.cakeRange[-1]['chiLower'],
                highestValue=self.cakeRange[-1]['chiUpper'],
                title=u"\u03A7"
        )

        setstatus(self.status,'Ready...')


    def saveCakeData(self,filename=''):

        if filename  in ['',()]: 
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('data','*.dat')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Caked Data")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension 
            # if you don't write it out explicitly, so do 
            # so automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        #redraw the image and make sure the user input is good.
        self.doCake() 

        numQOrTwoTheta = int(self.numQOrTwoThetaCake.getvalue())
        qOrTwoThetaLower = float(self.qOrTwoThetaLowerCake.getvalue())
        qOrTwoThetaUpper = float(self.qOrTwoThetaUpperCake.getvalue())
        numChi = int(self.numChiCake.getvalue())
        chiLower = float(self.chiLowerCake.getvalue())
        chiUpper = float(self.chiUpperCake.getvalue())

        doPolarizationCorrection = self.doPolarizationCorrectionCake.get()
        if doPolarizationCorrection:
            P = float(self.PCake.getvalue())
        else:
            # it dosen't matter what p is so assign it arbitrarily 
            P = 0

        self.addMaskedPixelInfoToObject(operationString="save cake data")

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in either \
Q or 2theta mode.")
        
        setstatus(self.status,'Saving...')

        self.diffractionData.saveCakeData(
                filename = filename,
                calibrationData = self.calibrationData[-1],
                qOrTwoThetaLower = self.cakeRange[-1]['qOrTwoThetaLower'],
                qOrTwoThetaUpper = self.cakeRange[-1]['qOrTwoThetaUpper'], 
                numQOrTwoTheta = numQOrTwoTheta,
                chiLower = self.cakeRange[-1]['chiLower'],
                chiUpper = self.cakeRange[-1]['chiUpper'], 
                numChi = numChi,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                maskedPixelInfo = self.maskedPixelInfo,
                type=type)
 
        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Caked Data','\t %s' % filename)

        setstatus(self.status,'Ready')

                    
    def saveCakeImage(self,filename=''):
        if filename in ['',()]: 
            defaultextension = ".jpg"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('JPEG','*.jpg'),('GIF','*.gif'),
                        ('EPS','*.eps'),('PDF','*.pdf'),
                        ('BMP','*.bmp'),('PNG','*.png'),
                        ('TIFF','*.tiff'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Caked Image")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension 
            # if you don't write it out explicitly, so do 
            # so automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        #redraw the image and make sure the user input is good.
        self.doCake() 

        lower = float(self.cakedisp.intenvarlo.get() )
        upper = float(self.cakedisp.intenvarhi.get() )

        numQOrTwoTheta = int(self.numQOrTwoThetaCake.getvalue())
        qOrTwoThetaLower = float(self.qOrTwoThetaLowerCake.getvalue())
        qOrTwoThetaUpper = float(self.qOrTwoThetaUpperCake.getvalue())
        numChi = int(self.numChiCake.getvalue())
        chiLower = float(self.chiLowerCake.getvalue())
        chiUpper = float(self.chiUpperCake.getvalue())

        doPolarizationCorrection = self.doPolarizationCorrectionCake.get()
        if doPolarizationCorrection:
            P = float(self.PCake.getvalue())
        else:
            # it dosen't matter what p is so assign it arbitrarily 
            P = 0
            
        self.addMaskedPixelInfoToObject(operationString="save cake image")

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")
        
        setstatus(self.status,'Saving')

        colorMapName = self.cakedisp.colmap.getvalue()[0]

        logScale = self.logVarCake.get()
        invert = self.invertVarCake.get()

        self.diffractionData.saveCakeImage(
                filename = filename,
                calibrationData = self.calibrationData[-1],
                qOrTwoThetaLower = self.cakeRange[-1]['qOrTwoThetaLower'],
                qOrTwoThetaUpper = self.cakeRange[-1]['qOrTwoThetaUpper'], 
                numQOrTwoTheta = numQOrTwoTheta,
                doPolarizationCorrection = doPolarizationCorrection,
                maskedPixelInfo = self.maskedPixelInfo,
                P = P,
                chiLower = self.cakeRange[-1]['chiLower'],
                chiUpper = self.cakeRange[-1]['chiUpper'], 
                numChi = numChi,
                colorMaps=self.colorMaps,
                colorMapName=colorMapName,
                lowerBound = lower, 
                upperBound = upper,
                logScale = logScale,
                invert = invert,
                drawQOrTwoThetaLines = self.drawQ.checkvar.get(),
                drawdQOrTwoThetaLines = self.drawdQ.checkvar.get(),
                QData = self.QData,
                drawPeaks = self.drawPeaks.checkvar.get(),
                peakList = self.peakList,
                qOrTwoThetaLinesColor = self.qLinesColor.get(),
                dQOrTwoThetaLinesColor = self.dQLinesColor.get(),
                peakLinesColor = self.peakLinesColor.get(),
                type=type)

        setstatus(self.status,'Ready')

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Caked Image','\t'+filename)


    def resizeCakeImage(self,event):
        """ When the frame holding the graphs gets 
            resized because the image canvas gets 
            streched by the user, redraw the cake image
            and the axis to fill the newly avalible space. """
        
        # resize canvas properly
        if event.width <= self.axisSize or \
                event.height <= self.axisSize:
            return

        self.cakeImageWidth=event.width-self.axisSize
        self.cakeImageHeight=event.height-self.axisSize

        self.cakedisp.imframe.config(height=self.cakeImageHeight,
                width=self.cakeImageWidth)

        self.cakedisp.bottomAxis.config(width=self.cakeImageWidth,
                height=self.axisSize)

        self.cakedisp.rightAxis.config(width=self.axisSize,
                height=self.cakeImageHeight)

        # redraw the image
        self.cakedisp.updateimageNoComplain()


    def selectDiffractionFiles(self):
        filenames = tkFileDialog.askopenfilenames(
            filetypes=[ 
                ("All Files", "*"), 
                ('Mar PCK Format','*.mar2300 *.mar3450'), 
                ('Mar CCD Format','*.mccd'), 
                ('ESRF Data Format','*.edf'),
                ('TIFF','*.tif *.tiff'), 
                ('Bruker','*.bruker') ], 
                initialdir=self.defaultDir,
                title="Load Diffraction Image")

        if filenames in ['',()]: return 

        # put the filename(s) into the input 
        self.fileentry.setvalue(General.joinPaths(filenames))

        # load in the data
        self.loadDiffractionFile()


    def setExtension(self, result):
        """ When the user specifys the extension of a particular 
            image, this is where his choice gets recorded. """
        if result == "mar 3450":
            self.extension = "mar3450"
        if result == "mar 2300":
            self.extension = "mar2300"
        if result == "Mar CCD Format":
            self.extension = "mccd"
        if result == "ESRF Data Format":
            self.extension = "edf"
        if result == "TIFF":
            self.extension = "tiff"
        if result == "Bruker":
            self.extension = "bruker"
        if result == "Cancel":
            self.extension = "return"
        self.dialog.deactivate()

    def removePolygons(self):
        setstatus(self.status,"Removing...")
        self.maskedPixelInfo.removePolygons()
        setstatus(self.status,"Ready")

        self.updatebothNoComplain()


    def loadPolygonsFromFile(self,filename=''):
        if filename == '':
            filename = tkFileDialog.askopenfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    initialdir=self.defaultDir,
                    title="Load Polygon File")

        if filename == '': return

        setstatus(self.status,"Loading...")
        self.maskedPixelInfo.loadPolygonsFromFile(filename)
        setstatus(self.status,"Ready")
        
        self.updatebothNoComplain()

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Load Mask','\t %s' % filename)

    
    def savePolygonsToFile(self,filename=''):

        if self.maskedPixelInfo.numPolygons() < 1: 
            raise UserInputException("Cannot save polygons to a \
file until there are polygons to save.")

        if filename in ['',()]: 
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Load Polygon File")

            if filename in ['',()]: return

            # on the mac, it won't give a default extension if you 
            # don't write it out explicitly, so make sure to do 
            # so automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

        setstatus(self.status,"Saving...")
        self.maskedPixelInfo.savePolygonsToFile(filename)
        setstatus(self.status,"Ready")

        self.updatebothNoComplain()

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Mask','\t %s' % filename)


    def toggleAddRemovePolygonMaskBindings(self,whichButton,onOff):
        if whichButton == 'Add Polygon':
            if onOff == 1:

                if self.diffractionData == None:
                    # if no diffraction image, unstick buttons and 
                    # raise an error
                    self.addRemovePolygonRadioSelect.setvalue( [''])
                    raise UserInputException("Cannot add a polygon mask \
until a diffraction image is set.")

                # Begin adding polygons, 
                # also, use this to deselect the Remove Polygon Option if
                # it is enabled
                self.addRemovePolygonRadioSelect.setvalue( ['Add Polygon'])
                # also, check the do polygon mask button b/c you won't see
                # what you have done otherwise
                self.doPolygonMask.checkvar.set(1)

                self.maindisp.imframe.unbind(sequence="<Shift-ButtonPress>")
                self.maindisp.imframe.bind(sequence="<Motion>", 
                        func=self.mouseDragNoPressDiffractionImage)
                self.maindisp.imframe.bind(sequence="<ButtonPress>", 
                        func=self.mouseButtonPressAddPolygonDiffractionImage)
                self.maindisp.imframe.bind(sequence="<Leave>", 
                        func=self.mouseLeaveDiffractionImage)
                self.maindisp.graphframe.bind("<Configure>",
                        func=self.resizeDiffractionImage) 

                # redraw the images - note that the cake display 
                # need not be ready to display
                self.maindisp.updateimage()
                self.cakedisp.updateimageNoComplainNoShow()

            elif onOff == 0:
                # End adding Polygons
                # if the user has not finished drawing a polygon, 
                # then just delete the half finished one.

                # remove the drawn polygon (if it had been drawn):
                if self.currentPolygonID != None:
                    self.maindisp.imframe.delete(self.currentPolygonID)
                    self.currentPolygonID == None
                self.currentPolygon = None
                self.currentPolygonID = None
            
                # change bindings back
                self.addZoomAndPanBindingsDiffractionImage()

        elif whichButton == 'Remove Polygon':

            if onOff == 1:
                # try removing a polygon

                if self.diffractionData == None:
                    # if no diffraction image, unstick buttons and 
                    # raise an error
                    self.addRemovePolygonRadioSelect.setvalue( [''])
                    raise UserInputException("Cannot remove a polygon \
mask until a diffraction image is set.")

                if self.maskedPixelInfo.numPolygons() < 1:
                    # if there are no polygons, then make this
                    # button just unstick and do nothing
                    self.addRemovePolygonRadioSelect.setvalue([])
                    return

                # Begin removing polygons also, use this to deselect the 
                # Add Polygon Option if it is enabled
                self.addRemovePolygonRadioSelect.setvalue( ['Remove Polygon'])

                # also, check the do polygon mask button b/c you can't
                # delete what you can't see
                self.doPolygonMask.checkvar.set(1)

                self.maindisp.imframe.unbind(sequence="<Shift-ButtonPress>")
                self.maindisp.imframe.bind(sequence="<Motion>", 
                        func=self.mouseDragNoPressRemovePolygonDiffractionImage)
                self.maindisp.imframe.bind(sequence="<ButtonPress>", 
                        func=self.mouseButtonPressRemovePolygonDiffractionImage)
                self.maindisp.imframe.bind(sequence="<Leave>", 
                        func=self.mouseLeaveDiffractionImage)
                self.maindisp.graphframe.bind("<Configure>",
                        func=self.resizeDiffractionImage) 

                # redraw the images - note that the cake display 
                # need not be ready to display
                self.maindisp.updateimage()
                self.cakedisp.updateimageNoComplainNoShow()

            elif onOff == 0:
                # Give up on removing a polygon before a polygon 
                # had been removed

                self.currentPolygon = None

                if self.currentPolygonID != None:
                    self.maindisp.imframe.delete(self.currentPolygonID)
                    self.currentPolygonID = None

                # change bindings back to to regular zoom
                self.addZoomAndPanBindingsDiffractionImage()

                # unpress both 'Add Polygon' and 'Remove Polygon'
                self.addRemovePolygonRadioSelect.setvalue( [])

                # redraw the images
                self.maindisp.updateimage()
                self.cakedisp.updateimageNoComplainNoShow()


    def mouseDragNoPressRemovePolygonDiffractionImage(self,event):
        self.coordReportUpdateDiffractionImage(event.x,event.y)

        x,y = self.getRealDiffractionImageCoordinates(event.x,event.y)

        # get the polygon that the mouse is hovering over
        self.currentPolygon = self.maskedPixelInfo.getPolygon(x,y)
        if self.currentPolygon == None:
            # if we are no longer over a polygon, remove any 
            # possible remaning polygon outline.
            if self.currentPolygonID != None:
                self.maindisp.imframe.delete(self.currentPolygonID)
                self.currentPolygonID = None

        else:
            if self.currentPolygonID == None:
                self.currentPolygonID = self.maindisp.imframe.create_polygon(
                        self.convertPolygonFromImageToCanvasCoordinates(
                        self.currentPolygon),
                        outline='red',fill='')
            else:
                self.maindisp.imframe.coords(self.currentPolygonID,
                        self.convertPolygonFromImageToCanvasCoordinates(
                        self.currentPolygon))


    def mouseButtonPressRemovePolygonDiffractionImage(self,event):
        self.coordReportUpdateDiffractionImage(event.x,event.y)

        x,y = self.getRealDiffractionImageCoordinates(event.x,event.y)

        self.currentPolygon = None
        if self.currentPolygonID != None:
            self.maindisp.imframe.delete(self.currentPolygonID)
            self.currentPolygonID = None

        if self.maskedPixelInfo.removePolygon(x,y):
            # if we successfully remove a polygon, 
            # then leave the removing state.

            # change bindings back to to regular zoom
            self.addZoomAndPanBindingsDiffractionImage()

            # unpress both 'Add Polygon' and 'Remove Polygon'
            self.addRemovePolygonRadioSelect.setvalue( [])

            # redraw the images
            self.maindisp.updateimage()
            self.cakedisp.updateimageNoComplainNoShow()


    def convertPolygonFromImageToCanvasCoordinates(self,polygon):
        """ Converts a polygon from diffraction image coordinates 
            into canvas pixel coordinates. The polygon must be a 
            list of the form (x1, y1, x2, y2, x3, y3, ...) A 
            converted polygon is returned """

        if len(polygon) % 2 != 0:
            raise Exception("Cannot convert the diffraction \
image coordinates because the number of x and y coordinates \
are not equal.")

        canvasPolygon = []

        # loop over Coordinates
        for i in range(len(polygon)/2):
            canvasPolygon += self.getCanvasDiffractionImageCoordinates(
                    polygon[2*i+0],polygon[2*i+1])
        return Tkinter._flatten(canvasPolygon)

    def mouseButtonPressAddPolygonDiffractionImage(self,event):
        self.coordReportUpdateDiffractionImage(event.x,event.y)

        if event.num == 1: # left click, add a new node to the polygon

            self.maindisp.imframe.bind(sequence="<Motion>", 
                    func=self.mouseDragAddPolygonDiffractionImage)

            if self.currentPolygon == None:
                # no polygon yet, make new one
                x,y = self.getRealDiffractionImageCoordinates(event.x,event.y)
                self.currentPolygon = [x, y, x, y]

                self.currentPolygonID = self.maindisp.imframe.create_polygon(
                        self.convertPolygonFromImageToCanvasCoordinates(
                        self.currentPolygon),
                        outline='red',fill='')
            else:
                # add new coords to existing polygon
                x,y = self.getRealDiffractionImageCoordinates(event.x,event.y)
                self.currentPolygon += [x,y]

                self.maindisp.imframe.coords(self.currentPolygonID,
                        self.convertPolygonFromImageToCanvasCoordinates(
                        self.currentPolygon))

        else: 
            # right click, so finish the making polygon 
            # and get ready to draw a new one
            self.maskedPixelInfo.addPolygon(self.currentPolygon)

            # remove the drawn polygon
            self.maindisp.imframe.delete(self.currentPolygonID)
            self.currentPolygon = None
            self.currentPolygonID = None

            # change bindings back to to regular zoom
            self.addZoomAndPanBindingsDiffractionImage()

            # unpress both 'Add Polygon' and 'Remove Polygon'
            self.addRemovePolygonRadioSelect.setvalue( [])

            # redraw the images
            self.maindisp.updateimage()
            self.cakedisp.updateimageNoComplainNoShow()


    def mouseDragAddPolygonDiffractionImage(self,event):
        self.coordReportUpdateDiffractionImage(event.x,event.y)

        x,y = self.getRealDiffractionImageCoordinates(event.x,event.y)
        # update the last coordinate in the exisitn polygon
        self.currentPolygon[-2],self.currentPolygon[-1] = x,y

        # display this now on the scren
        self.maindisp.imframe.coords(self.currentPolygonID,
                self.convertPolygonFromImageToCanvasCoordinates(
                self.currentPolygon))


    def addZoomAndPanBindingsDiffractionImage(self):
        self.maindisp.imframe.bind(sequence="<Shift-ButtonPress>", 
                func=self.mouseDownPanDiffractionImage)
        self.maindisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragNoPressDiffractionImage)
        self.maindisp.imframe.bind(sequence="<ButtonPress>", 
                func=self.mouseDownZoomDiffractionImage)
        self.maindisp.imframe.bind(sequence="<Leave>", 
                func=self.mouseLeaveDiffractionImage)
        self.maindisp.graphframe.bind("<Configure>",    
                func=self.resizeDiffractionImage) 


    def loadDiffractionFile(self,filenames=None):
        """ Optionally takes in a string with filenames 
            separated by spaces. """

        self.extension = None

        if filenames == None:
            # if no filename(s) given, read filename(s) form user input
            filenames=(General.splitPaths(self.fileentry.getvalue()))
        else:
            # if a single filename (or multiple filenames 
            # all in one long string) were passed, make 
            #it into a list
            filenames=General.splitPaths(filenames)

        if len(filenames) < 1:
            raise UserInputException("A filename must be given \
before that file can be loaded.")

        setstatus(self.status,"Loading...")

        # reset the gui before you load a (possibly) new image
        self.resetGui()

        # put possibly all the filenames into the user input
        # with each filename separated by a comma
        # separation
        self.fileentry.setvalue(General.joinPaths(filenames))

        try:
            # if this doesn't work, we don't want to loose our old object

            # load in the file(s)
            temp = DiffractionData(filenames)
            self.diffractionData = temp
        except UnknownFiletypeException,e:

            # if the DiffractionData object can't open file, 
            # ask explicitly for the file type and tell it to object

            self.dialog = Pmw.Dialog(self.xrdwin,
                buttons = ('mar 3450','mar 2300','Mar CCD Format',
                        'TIFF','Bruker','Cancel'),
                defaultbutton = 'Cancel',
                title = 'What Format is this File?',
                command = self.setExtension)

            self.dialog.activate()

            # unless you get a good extension, give up and return
            if self.extension != "mar3450" and self.extension != 'mar2300' \
                    and self.extension != "mccd" and self.extension != 'tiff' \
                    and self.extension != "edf" and \
                    self.extension != "bruker": return 

            self.diffractionData = DiffractionData(filenames,
                    extension=self.extension)

        self.maindisp.updateimage()
        self.addZoomAndPanBindingsDiffractionImage()

        removeAllItemsFromMenu(self.openedfilesmenu)

        for file in filenames:
            self.openedfilesmenu.add_command(label=file,command=DISABLED)

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            if len(filenames) > 1:
                self.macroMode.explicitMacroRecordTwoLines(
                        'Multiple Data Files:','\t[ %s ]' % 
                        getMaskedPeakList(self.maskedPixelInfo))
            else:
                self.macroMode.explicitMacroRecordTwoLines(
                        'Data File:','\t'+filenames[0])

        setstatus(self.status,"Ready")


    def selectStandardQDataFile(self,basename,filename):
        self.qfileentry.setvalue(filename)
        self.loadQData(doStandardQ=1)
        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Standard Q','\t %s' % basename)


    def selectQDataFile(self,filename=''):
        if filename=='':
            filename = tkFileDialog.askopenfilename(
                    filetypes=[('Data File','*.dat'),
                    ('All Files','*')],
                    initialdir=self.defaultDir,
                    title="Load Q Data")

        if filename in ['',()]: return 
        self.qfileentry.setvalue(filename)
        self.loadQData()


    def loadQData(self,doStandardQ=0):
        filename = self.qfileentry.getvalue()
        if filename == "":
            raise UserInputException("You must enter a Q data \
file name before it is loaded.")

        self.QData = QData.QData(filename)

        # reset peak list if different Q values come in
        self.peakList = None

        self.updatebothNoComplain()

        # Make sure to explicitly record this macro command (unless
        # this is being called b/c standardQ was pushed by user
        if self.macroLines != None and not doStandardQ:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Q Data:','\t %s' % filename)


    def addConstantQLinesCakeImage(self):
        # if there is nothing to do, the job is done
        if not self.drawQ.checkvar.get() and \
                not self.drawdQ.checkvar.get():
            return 

        if self.QData == None:
            raise UserInputException("Cannot add constant Q \
lines to the image until a QData file is set.")

        if self.calibrationData == [] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot add constant Q \
lines to the image until the calibration parameters are set.")

        if self.diffractionData == None:
            raise UserInputException("Cannot add constant Q \
lines to the image until a diffraction image is set.")

        self.addUserInputCalibrationDataToObject()

        # remove old Q lines
        for id in self.allQLineIDsCakeImage:
            self.cakedisp.imframe.delete(id)
        self.allQLineIDsCakeImage = []

        for Q,dQ in self.QData.getAllQPairs():
            # q lines are straight on caked data

            if self.drawQ.checkvar.get():
                    
                    x1,y1 = self.getCanvasCakeImageCoordinates(
                            Q,self.cakeRange[-1]['chiLower'])
                    x2,y2 = self.getCanvasCakeImageCoordinates(
                            Q,self.cakeRange[-1]['chiUpper'])

                    self.allQLineIDsCakeImage.append(
                            self.cakedisp.imframe.create_line(
                            x1,y1,x2,y2,fill=self.qLinesColor.get(),
                            width=1))

            if self.drawdQ.checkvar.get():
                    x1,y1 = self.getCanvasCakeImageCoordinates(
                            Q-dQ,self.cakeRange[-1]['chiLower'])
                    x2,y2 = self.getCanvasCakeImageCoordinates(
                            Q-dQ,self.cakeRange[-1]['chiUpper'])

                    self.allQLineIDsCakeImage.append(
                            self.cakedisp.imframe.create_line(
                            x1,y1,x2,y2,fill=self.dQLinesColor.get(),
                            width=1))

                    x1,y1 = self.getCanvasCakeImageCoordinates(
                            Q+dQ,self.cakeRange[-1]['chiLower'])
                    x2,y2 = self.getCanvasCakeImageCoordinates(
                            Q+dQ,self.cakeRange[-1]['chiUpper'])

                    self.allQLineIDsCakeImage.append(
                            self.cakedisp.imframe.create_line(
                            x1,y1,x2,y2,fill=self.dQLinesColor.get(),
                            width=1))

   
    def addPeaksCakeImage(self):
        # if there is nothing to do, the job is done
        if not self.drawPeaks.checkvar.get():
            return 

        if self.diffractionData == None:
            raise UserInputException("Cannot add peaks to the \
image until a diffraction image is set.")

        if self.cakeRange == []: 
            raise UserInputException("Cannot add peaks to the \
image until a diffraction image is set.")

        # no peak list = Don't do anything
        if self.peakList==None: return 

        # delete old lines
        for id in self.allPeakListIDsCakeImage:
            self.cakedisp.imframe.delete( id ) 
        self.allPeakListIDsCakeImage = []

        # update calibration data first
        self.addUserInputCalibrationDataToObject()

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work \
in either Q or 2theta mode.")

        # the nice thing about using the getSmallestRange 
        # function to calculate how big the xs will be is 
        # that the size will be independed of the cake range 
        # that the user selected.
        entireCakeRange = self.diffractionData.getSmallestRange(
                self.calibrationData[-1],type=type)

        unZoomWidth = 2.5

        # scale the length of the xs. For example, zoomed 
        # in to 50% means will cause the xs to be drawn 
        # with double the length.
        numTimesZoomInQ = abs( (entireCakeRange['qOrTwoThetaUpper'] - \
                entireCakeRange['qOrTwoThetaLower'])/ \
                (self.cakeRange[-1]['qOrTwoThetaUpper'] - \
                self.cakeRange[-1]['qOrTwoThetaLower']) )

        numTimesZoomInChi = abs( (entireCakeRange['chiUpper'] - \
                entireCakeRange['chiLower'])/ \
                (self.cakeRange[-1]['chiUpper'] - \
                self.cakeRange[-1]['chiLower']) )

        scalingFactor = min(numTimesZoomInQ,numTimesZoomInChi)

        halflength = unZoomWidth*scalingFactor
        
        if self.drawPeaks.checkvar.get():
            for x,y,qReal,qFit,chi,width in \
                    self.peakList.getMaskedPeakList(
                            self.maskedPixelInfo):
                # for each peak, we want to take the true 
                # x,y value of where the peak is on the 
                # image and figure out where it belongs 
                # on the cake data.
                qTemp,chiTemp = Transform.getQChi(
                        self.calibrationData[-1],x,y)

                # if our chi range begins in the negative, 
                # we might have to place our chi values in 
                # their 360 degree rotated values. Note that
                # getQChi always returns chi between 0 and 360
                if (chiTemp-360) > self.cakeRange[-1]['chiLower'] and \
                        (chiTemp-360) < self.cakeRange[-1]['chiUpper']:
                        chiTemp -= 360
                    
                canvasX,canvasY = self.getCanvasCakeImageCoordinates(
                        qTemp,chiTemp)

                # add in new lines if they would be visible
                if (canvasX >= 0 and canvasX < self.cakeImageWidth \
                        and canvasY >= 0 and canvasY < self.cakeImageHeight):

                    self.allPeakListIDsCakeImage.append(
                            self.cakedisp.imframe.create_line(
                            canvasX-halflength,canvasY-halflength,
                            canvasX+halflength,canvasY+halflength,
                            fill=self.peakLinesColor.get(),
                            width="1"))

                    self.allPeakListIDsCakeImage.append(
                            self.cakedisp.imframe.create_line(
                            canvasX+halflength,canvasY-halflength,
                            canvasX-halflength,canvasY+halflength,
                            fill=self.peakLinesColor.get(),
                            width="1"))

 
    def mouseDownZoomCakeImage(self,event):
        global druged, x0, y0, x1,y1
        druged = 0
        (x0, y0) = event.x, event.y
        (x1, y1) = event.x, event.y
        self.cakedisp.imframe.bind(sequence="<Motion>",
                func=self.mouseDragZoomCakeImage)        
        self.cakedisp.imframe.bind(sequence="<ButtonRelease>",
                func=self.mouseUpZoomCakeImage)
        
        # if right click = zoom in, draw the rectangle
        if event.num==1:
            self.zoomRectangle = \
                    self.cakedisp.imframe.create_rectangle(
                    x0,y0,x0,y0,dash=(2,2),outline="black" )

 
    def mouseLeaveCakeImage(self,event):
        """ Stop reporting cordinates. """
        self.noCoordReportUpdateCakeImage()

        
    def mouseDragPanCakeImage(self,event): 
        global druged, lastX, lastY

        currentX,currentY = event.x, event.y

        # if the mouse has not moved very much, do not recake
        if abs(currentX-lastX) < 1 and abs(currentY-lastY) < 1:
            return 

        druged = 1
        
        qOrTwoThetaLower = float(self.cakeRange[-1]['qOrTwoThetaLower'])
        qOrTwoThetaUpper = float(self.cakeRange[-1]['qOrTwoThetaUpper'])

        chiLower = float(self.cakeRange[-1]['chiLower'])
        chiUpper = float(self.cakeRange[-1]['chiUpper'])

        # figure out how far, in q-chi space, the 
        # person has moved the mouse since last time. 
        # Change the zoom range by that much.
        qOrTwoThetaDiff = ((currentX-lastX)*1.0/self.cakeImageWidth)* \
                (qOrTwoThetaUpper-qOrTwoThetaLower)
        chiDiff = ((currentY-lastY)*1.0/self.cakeImageHeight)* \
                (chiUpper-chiLower)

        # store where we are now
        lastX,lastY = currentX,currentY 

        # don't zoom outside of any bound
        if qOrTwoThetaLower-qOrTwoThetaDiff < 0:
            qOrTwoThetaDiff = qOrTwoThetaLower

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
                    either Q or 2theta mode.")

        if type == "Q":
            if qOrTwoThetaUpper-qOrTwoThetaDiff > \
                    Transform.getMaxQ(self.calibrationData[-1]):
                qOrTwoThetaDiff = qOrTwoThetaUpper - \
                        Transform.getMaxQ(self.calibrationData[-1])
        if type == "2theta": 
            if qOrTwoThetaUpper-qOrTwoThetaDiff > \
                    Transform.getMaxTwoTheta():
                qOrTwoThetaDiff = qOrTwoThetaUpper - \
                        Transform.getMaxTwoTheta()

        if chiLower-chiDiff < -360:
            chiDiff = chiLower + 360

        if chiUpper-chiDiff > 360:
            chiDiff = chiUpper - 360

        # act as though this was the cake range all along
        # This way, when you undo, you only undo through
        # previous zooms and not through previous pans

        val = float(str(qOrTwoThetaLower-qOrTwoThetaDiff)[:8])
        self.cakeRange[-1]['qOrTwoThetaLower'] = val
        self.qOrTwoThetaLowerCake.setvalue(val)
        
        val = float(str(qOrTwoThetaUpper-qOrTwoThetaDiff)[:8])
        self.cakeRange[-1]['qOrTwoThetaUpper'] = val
        self.qOrTwoThetaOrTwoThetaUpperCake.setvalue(val)

        val = float(str(chiLower-chiDiff)[:8])
        self.cakeRange[-1]['chiLower'] = val
        self.chiLowerCake.setvalue(val)

        val = float(str(chiUpper-chiDiff)[:8])
        self.cakeRange[-1]['chiUpper'] = val
        self.chiUpperCake.setvalue(val)

        self.coordReportUpdateCakeImage(currentX,currentY)

        self.cakedisp.updateimage()


    def mouseUpPanCakeImage(self,event):
        global druged
        self.cakedisp.imframe.unbind(sequence="<Motion>")
        self.cakedisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragNoPressCakeImage)
        self.cakedisp.imframe.unbind(sequence="<ButtonRelease>")


    def mouseDownPanCakeImage(self,event):
        global druged, lastX, lastY
        druged = 0
        (lastX, lastY) = event.x, event.y
        self.cakedisp.imframe.bind(sequence="<Motion>",
                func=self.mouseDragPanCakeImage)
        self.cakedisp.imframe.bind(sequence="<ButtonRelease>",
                func=self.mouseUpPanCakeImage)

 
    def noCoordReportUpdateCakeImage(self):
        self.cakedisp.xcoord.config(text="X=      ")
        self.cakedisp.ycoord.config(text="Y=      ")
        self.cakedisp.qcoord.config(text="Q=      ")
        self.cakedisp.dcoord.config(text="D=      ")
        self.cakedisp.ccoord.config(text="chi=      ")
        self.cakedisp.icoord.config(text="I=      ")


    def coordReportUpdateCakeImage(self,x,y):
        """ x,y are dixel distances relative to the canvas. """
        Q,chi = self.getQChiCakeImageCoordinates(x,y)
        x,y = Transform.getXY(self.calibrationData[-1], Q, chi)
        text=("X="+str(x))[:12] 
        self.cakedisp.xcoord.config(text=text)
        text=("Y="+str(y))[:12] 
        self.cakedisp.ycoord.config(text=text)

        try:
            intensity = self.diffractionData.getPixelValueBilinearInterpolation(x,y)
        except:
            intensity = ''
        text=("I="+str(intensity))[:12] 
        self.cakedisp.icoord.config(text=text)

        if self.calibrationData and self.calibrationData[-1].allSet():
            text=("Q="+str(Q))[:12] 
            self.cakedisp.qcoord.config(text=text)
            if Q == 0:
                self.cakedisp.dcoord.config(text="D=      ")
            else:
                D=2*math.pi/Q
                text=("D="+str(D))[:12] 
                self.cakedisp.dcoord.config(text=text)
            text=("chi="+str(chi))[:12] 
            self.cakedisp.ccoord.config(text=text)
        else:
            self.cakedisp.qcoord.config(text="Q=      ")
            self.cakedisp.dcoord.config(text="D=      ")
            self.cakedisp.ccoord.config(text="chi=      ")


    def doZoomCakeImage(self,qOrTwoThetaLower,qOrTwoThetaUpper,
            chiLower,chiUpper):
        self.qOrTwoThetaLowerCake.setvalue(qOrTwoThetaLower)
        self.qOrTwoThetaUpperCake.setvalue(qOrTwoThetaUpper)
        self.chiLowerCake.setvalue(chiLower)
        self.chiUpperCake.setvalue(chiUpper)

        self.cakedisp.updateimage()


    def undoZoomCakeImage(self,event=None):
        # if there is the current cake range and 
        # an old one, get rid of the current one, 
        # and put the previous one into the GUI.
        if len(self.cakeRange) > 1:
            self.cakeRange.pop()
            self.qOrTwoThetaLowerCake.setvalue(
                    self.cakeRange[-1]['qOrTwoThetaLower'])
            self.qOrTwoThetaUpperCake.setvalue(
                    self.cakeRange[-1]['qOrTwoThetaUpper'])

            self.chiLowerCake.setvalue(
                    self.cakeRange[-1]['chiLower'])
            self.chiUpperCake.setvalue(
                    self.cakeRange[-1]['chiUpper'])

        self.cakedisp.updateimage()


    def mouseDragNoPressCakeImage(self,event):
        self.coordReportUpdateCakeImage(event.x,event.y)


    def mouseDragZoomCakeImage(self,event):
        global x0, y0, x1, y1,druged
        druged = 1
        (x1, y1) = event.x, event.y

        # redraw rectangle
        try:
            self.cakedisp.imframe.coords(self.zoomRectangle,x0,y0,x1,y1)
        except:
            # it dosen't matter if this fails
            pass
        self.coordReportUpdateCakeImage(x1,y1)
 

    def mouseUpZoomCakeImage(self,event):
        global druged
        global x0, y0, x1, y1        

        self.cakedisp.imframe.unbind(sequence="<Motion>")
        self.cakedisp.imframe.bind(sequence="<Motion>", 
                func=self.mouseDragNoPressCakeImage)

        self.cakedisp.imframe.unbind(sequence="<ButtonRelease>")

        # If this was a left click, try to zoom in. 
        # Otherwise, zoom out
        if event.num == 1:
            self.cakedisp.imframe.delete(self.zoomRectangle)
            # ensure that the user would zoom into a real window
            if druged and (abs(x1-x0)>1 and abs(y1-y0)>1):
                qLower,chiLower = self.getQChiCakeImageCoordinates(x0,y0)
                qUpper,chiUpper = self.getQChiCakeImageCoordinates(x1,y1)

                qLower,qUpper = \
                    min(qLower,qUpper),max(qLower,qUpper)

                chiLower,chiUpper = \
                    min(chiLower,chiUpper),max(chiLower,chiUpper)

                if self.Qor2Theta.get() == "Work in Q":
                    type = "Q"
                elif self.Qor2Theta.get() == "Work in 2theta":
                    type = "2theta"
                else:
                    raise UserInputException("The program must work in \
either Q or 2theta mode.")

                if type == "Q":
                    qOrTwoThetaLower = qLower
                    qOrTwoThetaUpper = qUpper

                    if qOrTwoThetaUpper > Transform.getMaxQ(
                            self.calibrationData[-1]):
                        qOrTwoThetaUpper = Transform.getMaxQ(
                                self.calibrationData[-1])

                elif type == "2theta":
                    qOrTwoThetaLower = Transform.convertQToTwoTheta(
                            qLower,self.calibrationData[-1])
                    qOrTwoThetaUpper = Transform.convertQToTwoTheta(
                            qUpper,self.calibrationData[-1])

                    if qOrTwoThetaUpper > Transform.getMaxTwoTheta():
                        qOrTwoThetaUpper = Transform.getMaxTwoTheta()
        
                # make sure not to zoom of the map

                if qOrTwoThetaLower < 0:
                    qOrTwoThetaLower = 0
                if chiLower < -360:
                    chiLower = -360
                if chiUpper > 360:
                    chiUpper = 360

                if chiUpper-chiLower > 360:
                    # if the intent is to zoom into too big 
                    # a chi range, make smaller which of 
                    # chiLower or chiUpper is currently off 
                    # the screen

                    if chiUpper > float(self.cakeRange[-1]['chiUpper']):
                        chiUpper = chiLower+360
                    else:
                        chiLower = chiUpper-360

                # set the new zoom scale

                qOrTwoThetaLower = float(str(qOrTwoThetaLower)[:8])
                qOrTwoThetaUpper = float(str(qOrTwoThetaUpper)[:8])
                chiLower = float(str(chiLower)[:8])
                chiUpper = float(str(chiUpper)[:8])

                self.doZoomCakeImage(qOrTwoThetaLower,qOrTwoThetaUpper,
                        chiLower,chiUpper)
        else:
            self.undoZoomCakeImage()


    def setAutoCakeRange(self):

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")
        
        range = self.diffractionData.getSmallestRange(
                calibrationData = self.calibrationData[-1],
                type = type)

        self.qOrTwoThetaLowerCake.setvalue(range['qOrTwoThetaLower'])
        self.qOrTwoThetaUpperCake.setvalue(range['qOrTwoThetaUpper'])
        self.numQOrTwoThetaCake.setvalue(self.cakeImageWidth)

        self.chiLowerCake.setvalue(range['chiLower'])
        self.chiUpperCake.setvalue(range['chiUpper'])
        self.numChiCake.setvalue(self.cakeImageHeight)


    def autoCake(self):
        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.diffractionData==None:
            raise UserInputException("Cannot cake until an \
image is loaded.")
        if self.calibrationData==[] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot cake until the \
calibration parameters are set.")

        # when you auto cake, kill the old zoom range
        self.cakeRange = []
        self.setAutoCakeRange() 

        self.cakedisp.updateimage()


    def saveIntegratedIntensity(self,filename=''):
        if self.integrate == None:
            raise UserInputException("Cannot save the intensity \
integrated data until the integration has been performed")
        
        if filename in ['',()]: 
            defaultextension = ".dat"
            filename = tkFileDialog.asksaveasfilename(
                    filetypes=[('Data File','*.dat'),('All Files','*')],
                    defaultextension = defaultextension,
                    initialdir=self.defaultDir,
                    title="Save Integrated Intensity")

            if filename in ['',()]: return 

            # on the mac, it won't give a default extension 
            # if you don't write it out explicitly, so make 
            # sure to do so automatically otherwise
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension


        self.integrate.toFile(filename,
                self.diffractionData.theDiffractionData.filename)

        # Make sure to explicitly record this macro command
        if self.macroLines != None:
            self.macroMode.explicitMacroRecordTwoLines(
                    'Save Integration Data','\t %s' % filename)


    def autoIntegrateQOrTwoThetaI(self):
        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work \
in either Q or 2theta mode.")

        # must set numChi somehow
        self.numQOrTwoThetaIntegrate.setvalue(200)

        if self.diffractionData:
            range = self.diffractionData.getSmallestRange(
                    self.calibrationData[-1],type=type)
            self.QOrTwoThetaLowerIntegrate.setvalue(
                    range['qOrTwoThetaLower'])
            self.QOrTwoThetaUpperIntegrate.setvalue(
                    range['qOrTwoThetaUpper'])
            self.constrainWithRangeOnRight.set(0)
            self.integrateQOrTwoThetaI()

        else:
            self.QOrTwoThetaLowerIntegrate.setvalue(0)
            self.QOrTwoThetaUpperIntegrate.setvalue(
                    Transform.getMaxQ(self.calibrationData[-1]))

        
    def integrateQOrTwoThetaI(self):
        setstatus(self.status,'Integrating...')
        self.resetIntegrationDisplay()

        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.diffractionData==None:
            raise UserInputException("Cannot integrate \
until an image is loaded.")

        if self.calibrationData==[] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot integrate \
until the calibration parameters are set.")

        try:
            num = int(self.numQOrTwoThetaIntegrate.getvalue())
        except:
            raise UserInputException("The number of Q values \
to use when integrating has not been set.")

        try:
            lower = float(self.QOrTwoThetaLowerIntegrate.getvalue())
        except:
            raise UserInputException("The lower Q value to \
use when integrating has not been set.")

        try:
            upper = float(self.QOrTwoThetaUpperIntegrate.getvalue())
        except:
            raise UserInputException("The upper Q value to \
use when integrating has not been set.")

        if self.Qor2Theta.get() == "Work in Q":

            if lower >= upper:
                raise UserInputException("Unable to integrate \
the intensity. The lower Q value must be less then the upper \
Q value")

            if lower < 0:
                raise UserInputException("Unable to integrate \
intensity. The lower Q value must be larger then 0.")

            if upper > Transform.getMaxQ(self.calibrationData[-1]):
                raise UserInputException("Unable to integrate \
intensity. The upper Q value must be less then the largest \
possible Q value.")

            if num < 1:
                raise UserInputException("Unable to integrate \
intensity. The number of Q must be at least 1.")

        elif self.Qor2Theta.get() == "Work in 2theta":

            if lower >= upper:
                raise UserInputException("Unable to integrate \
the intensity. The lower 2theta value must be less then the \
upper 2theta value")

            if lower < 0:
                raise UserInputException("Unable to integrate \
intensity. The lower 2theta value must be larger then 0.")

            if upper > 90:
                raise UserInputException("Unable to integrate \
intensity. The upper 2theta value must be smaller then 90.")

            if num < 1:
                raise UserInputException("Unable to integrate \
intensity. The number of 2theta must be at least 1.")

        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")

        constrainWithRangeOnRight = self.constrainWithRangeOnRight.get()
        doConstraint = constrainWithRangeOnRight

        if doConstraint:
            try:
                constraintLower = float(self.chiLowerIntegrate.getvalue())
            except:
                raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range On Right' \
has been set, a valid chi lower must be given")

            try:
                constraintUpper = float(self.chiUpperIntegrate.getvalue())
            except:
                raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range On Right' \
has been set, a valid chi upper must be given")

            if constraintLower >= constraintUpper:
                raise UserInputException("Unable to integrate \
the intensity. The constraint lower chi value must be less \
then the upper chi value")

            if constraintLower < -360:
                raise UserInputException("Unable to integrate \
intensity. The constraint lower chi value must be larger \
then -360 degrees.")

            if constraintUpper > +360:
                raise UserInputException("Unable to integrate \
intensity. The constraint upper chi value must be lower \
then 360 degrees.")

            if constraintUpper - constraintLower > 360:
                raise UserInputException("Unable to integrate \
intensity. The constraint chi range can be at most 360 degrees.")
            
        else:
            # the bound dosen't matter, so just give it 
            # something arbitrary
            constraintLower,constraintUpper = 0,0
        
        doPolarizationCorrection = self.doPolarizationCorrectionIntegrate.get()
        if doPolarizationCorrection:
            try:
                P = float(self.PIntegrate.getvalue())
            except:
                raise UserInputException("The P integration value has \
not been set.")

        else:
            P = 0 # P can be anything since it won't be used.

        self.addMaskedPixelInfoToObject(
                operationString="integrate the diffraction data")
            
        if self.Qor2Theta.get() == "Work in Q":
            self.integrate = self.diffractionData.integrateQI(
                    calibrationData = self.calibrationData[-1],
                    lower = lower,
                    upper = upper,
                    num = num,
                    constraintLower = constraintLower,
                    constraintUpper = constraintUpper,
                    doConstraint = doConstraint,
                    doPolarizationCorrection = doPolarizationCorrection,
                    P = P,
                    typeOfConstraint = "chi",
                    maskedPixelInfo = self.maskedPixelInfo)

            self.integratedisp.makegraph(xd=self.integrate.getValues(),
                    yd=self.integrate.getIntensityData(),
                    yLabel='I',xLabel='Q',
                    xUpdateName='Q',yUpdateName='I',
                    dontConnectDataPointsWithValue=-1)

        elif self.Qor2Theta.get() == "Work in 2theta":
            self.integrate = self.diffractionData.integrate2ThetaI(
                    calibrationData = self.calibrationData[-1],
                    lower = lower,
                    upper = upper,
                    num = num,
                    constraintLower = constraintLower,
                    constraintUpper = constraintUpper,
                    doConstraint = doConstraint,
                    doPolarizationCorrection = doPolarizationCorrection,
                    P = P,
                    typeOfConstraint = "chi",
                    maskedPixelInfo = self.maskedPixelInfo) 

            self.integratedisp.makegraph(
                    xd=self.integrate.getValues(),
                    yd=self.integrate.getIntensityData(),
                    yLabel='I',xLabel='2theta',
                    xUpdateName='2theta',yUpdateName='I',
                    dontConnectDataPointsWithValue=-1)
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")

        # show the new display
        self.integratedisp.main.show()

        setstatus(self.status,'Ready')

    
    def autoIntegrateChiI(self):
        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.Qor2Theta.get() == "Work in Q":
            type = "Q"
        elif self.Qor2Theta.get() == "Work in 2theta":
            type = "2theta"
        else:
            raise UserInputException("The program must work in \
either Q or 2theta mode.")

        # must set numChi somehow
        self.numChiIntegrate.setvalue(200)

        if self.diffractionData:
            range = self.diffractionData.getSmallestRange(
self.calibrationData[-1],type=type)
            
            self.chiLowerIntegrate.setvalue(range['chiLower'])
            self.chiUpperIntegrate.setvalue(range['chiUpper'])

            self.constrainWithRangeOnLeft.set(0)

            self.integrateChiI()

        else:
            self.QOrTwoThetaLowerIntegrate.setvalue(-180)
            self.QOrTwoThetaUpperIntegrate.setvalue(180)
        

    def integrateChiI(self):
        setstatus(self.status,'Integrating...')
        self.resetIntegrationDisplay()

        # update calibrationData first
        self.addUserInputCalibrationDataToObject()

        if self.diffractionData==None:
            raise UserInputException("Cannot integrate until \
an image is loaded.")

        if self.calibrationData==[] or \
                not self.calibrationData[-1].allSet():
            raise UserInputException("Cannot integrate until \
the calibration parameters are set.")

        try:
            num = int(self.numChiIntegrate.getvalue())
        except:
            raise UserInputException("Cannot integrate \
intensity. The number of chi values to use when integrating \
has not been set.")

        try:
            lower = float(self.chiLowerIntegrate.getvalue())
        except:
            raise UserInputException("Cannot integrate \
intensity. The lower chi value to use when integrating \
has not been set.")

        try:
            upper = float(self.chiUpperIntegrate.getvalue())
        except:
            raise UserInputException("Cannot integrate \
intensity. The upper chi value to use when integrating \
has not been set.")

        if upper-lower > 360:
            raise UserInputException("Cannot integrate \
intensity. The chi range must be at most 360 degrees.")

        constrainWithRangeOnLeft = self.constrainWithRangeOnLeft.get()
        doConstraint = constrainWithRangeOnLeft

        if doConstraint:
            try:
                constraintLower = float(self.QOrTwoThetaLowerIntegrate.getvalue())
            except:
                if self.Qor2Theta.get() == "Work in Q":
                    raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range On Right' has \
been set, a valid Q lower must be given")

                elif self.Qor2Theta.get() == "Work in 2theta":
                    raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range On Right' has \
been set, a valid 2theta lower must be given")
                else:
                    raise UserInputException("The program must \
work in either Q or 2theta mode.")

            try:
                constraintUpper = float(self.QOrTwoThetaUpperIntegrate.getvalue())
            except:
                if self.Qor2Theta.get() == "Work in Q":
                    raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range on Right' has \
been set, a valid Q upper must be given")

                elif self.Qor2Theta.get() == "Work in 2theta":
                    raise UserInputException("Cannot integrate \
intensity. Since the option 'Constrain With Range on Right' has \
been set, a valid 2theta upper must be given")

                else:
                    raise UserInputException("The program must \
work in either Q or 2theta mode.")

            if self.Qor2Theta.get() == "Work in Q":
                constraintType = "Q"

                if constraintLower >= constraintUpper:
                    raise UserInputException("Unable to \
integrate the intensity. The constraint lower Q value must \
be less then the upper Q value")

                if constraintLower < 0:
                    raise UserInputException("Unable to \
integrate intensity. The constraint lower Q value must be \
larger then 0.")

                if constraintUpper > Transform.getMaxQ(self.calibrationData[-1]):
                    raise UserInputException("Unable to \
integrate intensity. The constraint upper Q value must \
be less then the largest possible Q value.")

            elif self.Qor2Theta.get() == "Work in 2theta":
                constraintType = "2theta"

                if constraintLower >= constraintUpper:
                    raise UserInputException("Unable to \
integrate the intensity. The constraint lower 2theta value \
must be less then the upper 2theta value")

                if constraintLower < 0:
                    raise UserInputException("Unable to \
integrate intensity. The constraint lower 2theta value \
must be larger then 0.")

                if constraintUpper > 90:
                    raise UserInputException("Unable to \
integrate intensity. The constraint upper 2theta value must \
be smaller then 90.")

            else:
                raise UserInputException("The program must \
work in either Q or 2theta mode.")

        else:
            # the bound dosen't matter, so just give it something arbitrary
            constraintType = ""
            constraintLower = 0
            constraintUpper = 0
        
        doPolarizationCorrection=self.doPolarizationCorrectionIntegrate.get()
        if doPolarizationCorrection:
            try:
                P = float(self.PIntegrate.getvalue())
            except:
                raise UserInputException("The P integration value \
has not been set.")
        else:
            P = 0 # P can be anything since it won't be used.

        self.addMaskedPixelInfoToObject(
                operationString="integrate the diffraction data")

        self.integrate = self.diffractionData.integrateChiI(
                calibrationData = self.calibrationData[-1],
                lower = lower,
                upper = upper,
                num = num,
                constraintLower = constraintLower,
                constraintUpper = constraintUpper,
                doConstraint = doConstraint,
                doPolarizationCorrection = doPolarizationCorrection,
                P = P,
                typeOfConstraint = constraintType,
                maskedPixelInfo = self.maskedPixelInfo)

        self.integratedisp.makegraph(xd=self.integrate.getValues(),
                yd=self.integrate.getIntensityData(),
                yLabel='I',xLabel='chi',
                xUpdateName='chi',yUpdateName='I',
                dontConnectDataPointsWithValue=-1)

        # show the new dsiplay
        self.integratedisp.main.show()

        setstatus(self.status,'Ready')


    def runMacro(self):
        # make the macro object do all the hard 
        # work so that macro running can happen
        self.macroMode.runMacro()
    

    def startRecordMacro(self):
        # make the macro object do all the hard 
        # work so that macro recording can happen
        self.macroMode.startRecordMacro()


    def stopRecordMacro(self):
        # make the macro object stop the macro from 
        # recording
        self.macroMode.stopRecordMacro()

    def setAsInitializationMacro(self):
        # make the macro object stop the macro from 
        # recording and set the recorded macro as
        # the macro run ever time the program opens
        self.macroMode.setAsInitializationMacro()


""" Start the Loop if this program is begin called explicitly. """
if __name__ == "__main__":
    class Start:
        Main(root)
        root.mainloop()

