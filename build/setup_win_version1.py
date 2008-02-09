import sys
import os.path
import shutil

sys.path.append(r"..\source\version1")

from distutils.core import setup
import py2exe

def listdirFull(thedir):
    """ This is just os.listdir() but it returns the full path names. """
    files = os.listdir(thedir)
    for loop in range(len(files)):
        files[loop] = thedir+os.sep+files[loop]
    return files

allXBMS = listdirFull(r"..\source\version1\xbms")
allStandardQ = listdirFull(r"..\source\version1\StandardQ")

setup(name='',
      description="",
      version='1',
      scripts=[r'..\source\version1\AreaDiffractionMachine.py'],
      data_files = [('.',[r"..\source\version1\colormaps.txt",
                         r"..\source\version1\BLT24.dll",
                         r"..\source\version1\tix8183.dll",
                         r"..\source\version1\tips_and_tricks.html"]),
                    ('xbms',allXBMS),
                    ('StandardQ',allStandardQ)])

if not os.path.exists(r"dist\AreaDiffractionMachine\tcl\tix8.1"):
    # if you are building the program somewhere else,
    # you might need to copy tix8.1 from somewhere else.
    shutil.copytree(r"C:\Program Files\Python21\tcl\tix8.1",
    r"dist\AreaDiffractionMachine\tcl\tix8.1")

