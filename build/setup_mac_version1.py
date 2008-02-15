# Usage: sudo python setup_mac_version1.py py2app --iconfile=landeBMWIcon.icns
import sys
import os.path
import shutil

def listdirFull(thedir):
    """ This is just os.listdir() but it returns the full path names. """
    files = os.listdir(thedir)
    for loop in range(len(files)):
        files[loop] = thedir+os.sep+files[loop]
    return files

allXBMS = listdirFull(r"../source/version1/xbms")
allStandardQ = listdirFull(r"../source/version1/StandardQ")

from setuptools import setup,Extension

setup(
    data_files = [('.',['../source/version1/colormaps.txt']),
                  ('xbms',allXBMS),
                  ('StandardQ',allStandardQ)
                 ],
    app=["../source/version1/AreaDiffractionMachine.py"],
    setup_requires=['py2app'],
)