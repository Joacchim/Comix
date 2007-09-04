# ============================================================================
# icons.py
#
# This module is a part of Comix. <http://comix.sourceforge.net/>
# 
# Version: $Revision$
# ============================================================================
import os
import sys

import gtk

# Some heuristics to find the path to the image files.
cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
if os.path.isfile(os.path.join(os.path.dirname(cwd), 'images/lens.png')):
    icon_path = os.path.join(os.path.dirname(cwd), 'images')
else:
    for prefix in [os.path.dirname(os.path.dirname(sys.argv[0])),
        '/usr', '/usr/local', '/usr/X11R6']:
        if os.path.isfile(os.path.join(prefix,
            'share/pixmaps/comix/lens.png')): # Try one
            icon_path = os.path.join(prefix, 'share/pixmaps/comix')
            break
try:
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'comix.png'))
    gtk.window_set_default_icon(pixbuf)

    factory = gtk.IconFactory()
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'flip-horizontal.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-flip-horizontal', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'flip-vertical.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-flip-vertical', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'rotate-180.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-rotate-180', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'rotate-270.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-rotate-270', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'rotate-90.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-rotate-90', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'rotate-90-jpeg.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-rotate-90-jpeg', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'rotate-270-jpeg.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-rotate-270-jpeg', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'flip-horizontal-jpeg.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-flip-horizontal-jpeg', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'flip-vertical-jpeg.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-flip-vertical-jpeg', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-library.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-library', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-library-add.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-library-add', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-slideshow.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-slideshow', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-bookmarks.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-bookmarks', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-desaturate.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-desaturate', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-file-operations.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-file-operations', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-thumbnails.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-thumbnails', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-view.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-view', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-zoom.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-zoom', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-transform.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-transform', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-recent-files.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-recent-files', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-edit-bookmarks.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-edit-bookmarks', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-toolbars.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-toolbars', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'silk-colour-adjust.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-colour-adjust', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'lens.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-lens', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'double-page.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-double-page', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'manga.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-manga', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'fitscreen.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-fitscreen', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'fitwidth.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-fitwidth', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'fitheight.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-fitheight', iconset)
    pixbuf = \
        gtk.gdk.pixbuf_new_from_file(
        os.path.join(icon_path, 'fitnone.png'))
    iconset = gtk.IconSet(pixbuf)
    factory.add('comix-fitnone', iconset)
    factory.add_default()
except:
    print 'Could not load icons.'
    print

