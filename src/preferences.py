import os
import cPickle

import gtk

# =======================================================
# All the preferences are stored here.
# =======================================================
prefs = {
    'auto comments': False,
    'autocontrast': False,
    'auto load last file': False,
    'blue bg': 2100,
    'brightness': 1.0,
    'cache': True,
    'comment extensions': 'txt nfo',
    'contrast': 1.0,
    'default double page': False,
    'default fullscreen': False,
    'default open path': os.getenv('HOME'), #XXX: remove?
    'default zoom mode': 'fit', # fit, width, height or manual
    'default manga mode': False,
    'emulate double page': False,
    'go to next archive': True,
    'green bg': 2100,
    'hide all': False,
    'hide all in fullscreen': True,
    'interp mode': gtk.gdk.INTERP_TILES,
    'last convert type': 'zip',
    'lens magnification': 2,
    'lens size from center': 90,
    'library cover size': 128, #XXX: remove?
    'lib window height': gtk.gdk.screen_get_default().get_height() * 3 / 4,
    'lib window width': gtk.gdk.screen_get_default().get_width() * 3 / 4,
    'max lens update interval': 15,
    'no double page for wide images': True, #XXX: not implemented
    'open defaults to last browsed': True,
    'page of last file': 0,
    'path of last browsed': os.getenv('HOME'),
    'path to last file': '',
    'red bg': 2100,
    'saturation': 1.0,
    'save image adjustments': False, #XXX: remove?
    'save window pos': True,
    'sharpness': 1.0,
    'show menubar': True,
    'show page numbers on thumbnails': True,
    'show scrollbar': True,
    'show statusbar': True,
    'show thumbnails': True,
    'show toolbar': True,
    'slideshow delay': 6.0,
    'smart space scroll': True,
    'space scroll length': 85,
    'space scroll type': 'window', # window or image
    'stored hide all values': (True, True, True, True, True),
    'store recent file info': True,
    'stretch': False,
    'thumbnail size': 80,
    'toolbar style': gtk.TOOLBAR_ICONS,
    'use freedesktop thumbnails': True,
    'window height': gtk.gdk.screen_get_default().get_height() * 3 / 4, 
    'window width': gtk.gdk.screen_get_default().get_width() / 2,
    'window x': 50,
    'window y': 50
}

config_path = os.path.join(os.environ['HOME'], '.comix/preferences_data')

# =======================================================
# Parse preferences_data file.
# =======================================================
if os.path.isfile(config_path):
    try:
        config = open(config_path)
        version = cPickle.load(config)
        if version < '4.0':
            config.close()
            os.remove(config_path)
            print 'Removed outdated config data (version %s).' % version
        else:
            prefs.update(cPickle.load(config))
    except:
        print 'preferences.py: Error reading or writing', config_path

