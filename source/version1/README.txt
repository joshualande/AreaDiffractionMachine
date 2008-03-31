In order to get Pmw to work with py2exe, I had to freeze it into the current folder. This is described at http://pmw.sourceforge.net/doc/dynamicloader.html. In particular, I had to copy the files PmwBlt.py and PmwColor.py into the current folder. I then had to run the following command from inside the current folder.
    
    python "C:\Program Files\Python21\Pmw\Pmw_1_2\bin\bundlepmw.py" "C:\Program Files\Python21\Pmw\Pmw_1_2\bin" 

This command created the file Pmw.py inside of the current folder which could be used to include Pmw ih py2exe. This ne Pmw file can now be imported as "import Pmw" and py2exe will be happy. The only problem is that python gets confused about which Pmw.py I am trying to import. To fix this problem, I renamed this file to PmwFreeze.py. I then issued the command inside of my program "import PmwFreeze as Pmw" and it uniquely includes the right frozen Pmw. This lets me have Pmw widgets inside of an py2exe executable!

On the mac, PmwFreeze.py was giving me this silly error:

    File "/Users/jolande/xrd work/areadiffractionmachine/source/version1/PmwFreeze.py", line 1814, in _reporterror
    msg = exc_type + ' Exception in Tk callback\n'

So, I changed the line to:

    msg = str(exc_type) + ' Exception in Tk callback\n'

And everything worked after that.

---------------------------

getting BLT to work with Pmw was even sketchyer. In particular, I had to use sam's blt install: blt24z-for-tcl83.exe. This ended up installing the Blt stuff inside of C:/program files/Tcl. I then followed the instructions on: http://heim.ifi.uio.no/~hpl/Pmw.Blt/doc/links.html. This site was down so I used the google cache of it. The dude's advice for getting BLt to work was

    *   Getting Pmw.Blt to work on Windows machines.  Some users have had a problem with importing the Pmw.Blt widget on Windows systems. Here is a recipe collected from Python newsgroup messages by Peter Brown at phbrown@acm.org:
         1. Install BLT 2.4u into C:/Python20/tcl, using BLT's installer (the one for Tcl/Tk 8.3). This gives you bin, include, and lib subdirectories of C:/Python20/tcl, with all the BLT stuff in them.
         2. Copy C:/Python20/tcl/lib/blt2.4 into C:/Python20/tcl/tcl8.3.
         3. Put the BLT DLLs in a directory on your PATH (not necessarilly a system directory, it just has to be on your PATH) 


So, what I really did was copy my C:\Program Files\Tcl\lib\blt2.4 into my C:\program files\python21\tcl\tcl8.3 folder. I then copied C:\Program Files\Tcl\bin\BLT24.dll into this current build folder and blt finally worked. Note that when you build the program into an application using py2exe, you have to explicitly copy the BLT24.dll file into the folder with the executable in it.
