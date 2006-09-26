#!/usr/bin/env python

import os
import sys
import getopt
import shutil

usage_info = """
This script installs or uninstalls Comix on your system.
If you encounter any bugs, please report them to herrekberg@users.sf.net.

--------------------------------------------------------------------------------

Usage:

 ./install.py install              ---      Install to /usr/local

 ./install.py uninstall            ---      Uninstall from /usr/local

--------------------------------------------------------------------------------

Options:

 --installdir <directory>          ---      Install or uninstall in <directory>
                                            instead of /usr/local

 --no-mime                         ---      Do not install Nautilus thumbnailer
                                            or register new mime types for
                                            x-cbz, x-cbt and x-cbr archive
                                            files.

 --no-balloon                      ---      Nautilus thumbnailer does not
                                            imprint a balloon on the thumbnails
                                            by default.
"""

def info():
    print usage_info
    sys.exit(1)

def install(src, dst):
    try:
        dst = os.path.join(install_dir, dst)
        assert os.path.isfile(src)
        assert not os.path.isdir(dst)
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy(src, dst)
        print "Installed", dst
    except:
        print "Error while installing", dst

def uninstall(path):
    try:
        path = os.path.join(install_dir, path)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return
        print "Removed", path
    except:
        print "Error while removing", path

def check_dependencies():
    required_found = True
    recommended_found = True
    print "Checking dependencies..."
    print
    print "Required dependencies:"
    print
    # Should also check the PyGTK version. To do that we have to load the
    # gtk module though, which normally can't be done while using `sudo`.
    try:
        import pygtk
        print "    PyGTK ........................ OK"
    except ImportError:
        print "    !!! PyGTK .................... Not found"
        required_found = False
    try:
        import Image
        assert Image.VERSION >= "1.1.4"
        print "    Python Imaging Library ....... OK"
    except ImportError:
        print "    !!! Python Imaging Library ... Not found"
        required_found = False
    except AssertionError:
        print "    !!! Python Imaging Library ... version", Image.VERSION,
        print "found"
        print "    !!! Python Imaging Library 1.1.4 or higher is required"
        required_found = False
    print "\nRecommended dependencies:\n"
    # rar/unrar is only a requirement to read RAR (.cbr) files.
    rar = False
    for path in os.getenv("PATH").split(":"):
        if (os.path.isfile(os.path.join(path, "unrar")) or
            os.path.isfile(os.path.join(path, "rar"))):
            print "    rar/unrar .................... OK"
            rar = True
            break
    if not rar:
        print "    !!! rar/unrar ................ Not found"
        recommended_found = False
    # jpegtran is only a requirement to rotate JPEG files.
    jpegtran = False
    for path in os.getenv("PATH").split(":"):
        if os.path.isfile(os.path.join(path, "jpegtran")):
            print "    jpegtran ..................... OK"
            jpegtran = True
            break
    if not jpegtran:
        print "    !!! jpegtran ................. Not found"
        recommended_found = False
    if not required_found:
        print
        print "Could not find all required dependencies!"
        print "Please install them and try again."
        print
        sys.exit(1)
    if not recommended_found:
        print
        print "Note that not all recommeded dependencies were found."
        print "Comix has still been installed, but it will not be able to"
        print "use all it's functions."
    print




install_dir = "/usr/local/"
no_mime = False
no_balloon = False
ISO_CODES = \
    ("sv", "es", "zh_CN", "zh_TW", "pt_BR", "de", "it", "nl", "fr", "pl",
    "el", "ca")

try:
    opts, args = \
        getopt.gnu_getopt(sys.argv[1:], "",
        ["installdir=", "no-mime", "no-balloon"])
except getopt.GetoptError:
    info()
for opt, value in opts:
    if opt == "--installdir":
        install_dir = value
        if not os.path.isdir(install_dir):
            print "\n*** Error:", install_dir, "does not exist.\n" 
            info()
    elif opt == "--no-mime":
        no_mime = True
    elif opt == "--no-balloon":
        no_balloon = True

if args == ["install"]:
    check_dependencies()
    print "Installing Comix in", install_dir, "...\n"
    install("comix", "bin/comix")
    install("comix.1.gz", "share/man/man1/comix.1.gz")
    install("comix.desktop", "share/applications/comix.desktop")
    install("images/logo/comix.png", "share/pixmaps/comix.png")
    install("images/logo/comix.png", "share/icons/hicolor/48x48/apps/comix.png")
    install("images/logo/comix.svg",
        "share/icons/hicolor/scalable/apps/comix.svg")
    print 'Installed some spam'
    for imagefile in os.listdir('images'):
        if os.path.isfile(os.path.join('images', imagefile)):
            install(os.path.join('images', imagefile),
                os.path.join('share/pixmaps/comix', imagefile))
    for lang in ISO_CODES:
        install("messages/" + lang + "/LC_MESSAGES/comix.mo",
            "share/locale/" + lang + "/LC_MESSAGES/comix.mo")
    if not no_mime:
        install("mime/comicthumb", "bin/comicthumb")
        install("mime/comicthumb.1.gz", "share/man/man1/comicthumb.1.gz")
        install("mime/comix.xml", "share/mime/packages/comix.xml")
        os.popen("update-mime-database '" + 
            os.path.join(install_dir, "share/mime'"))
        print
        print "Updated mime database."
        schemas = \
            no_balloon and "comicbook-no-balloon.schemas" or "comicbook.schemas"
        os.popen("export GCONF_CONFIG_SOURCE=`gconftool-2 "
                 "--get-default-source 2>/dev/null` && gconftool-2 "
                 "--makefile-install-rule ./mime/%s 2>/dev/null" % schemas)
        print
        print "Registered comic archive thumbnailer in gconf (if available)."
        print "The thumbnailer is at this point supported by Nautilus only."
        print "You have to restart Nautilus before it is activated."
elif args == ["uninstall"]:
    print "Uninstalling Comix from", install_dir, "...\n"
    uninstall("bin/comix")
    uninstall("share/man/man1/comix.1.gz")
    uninstall("share/applications/comix.desktop")
    uninstall("share/pixmaps/comix.png")
    uninstall("share/icons/hicolor/48x48/apps/comix.png")
    uninstall("share/icons/hicolor/scalable/apps/comix.svg")
    uninstall("share/pixmaps/comix")
    uninstall("bin/comicthumb")
    uninstall("share/man/man1/comicthumb.1.gz")
    uninstall("share/mime/packages/comix.xml")
    for lang in ISO_CODES:
        uninstall("share/locale/" + lang + "/LC_MESSAGES/comix.mo")
    uninstall("/tmp/comix")
    print
    print "There might still be files in ~/.comix/ left on your system."
    print "Please remove that directory manually if you do not plan to"
    print "install Comix again later."
    
else:
    info()

