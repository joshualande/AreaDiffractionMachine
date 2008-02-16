# usage: python setup_win_version1.py py2exe
import sys
import os.path
import shutil

sys.path.append(r"..\source\version1")

from distutils.core import setup
import py2exe

def listdirFull(thedir):
    """ This is just os.listdir() but it returns the full path names. """
    files = os.listdir(thedir)
    list = []
    for file in files:
        if file != '.svn':
            list.append(thedir+os.sep+file)
    return list

allXBMS = listdirFull(r"..\source\version1\xbms")
allStandardQ = listdirFull(r"..\source\version1\StandardQ")

setup(name='Area Diffraction Machine',
      version='1',
      description='Analyze x-ray diffraction data.',
      console=[{"script":r"..\source\version1\AreaDiffractionMachine.py",
      "icon_resources":[(1,"LandeBMWIcon.ico")]}],
      data_files = [('.',[r"..\source\version1\colormaps.txt",
                         r"..\source\version1\tips_and_tricks.html"]),
                    ('xbms',allXBMS),
                    ('StandardQ',allStandardQ)])


# console=[r'..\source\version1\AreaDiffractionMachine.py'],
