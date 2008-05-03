import sys
import os
import shutil


usage = """Usage: python setup_win_version2.py py2exe --version=X.X.X"""

# figure out the version of the program
versionstring = sys.argv.pop()

if versionstring[0:10] != "--version=":
    print usage
    sys.exit(2)
version = versionstring[10:]


sys.path.append(r"..\source\version2")

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

allXBMS = listdirFull(r"..\source\version2\xbms")
allStandardQ = listdirFull(r"..\source\version2\StandardQ")

setup(name='Area Diffraction Machine',
      version=version,
      description='Analyze x-ray diffraction data.',
      console=[{"script":r"..\source\version2\AreaDiffractionMachine.py",
      "icon_resources":[(1,"LandeBMWIcon.ico")]}],
      data_files = [('.',[r"..\source\version2\colormaps.txt",
                          r"..\source\ChangeLog.txt",
                         r"..\source\version2\tips_and_tricks.html"]),
                    ('xbms',allXBMS),
                    ('StandardQ',allStandardQ)])


print 'clean up directory'
os.popen('RMDIR /s /q build')
os.popen('del /s "Area Diffraction Machine v*"')
os.popen('move dist "Area Diffraction Machine v%s"' % version)
os.popen('move "Area Diffraction Machine v%s\AreaDiffractionMachine.exe" "Area Diffraction Machine v%s\Area Diffraction Machine v%s.exe"' % (version,version,version))
print 'zipping up the folder'
os.popen('zip -r "Area Diffraction Machine v%s.zip" "Area Diffraction Machine v%s"' % (version,version))
os.popen('RMDIR /s /q "Area Diffraction Machine v%s"' % (version))
