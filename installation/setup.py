import sys
import subprocess
import os
import struct

def install_lxml():
    """
    Install LXML from local binaries
    (I couldn't install the one on the web)
    :return:
    """
    print "Install LXML"
    if 8 * struct.calcsize("P") == 32:
        pip.main(['install', os.path.join(dir_name, "lxml-3.6.1-cp27-cp27m-win32.whl")])
    else:
        pip.main(['install', os.path.join(dir_name, "lxml-3.6.1-cp27-cp27m-win_amd64.whl")])
    try:
        import lxml
        print "Done"
    except ImportError:
        print "Could not install"

def install_pip():
    """
    Install latest version of pip from the web
    Since Python 2.7.9 PIP should be shipped by with the python install.
    This step should normally not be necessary.
    :return:
    """
    print "Install PIP"
    paths = sys.path
    for path in paths:
        p = path.split("\\")
    if len(p) == 3 and "Python" in p[1] and "ArcGIS" in [2]:

        process = subprocess.Popen([os.path.join(path, "python.exe"), os.path.join(dir_name, "get-pip.py")],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        print out

if __name__ == "__main__":

    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)

    try:
        import lxml
        print "All extensions already installed"
    except ImportError:
        try:
            import pip
            install_lxml()
        except ImportError:
            install_pip()
            try:
                import pip
                install_lxml()
            except ImportError:
                "Could not install pip."
    try:
        import lxml
        print "Installed lxml successfully"
    except ImportError:
        "Could not install lxml"
    input("Press Enter to continue...")