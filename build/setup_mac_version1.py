import sys
import os.path
import shutil

usage = """Usage: sudo python setup_mac_version1.py py2app --iconfile=landeBMWIcon.icns --version=X.X.X"""

# figure out the version of the program
versionstring = sys.argv.pop()

if versionstring[0:10] != "--version=":
    print usage
    sys.exit(2)

version = versionstring[10:]


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
    name = "Area Diffraction Machine",
    version = "1",
    data_files = [('.',['../source/version1/colormaps.txt']),
                  ('.',['../source/version1/tips_and_tricks.html']),
                  ('xbms',allXBMS),
                  ('StandardQ',allStandardQ)
                 ],
    app=["../source/version1/AreaDiffractionMachine.py"],
    setup_requires=['py2app'],
)

os.popen('sudo rm -rf *.dmg').close()
print "Creating the disk image"
os.popen('sudo mv dist "Area Diffraction Machine v%s"' % version).close()
os.popen('sudo mv "Area Diffraction Machine v%s/Area Diffraction Machine.app" "Area Diffraction Machine v%s/Area Diffraction Machine v%s.app"' % (version,version,version)).close()
os.popen('sudo hdiutil create -srcfolder "Area Diffraction Machine v%s" "Area Diffraction Machine v%s.dmg"' % (version,version) ).close()
os.popen('sudo rm -rf "Area Diffraction Machine v%s"' % version).close()
os.popen('sudo rm -rf "build"').close()
