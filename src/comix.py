#!/usr/bin/env python

"""Comix - GTK Comic Book Viewer

Copyright (C) 2005-2008 Pontus Ekberg
<herrekberg@users.sourceforge.net>
"""

# -------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# -------------------------------------------------------------------------

import os
import sys
import gettext

import main
import icons
import preferences

# ------------------------------------------------------------------------
# Check for PyGTK and PIL dependencies.
# ------------------------------------------------------------------------
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    assert gtk.gtk_version >= (2, 10, 0)
    assert gtk.pygtk_version >= (2, 10, 0)
except AssertionError:
    print "You don't have the required versions of GTK+ and/or PyGTK installed."
    print 'Installed GTK+ version is: %s' % (
        '.'.join([str(n) for n in gtk.gtk_version]))
    print 'Required GTK+ version is: 2.10.0 or higher\n'
    print 'Installed PyGTK version is: %s' % ( 
        '.'.join([str(n) for n in gtk.pygtk_version]))
    print 'Required PyGTK version is: 2.10.0 or higher'
    sys.exit(1)
except ImportError:
    print 'PyGTK version 2.10.0 or higher is required to run Comix.'
    print 'No version of PyGTK was found on your system.'
    sys.exit(1)

try:
    import Image
    assert Image.VERSION >= '1.1.4'
except AssertionError:
    print "You don't have the required version of the Python Imaging Library"
    print '(PIL) installed.' 
    print 'Installed PIL version is: %s' % Image.VERSION
    print 'Required PIL version is: 1.1.4 or higher'
    sys.exit(1)
except ImportError:
    print 'Python Imaging Library (PIL) 1.1.4 or higher is required.'
    print 'No version of the Python Imaging Library was found on your system.'
    sys.exit(1)


if __name__ == '__main__':
    # --------------------------------------------------------------------
    # Use gettext translations as found in the source dir, otherwise
    # based on the install path.
    # --------------------------------------------------------------------
    exec_path = os.path.abspath(sys.argv[0])
    base_dir = os.path.dirname(os.path.dirname(exec_path))
    if os.path.isdir(os.path.join(base_dir, 'messages')):
        gettext.install('comix', os.path.join(base_dir, 'messages'),
            unicode=True)
    else:
        gettext.install('comix', os.path.join(base_dir, 'share/locale'),
            unicode=True)
    preferences.read_preferences_file()
    icons.load()
    window = main.MainWindow()
    if len(sys.argv) >= 2:
        window.file_handler.open_file(os.path.normpath(sys.argv[1]))
    try:
        gtk.main()
    except KeyboardInterrupt:
        window.terminate_program()

