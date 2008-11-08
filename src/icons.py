"""icons.py - Load Comix specific icons."""

import os
import sys

import gtk

_icons = (('gimp-flip-horizontal.png',   'comix-flip-horizontal'),
          ('gimp-flip-vertical.png',     'comix-flip-vertical'),
          ('gimp-rotate-180.png',        'comix-rotate-180'),
          ('gimp-rotate-270.png',        'comix-rotate-270'),
          ('gimp-rotate-90.png',         'comix-rotate-90'),
          ('gimp-thumbnails.png',        'comix-thumbnails'),
          ('gimp-transform.png',         'comix-transform'),
          ('tango-enhance-image.png',    'comix-enhance-image'),
          ('tango-add-bookmark.png',     'comix-add-bookmark'),
          ('tango-archive.png',          'comix-archive'),
          ('tango-image.png',            'comix-image'),
          ('library.png',                'comix-library'),
          ('comments.png',               'comix-comments'),
          ('zoom.png',                   'comix-zoom'),
          ('lens.png',                   'comix-lens'),
          ('double-page.png',            'comix-double-page'),
          ('manga.png',                  'comix-manga'),
          ('fitscreen.png',              'comix-fitscreen'),
          ('fitwidth.png',               'comix-fitwidth'),
          ('fitheight.png',              'comix-fitheight'),
          ('fitmanual.png',              'comix-fitmanual'))

# Some heuristics to find the path to the icon image files.
base = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
if os.path.isfile(os.path.join(base, 'images/comix.png')): # Source dir
    icon_path = os.path.join(base, 'images')
else: # Installed in some system dir
    for prefix in [base, '/usr', '/usr/local', '/usr/X11R6']:
        if os.path.isfile(os.path.join(prefix,
            'share/pixmaps/comix/comix.png')): # Try one
            icon_path = os.path.join(prefix, 'share/pixmaps/comix')
            break

pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(icon_path, 'comix.png'))
gtk.window_set_default_icon(pixbuf)
factory = gtk.IconFactory()
for filename, stockid in _icons:
    try:
        filename = os.path.join(icon_path, filename)
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        iconset = gtk.IconSet(pixbuf)
        factory.add(stockid, iconset)
    except Exception:
        print '! Could not load icon "%s".' % stockid
factory.add_default()
