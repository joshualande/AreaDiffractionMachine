from Tkinter import *
from math import log10
from Axis import Axis



# lame function for updating status bars
def setstatus(n,format):
    n.config(text=format)
    n.update_idletasks()


class LinePlot:
    """ Plot creates a pretty rudimentary scatter plot which is good 
        enough for my use. I am kind of ripping of the API 
        to Pmw's Blt - http://heim.ifi.uio.no/~hpl/Pmw.Blt/doc/reference.html
        I was originally using Pmw's BLT but found it incompatible
        with mac. So this is a rewrite in pure tkinter which should
        run anywhere that Tk is installed. I am basically just
        using the Blt interface so I don't have to change any other
        code. 

        When plotting data with a log y axis, this class will force 
        the axis so that the smallest possible y value is 1
        
        """

    graphwidth = None
    graphheight = None
    axisSize = None

    # store all the lines that need to be plotted
    # The format for these lines should be a hash where
    # the key is the name of some line and the
    # value is a tuple holding the x and then y data
    # as 2 seperate lists and also the current ID of the line 
    # (possibly equal to none).
    lines = {}

    # the only allowed marker is a rectangle
    # store the markers that should be put on this object.
    # the format for this is a hash where the key is the name
    # of some marker and the value is the ID of the object
    # as it is stored on the canvas.
    markers = {}

    inputXmin = None
    inputXmax = None
    inputYmin = None
    inputYmax = None

    usedXmin = None
    usedXmax = None
    usedYmin = None
    usedYmax = None

    def update(self):

        # remove everything from the graph
        for key in self.lines.keys():
            record = self.lines[key]
            for id in record['ID']:
                self.graph.delete(id)
            record['ID'] = []

        # if there is no line to plot AND no given axis
        if len(self.lines) == 0 and (self.inputXmin == None or
                self.inputXmax == None or self.inputYmin or
                self.inputYmax == 0):
            # configure the axis to have nothing in them
            self.xaxis.config(lowestValue=None,highestValue=None)
            self.yaxis.config(lowestValue=None,highestValue=None,
                    logscale = self.ylogscale)


        # figure out what usedXmin and usedXmax should be
        if self.inputXmin == None or self.inputXmax == None:
            # auto scale x
            self.usedXmin = None
            self.usedXmax = None
            for key in self.lines.keys():
                record = self.lines[key]
                for index in range(len(record['x'])):
                    if self.usedXmin == None or record['x'][index] < self.usedXmin:
                        self.usedXmin = record['x'][index]
                    if self.usedXmax == None or record['x'][index] > self.usedXmax:
                        self.usedXmax = record['x'][index]
            
        else:
            self.usedXmin = self.inputXmin
            self.usedXmax = self.inputXmax

        # figure out what usedYmin and usedYmax should be
        if self.inputYmin == None or self.inputYmax == None:
            # auto scale y
            self.usedYmin = None
            self.usedYmax = None
            for key in self.lines.keys():
                record = self.lines[key]
                for index in range(len(record['y'])):
                    if self.usedYmin == None or record['y'][index] < self.usedYmin:
                        self.usedYmin = record['y'][index]
                    if self.usedYmax == None or record['y'][index] > self.usedYmax:
                        self.usedYmax = record['y'][index]
            
        else:
            self.usedYmin = self.inputYmin
            self.usedYmax = self.inputYmax

        # configure the axis
        self.xaxis.config(lowestValue=self.usedXmin,highestValue=self.usedXmax)
        self.yaxis.config(lowestValue=self.usedYmin,highestValue=self.usedYmax,
                logscale=self.ylogscale)
        for line in self.lines.keys():
            record = self.lines[line]

            if len(record['x']) == 1:
                # draw just a point !!!
                # get the only line out
                x,y=self.invtransform(record['x'][0],record['y'][0])
                line['ID'].append(self.graph.create_line(
                            x,y,x,y,fill=record['color'],width=1))
            else:
                record['ID'] = []
                for index in range(len(record['x'])-1):
                    x1,y1 = self.transform(record['x'][index],record['y'][index])
                    x2,y2 = self.transform(record['x'][index+1],record['y'][index+1])
                    record['ID'].append(self.graph.create_line(
                                x1,y1,x2,y2,fill=record['color'],width=1))


    def element_names(self):
        return self.lines.keys()


    def marker_create(self,type, name, dashes,coords=""):
        """ Put the marker outside of the frame, for now. """
        if type != "line":
            raise Exception("The only type of marker that can be created is a line")
        self.markers[name] = self.graph.create_rectangle(-1,-1,-1,-1,
            dash=dashes,outline="black")
        

    def marker_configure(self,name,coords):
        (x0, y0, x1, y0, x1, y1, x0, y1, x0, y0) = coords
        # transform the real coordinates into canvas coordiantes 
        # before adding them to the graph
        x0,y0 = self.transform(x0,y0)
        x1,y1 = self.transform(x1,y1)
        self.graph.coords(self.markers[name],x0,y0,x1,y1)


    def marker_delete(self,name):
        self.graph.delete(self.markers[name])
        del self.markers[name]


    def inside(self,x,y):
        """ Check if the canvas coordinates (x,y) are inside the image. """
        if x>0 and x<self.graphwidth and y>0 and y<self.graphheight:
            return 1
        return 0


    def transform(self,x,y):
        """ takes in real coodinates as they are plotted and returns 
            the corresponding coordinates on the graph canvas. """

        if self.usedXmin == None or self.usedXmax == None or \
                self.usedYmin == None or self.usedYmax == None:
            
            if self.inputXmin == None or self.inputXmax == None or \
                    self.inputYmin == None or self.inputYmax == None:
                raise Exception("Cannot perform the inverse transform until a range for the plot is set.")
                
            xmin = self.inputXmin    
            xmax = self.inputXmax
            ymin = self.inputYmin    
            ymax = self.inputYmax
        else:
            xmin = self.usedXmin    
            xmax = self.usedXmax
            ymin = self.usedYmin    
            ymax = self.usedYmax

        transX = (x-xmin)*(self.graphwidth-1.0)/(xmax-xmin)
        if self.ylogscale:
            if y<=0:
                # anything less then 0 must be forced outside the image 
                # This is kind of tricky, though, because a Tkinter canvas
                # has negative values on top of the canvas and very large
                # values below the canvas. That it why we are giving 
                # our too small pixels very large values
                transY = 1000 
            else: 
                # if doing long scale, the smallest allowed ymin value is 1
                # and teh smallest allowed ymax value is 10
                if ymin < 1:
                    ymin = 1
                if ymax < 10:
                    ymax = 10
                transY = (self.graphheight-1.0)*(log10(y)-log10(ymin))/(log10(ymax)-log10(ymin))
                # coordiantes are weird b/c they go down not up, so we have to invert them
                transY = self.graphheight-1.0-transY
        else:
            transY = (y-ymin)*(self.graphheight-1.0)/(ymax-ymin)
            # coordiantes are weird b/c they go down not up, so we have to invert them
            transY = self.graphheight-1-transY

        return transX,transY


    def invtransform(self,x,y):
        """ takes in coordinates on the graph canvas 
            and convert them to real coordinates. """

        if self.usedXmin == None or self.usedXmax == None or \
                self.usedYmin == None or self.usedYmax == None:
            
            if self.inputXmin == None or self.inputXmax == None or \
                    self.inputYmin == None or self.inputYmax == None:
                raise Exception("Cannot perform the inverse transform until a range for the plot is set.")

            xmin = self.inputXmin    
            xmax = self.inputXmax
            ymin = self.inputYmin    
            ymax = self.inputYmax
        else:
            xmin = self.usedXmin    
            xmax = self.usedXmax
            ymin = self.usedYmin    
            ymax = self.usedYmax
                           
        transX = self.usedXmin+x*(self.usedXmax-self.usedXmin)/(self.graphwidth-1.0)
        if self.ylogscale:
            # remember that the lowest possible value allowed in a log plot is 1.
            usedYmin = self.usedYmin
            if usedYmin < 1.0:
                usedYmin = 1.0
            usedYmax = self.usedYmax
            if usedYmax < 10:
                usedYmax = 10.0
            print 'min,max = %f,%f' % (usedYmin,usedYmax)
            print 'logmin,logmax = %f,%f' % (log10(usedYmin),log10(usedYmax))
            print 'inside = ',((self.graphheight-1.0-y)/(self.graphheight-1.0))*(log10(usedYmax)-log10(usedYmin))-log10(usedYmin)
            transY = pow(10,((self.graphheight-1.0-y)/(self.graphheight-1.0))*(log10(usedYmax)-log10(usedYmin))-log10(usedYmin))
        else:        
            transY = self.usedYmin+(self.graphheight-1.0-y)*(self.usedYmax-self.usedYmin)/(self.graphheight-1.0)
        return transX,transY
                     

    def xaxis_configure(self,title=None,min=None,max=None):
        """ If min == '' and max == '', then auto scale the graph """
        if title != None: 
            print 'add title'

        # when min & max aren't passed in, then don't change the ranges
        if min != None and max != None:
            if min == '':
                if max != '':
                    raise Exception("You can not fix part but not all of one of the ranges.")
                self.inputXmin = None
                self.inputXmax = None
                self.usedXmin = None
                self.usedXmax = None

            else:
                self.inputXmin = min
                self.inputXmax = max
                self.usedXmin = None
                self.usedXmax = None

        self.update()


    def yaxis_configure(self,title=None,min=None,max=None,logscale=None):
        """ If min == '' and max == '', then auto scale the graph """

        if title != None: 
            print 'add title'

        # when min & max aren't passed in, then don't change the ranges
        if min != None and max != None:
            # if they are both set to '', reset the axis
            if min == '':
                if max != '':
                    raise Exception("You can not fix part but not all of one of the ranges.")
                self.inputYmin = None
                self.inputYmax = None
                self.usedYmin = None
                self.usedYmax = None
            
            else:
                # otherwise, set it to new values
                self.inputYmin = min
                self.inputYmax = max
                self.usedYmin = None
                self.usedYmax = None

        if logscale != None:
            self.ylogscale = logscale

        self.update()


    def resize(self,event):
        """ Resize canvas if needed. """

        # resize canvas properly
        if event.width <= self.axisSize or \
                event.height <= self.axisSize:
            return

        self.graphwidth=event.width-self.axisSize
        self.graphheight=event.height-self.axisSize

        self.graph.config(height=self.graphheight,
                width=self.graphwidth)

        self.xaxis.config(width=self.graphwidth,
                height=self.axisSize)

        self.yaxis.config(width=self.axisSize,
                height=self.graphheight)

        self.update()


    def line_create(self,name,xdata=None,ydata=None,symbol='',color='red'):
        if symbol != '': 
            raise Exception("Currently, no symbols can be used when drawing graphs.")
        
        if len(xdata) != len(ydata):
            raise Exception("The number of x and y values of the line to plot must be equal")
    
        if len(xdata) < 1:
            raise Exception("There must be at least one point to plot on the current line") 

        if name in self.lines.keys():
            raise Exception("Cannot add this line because another line with the same name already exists.")
                    
        self.lines[name]={'x':xdata,'y':ydata,'color':color,'ID':[]}
        self.update()
    

    def element_delete(self,g):
        """ Deletes one of the lines by its name. """

        if not g in self.lines.keys():
            raise Exception("Cannot delete element that dose not exist.")

        # remove everything from the graph
        for id in self.lines[g]['ID']:
            self.graph.delete(id)

        del self.lines[g]
        self.update()


    def xaxis_cget(self,str):
        if str=="min":
            return self.inputXmin
        if str=="max":
            return self.inputXmax

    def yaxis_cget(self,str):
        if str=="min":
            return self.inputYmin
        if str=="max":
            return self.inputYmax

    def bind(self,**args):
        """ Bindings happen only on the graph with the data on it.
            I have no idea why I can't just call the function bind
            as:
            
                self.graph.bind(args) 
        
            But what works, works... """
        self.graph.bind(sequence=args['sequence'],func=args['func'])


    def unbind(self,**args):
        """ Bindings happen only on the graph with the data on it."""
        self.graph.unbind(sequence=args['sequence'])


    def grid(self,**args):
        """ Allow the Frame that the plot gets put on to be gridded into the GUI. """
        self.graphframe.grid(args)
        

    def pack(self,**args):
        """ Allow the Frame that the plot gets put on to be gridded into the GUI. """
        self.graphframe.pack(args)


    def legend_configure(self,hide=1):
        """ This is just for compatability."""
        if hide != 1:
            raise Exception("The legend in this program can only be hidden.")
        pass


    def __init__(self,widget,plotbackground,height,width):
        """ Creates the graph object. You have to pack or grid it yourself. You
            can add bindings onto it however you want. """

        # default axis size
        self.axisSize=50

        self.graphwidth = width  - self.axisSize
        self.graphheight = height - self.axisSize
        self.ylogscale = 0 # can be changed with a call to yaxis_configure

        self.graphframe = Frame(widget)

        self.graph=Canvas(self.graphframe,bg=plotbackground,
                borderwidth=0,highlightthickness=0,
                height=self.graphheight,
                width=self.graphwidth, cursor='crosshair')
        self.graph.grid(row=0,column=1,sticky=N+W)

        # add the 2 axis
        # flip = 1 so positive numbers go up, not down
        self.yaxis= Axis(self.graphframe,
                lowestValue = None, highestValue = None,
                height = self.graphheight, 
                width = self.axisSize, side = "left",
                flip = 1,logscale=self.ylogscale) 
        self.yaxis.grid(row=0,column=0,sticky=N+W+E+S)

        self.xaxis = Axis(self.graphframe,
                lowestValue = None, highestValue = None,
                width = self.graphwidth, 
                height = self.axisSize, side = "bottom")
        self.xaxis.grid(row=1,column=1,sticky=N+W+E+S)

        # Make sure the main image will collapse before anything else
        self.graphframe.grid_rowconfigure(0,weight=1)
        self.graphframe.grid_columnconfigure(1,weight=1)
            
        # allow the graph to be resized
        self.graphframe.bind("<Configure>",self.resize)


