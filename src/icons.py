# ============================================================================
# icons.py - Loads icons for Comix.
# ============================================================================

import os
import sys

import gtk

_icons = (('flip-horizontal.png',        'comix-flip-horizontal'),
          ('flip-vertical.png',          'comix-flip-vertical'),
          ('rotate-180.png',             'comix-rotate-180'),
          ('rotate-270.png',             'comix-rotate-270'),
          ('rotate-90.png',              'comix-rotate-90'),
          ('rotate-270-jpeg.png',        'comix-rotate-270-jpeg'),
          ('rotate-90-jpeg.png',         'comix-rotate-90-jpeg'),
          ('flip-horizontal-jpeg.png',   'comix-flip-horizontal-jpeg'),
          ('flip-vertical-jpeg.png',     'comix-flip-vertical-jpeg'),
          ('silk-library.png',           'comix-library'),
          ('silk-library-add.png',       'comix-library-add'),
          ('silk-slideshow.png',         'comix-slideshow'),
          ('silk-bookmarks.png',         'comix-bookmarks'),
          ('silk-desaturate.png',        'comix-desaturate'),
          ('silk-file-operations.png',   'comix-file-operations'),
          ('silk-thumbnails.png',        'comix-thumbnails'),
          ('silk-view.png',              'comix-view'),
          ('silk-zoom.png',              'comix-zoom'),
          ('silk-transform.png',         'comix-transform'),
          ('silk-recent-files.png',      'comix-recent-files'),
          ('silk-edit-bookmarks.png',    'comix-edit-bookmarks'),
          ('silk-toolbars.png',          'comix-toolbars'),
          ('silk-colour-adjust.png',     'comix-colour-adjust'),
          ('lens.png',                   'comix-lens'),
          ('double-page.png',            'comix-double-page'),
          ('manga.png',                  'comix-manga'),
          ('fitscreen.png',              'comix-fitscreen'),
          ('fitwidth.png',               'comix-fitwidth'),
          ('fitheight.png',              'comix-fitheight'),
          ('fitnone.png',                'comix-fitnone'))

def load():
    # Some heuristics to find the path to the icon image files.
    cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
    if os.path.isfile(os.path.join(os.path.dirname(cwd), 'images/comix.png')):
        icon_path = os.path.join(os.path.dirname(cwd), 'images')
    else:
        for prefix in [os.path.dirname(os.path.dirname(sys.argv[0])),
            '/usr', '/usr/local', '/usr/X11R6']:
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
        except:
            continue
    factory.add_default()

