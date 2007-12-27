#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 -------------------------------------------------------------------------

 Comix 4.0dev - GTK Comic Book Viewer

 Copyright (C) 2005-2007 Pontus Ekberg
 <herrekberg@users.sourceforge.net>

 -------------------------------------------------------------------------

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

 -------------------------------------------------------------------------
"""

import os
import sys
import gettext

import main

# ------------------------------------------------------------------------
# Check for PyGTK and PIL dependencies.
# ------------------------------------------------------------------------
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    assert gtk.gtk_version >= (2, 8, 0)
    assert gtk.pygtk_version >= (2, 8, 0)
except AssertionError:
    print (
    'You do not have the required versions of GTK+ and/or PyGTK installed.\n\n'
    'Installed GTK+ version is ' + 
    '.'.join([str(n) for n in gtk.gtk_version]) + '\n' +
    'Required GTK+ version is 2.8.0 or higher\n\n'
    'Installed PyGTK version is ' + 
    '.'.join([str(n) for n in gtk.pygtk_version]) + '\n' +
    'Required PyGTK version is 2.8.0 or higher')
    sys.exit(1)
except:
    print 'PyGTK version 2.8.0 or higher is required to run Comix.'
    print 'No version of PyGTK was found on your system.'
    sys.exit(1)

try:
    import Image
    assert Image.VERSION >= '1.1.4'
except AssertionError:
    print (
    'You do not have the required version of the Python Imaging Library (PIL) '
    'installed.\n\n' + 
    'Installed Python Imaging Library version is ' + Image.VERSION + '\n' +
    'Required Python Imaging Library version is 1.1.4 or higher')
    sys.exit(1)
except:
    print 'Python Imaging Library 1.1.4 or higher is required to run Comix.'
    print 'No version of the Python Imaging Library was found on your system.'
    sys.exit(1)


if __name__ == '__main__':
    
    # --------------------------------------------------------------------
    # Use gettext translations as found in the source dir, otherwise
    # based on the install path.
    # --------------------------------------------------------------------
    exec_path = os.path.realpath(sys.argv[0])
    base_dir = os.path.dirname(os.path.dirname(exec_path))
    if os.path.isdir(os.path.join(base_dir, 'messages')):
        gettext.install('comix', os.path.join(base_dir, 'messages'),
            unicode=True)
    else:
        gettext.install('comix', os.path.join(base_dir, '/share/locale'),
            unicode=True)
    
    main.MainWindow()
    gtk.main()

