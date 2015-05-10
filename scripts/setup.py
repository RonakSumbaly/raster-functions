'''
=========================================================
setup.py: Automate installation of dependencies required for Python raster function
=========================================================

Installation
------------
**setup.py** has no external library dependencies and should compile on
most systems that are running Python 2.7, or 3.4.

To execute **setup.py** within the package directory run:
  $ python setup.py
'''

import os
import sys
import subprocess
import time
import urllib2
import logging
import platform

from os.path import join as pjoin

'''
ERRORLEVEL
0 - Installation successful.
1 - pip installation unsuccessful.
2 - HTTP 404 Error URL cannot be found.
3 - File cannot be downloaded.
4 - VC++ Compiler for Python installation unsuccessful.
5 - Python Window Binary installation unsuccessful.
6 - Python package could not be installed.
7 - requirements.txt file not found.
'''


#PATHs
PY_PATH =               sys.executable
PACKAGE_PATH =          os.path.abspath(os.path.dirname(__file__))
MODULE_PATH =           pjoin(PACKAGE_PATH, 'setup.py')
SCRIPT_PATH =           pjoin(os.path.dirname(PY_PATH),'Scripts')
PIP_PATH =              pjoin(SCRIPT_PATH,'pip.exe')
PY_VER2 =               True if sys.version_info[0] == 2 else False

#URLs
PIP_URL =               "http://bootstrap.pypa.io/get-pip.py"
VC_URL =                "http://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi"

# Numpy 1.9.2+ MKL Binaries
NUMPY27_32_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/numpy-1.9.2+mkl-cp27-none-win32.whl"
NUMPY27_64_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/numpy-1.9.2+mkl-cp27-none-win_amd64.whl"
NUMPY34_64_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/numpy-1.9.2+mkl-cp34-none-win_amd64.whl"

# Scipy 0.15.1 Window Binaries
SCIPY27_32_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/scipy-0.15.1-cp27-none-win32.whl"
SCIPY27_64_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/scipy-0.15.1-cp27-none-win_amd64.whl"
SCIPY34_64_URL =        "http://www.lfd.uci.edu/~gohlke/pythonlibs/r7to5k3j/scipy-0.15.1-cp34-none-win_amd64.whl"


def errorHandler(errorLog, errorCode):
    logging.error(errorLog)
    time.sleep(5)
    exit(errorCode)
    

def downloadFile(installURL, installLoc):
    try:
        # Check if URL responses
        URLreq =        urllib2.Request(installURL, headers={'User-Agent': 'Mozilla/5.0'})
        URLopen =       urllib2.urlopen(req)

    except urllib2.HTTPError:
        errorHandler("HTTP 404 URL not found.", 2)

    try:
        # Download file
        fileDownload =  open(installLoc, 'wb')
        fileDownload.write(URLopen.read())
        fileDownload.close()

    except:
        errorHandler("File could not be downloaded.", 3)


def locateFile(installURL, installLoc):
    # Check PACKAGE_PATH for dependencies fle
    if (os.path.isfile(installLoc)):
        print ("Files located. Starting installation.\n")

    else:
        print ("File not found. Downloading file.\n")
        downloadFile(installURL, installLoc)
        print ("File succesfully downloaded. Starting installation.\n")


def main():
    # Install pip
    print ("pip Installation.\n") + ("Locating get-pip.py in ") + PACKAGE_PATH + "\n"

    locateFile(PIP_URL, (PACKAGE_PATH + "\get-pip.py"))

    try:
        subprocess.call([PY_PATH, pjoin(PACKAGE_PATH, 'get-pip.py')])

    except:
        errorHandler("pip installation unsuccessful.", 1)

    if os.path.isfile(PIP_PATH):
        print ("\npip installation successful.\n")

    else:
        errorHandler("pip installation unsuccessful.", 1)

    # Install Microsoft Visual C++ Compiler for Python if PY_VERSION = 2.7
    if PY_VER2:
        # Step 2. Install Microsoft Visual C++ Compiler for Python
        print ("Microsoft Visual C++ Compiler Installation.\n") + ("Locating file in ") + PACKAGE_PATH + "\n"

        locateFile(VC_URL, (PACKAGE_PATH + "\VCForPython.msi"))

        try:
            os.system('msiexec /i VCForPython.msi /qb')
            print "\nInstallation successful.\n"

        except:
            errorHandler("VC++ Compiler for Python installation unsuccessful.", 4)


    # Install Numpy + Scipy using Windows Binaries
    print ("\nNumpy & Scipy Installation.\n") + ("Locating File in ") + PACKAGE_PATH + "\n"

    if PY_VER2:
        if platform.architecture()[0] == "32bit":
            NUMPY_PATH =            (PACKAGE_PATH + "\\numpy-1.9.2+mkl-cp27-none-win32.whl")
            SCIPY_PATH =            (PACKAGE_PATH + "\scipy-0.15.1-cp27-none-win32.whl")

            locateFile(NUMPY27_32_URL, NUMPY_PATH)
            locateFile(SCIPY27_32_URL, SCIPY_PATH)

        else:
            NUMPY_PATH =            (PACKAGE_PATH + "\\numpy-1.9.2+mkl-cp27-none-win_amd64.whl")
            SCIPY_PATH =            (PACKAGE_PATH + "\scipy-0.15.1-cp27-none-win_amd64.whl")

            locateFile(NUMPY27_64_URL, NUMPY_PATH)
            locateFile(SCIPY27_64_URL, SCIPY_PATH)

    else:
        NUMPY_PATH =                (PACKAGE_PATH + "\\numpy-1.9.2+mkl-cp34-none-win_amd64.whl")
        SCIPY_PATH =                (PACKAGE_PATH + "\scipy-0.15.1-cp34-none-win_amd64.whl.whl")

        locateFile(NUMPY34_64_URL, NUMPY_PATH)
        locateFile(SCIPY34_64_URL, SCIPY_PATH)

    try:
        subprocess.call([PIP_PATH, 'install','-U','--upgrade', NUMPY_PATH])
        subprocess.call([PIP_PATH, 'install','-U','--upgrade', SCIPY_PATH])

    except:
        errorHandler("Python Windows Binaries could not be installed.", 5)


    # Install Python Dependencies
    print ("\nInstall Python Dependencies.\n") +("Locating requirements.txt in ") + PACKAGE_PATH + "\n"

    if (os.path.isfile((PACKAGE_PATH + "\\requirements.txt"))):
        install_require = [line.strip() for line in open((PACKAGE_PATH + "\\requirements.txt"))]

        for package in install_require:
            print ("Installing ") + package + (" package.\n")

            try:
                subprocess.call([PIP_PATH, 'install','-U','--upgrade', package])

            except:
                errorHandler(("Error: " + package + " could not be downloaded."), 6)

            print package + (" successfully installed.\n")
            time.sleep(2)

    else:
        errorHandler("requirements.txt not found.", 7)

    print ("Installation successful.\n")
    time.sleep(5)
    exit(0)


if __name__ == '__main__':
    main()