if __name__ == "__main__":
    """ Here is a silly program just to test out if the plot is being drawn properly. """

    import Pmw

    top = Tk()
    Label(top,text='This would be the main window').pack()
    root = Pmw.MegaToplevel(top)
    h = root.interior()

    class Main:

        def __init__(self):

            # defaults
            height = 500
            width = 500

            self.logscale = IntVar()
            self.logscale.set(0)

            self.xUpdateName = 'x'
            self.yUpdateName = 'y'

            #coordinates
            botfr=Frame(h)        
            self.xcoord=Label(botfr,text="%s=      " % \
                    self.xUpdateName,width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
            self.ycoord=Label(botfr,text="%s=      " % \
                    self.yUpdateName,width=15,bd=2,relief=RIDGE,anchor=W,fg='red')
            self.ycoord.pack(side=RIGHT,fill=X)
            self.xcoord.pack(side=RIGHT,fill=X)

            self.collog = Checkbutton(botfr,text="Log Scale? ", 
                    variable=self.logscale,command=self.changeLogScale)
            self.collog.pack(side=RIGHT,fill=X)

            botfr.grid(row=1,column=0)

            import LinePlot
            self.plot = LinePlot.LinePlot(h,plotbackground='white',height=height,width=width)
            self.plot.grid(row=0,column=0,sticky=N+W+E+S)

            from math import exp
            xdata = []
            ydata = []
            for index in range(1000):
                xdata.append(index/100.)
                ydata.append(exp(index/100.))

            self.plot.line_create('1',xdata=xdata,ydata=ydata,symbol='',color='red')
            self.plot.line_create('2',xdata=[0,10],ydata=[10,10],symbol='',color='red')
            self.plot.line_create('3',xdata=[0,10],ydata=[100,100],symbol='',color='red')
            self.plot.line_create('4',xdata=[0,10],ydata=[1000,1000],symbol='',color='red')
            self.plot.line_create('5',xdata=[0,10],ydata=[10000,10000],symbol='',color='red')

            root.grid_rowconfigure(0,weight=1)
            root.grid_columnconfigure(0,weight=1)

            self.plot.bind(sequence="<Motion>", func=self.coordreport)
            self.plot.bind(sequence="<Leave>", func=self.nocoordreport)


        def changeLogScale(self):
            self.plot.yaxis_configure(logscale=self.logscale.get())


        def nocoordreport(self,event=None):
            xtext=self.xUpdateName+"="
            ytext=self.yUpdateName+"="
            setstatus(self.xcoord,xtext)
            setstatus(self.ycoord,ytext)


        def coordreport(self,event):
            (x,y)=self.plot.invtransform(event.x,event.y)
            xtext=self.xUpdateName+"="+str(x)
            ytext=self.yUpdateName+"="+str(y)
            xtext=xtext[:12]
            ytext=ytext[:12]
            setstatus(self.xcoord,xtext)
            setstatus(self.ycoord,ytext)
        
    Main()
    root.mainloop()

