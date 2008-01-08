# ============================================================================
# preferences.py - Preference handler for Comix.
# ============================================================================

import os
import cPickle

import gtk

import constants

# ------------------------------------------------------------------------
# All the preferences are stored here.
# ------------------------------------------------------------------------
prefs = {
    #'auto comments': False,
    'comment extensions': 'txt nfo',
    #'auto load last file': False,
    #'page of last file': 0,
    #'path to last file': '',
    'auto open next archive': True,
    'bg colour': (2100, 2100, 2100),
    'cache': True,
    'stretch': False,
    'default double page': False,
    'default fullscreen': False,
    'default zoom mode': 'fit',  # 'fit', 'width', 'height' or 'manual'
    'default manga mode': False,
    #'emulate double page': False,
    'hide all': False,
    'hide all in fullscreen': True,
    'stored hide all values': (True, True, True, True, True),
    'interp mode': gtk.gdk.INTERP_TILES,
    #'last convert type': 'zip',
    #'lens magnification': 2,
    #'lens size from center': 90,
    #'lens max update interval': 15,
    #'library cover size': 128,
    #'lib window height': gtk.gdk.screen_get_default().get_height() * 3 / 4,
    #'lib window width': gtk.gdk.screen_get_default().get_width() * 3 / 4,
    #'no double page for wide images': True,
    'open defaults to last browsed': True,
    'path of last browsed': os.getenv('HOME'),
    #'default open path': os.getenv('HOME'),
    'show menubar': True,
    'show scrollbar': True,
    'show statusbar': True,
    'show toolbar': True,
    'show thumbnails': True,
    'show page numbers on thumbnails': True,
    'thumbnail size': 80,
    'create thumbnails': True,
    #'slideshow delay': 6.0,
    'smart space scroll': True,
    'space scroll percent': 85,
    #'store recent file info': True,
    'window height': gtk.gdk.screen_get_default().get_height() * 3 / 4, 
    'window width': gtk.gdk.screen_get_default().get_width() / 2
}

_config_path = os.path.join(constants.COMIX_DIR, 'preferences_data')

def read_config_file():
    if os.path.isfile(_config_path):
        try:
            config = open(_config_path)
            version = cPickle.load(config)
            if version < '4.0':
                config.close()
                os.remove(_config_path)
                print 'Removed old incompatible config (version %s).' % version
            else:
                old_prefs = cPickle.load(config)
                config.close()
                for key in old_prefs.iterkeys():
                    if prefs.has_key(key):
                        prefs[key] = old_prefs[key]
        except:
            print '! preferences.py: Error reading or writing', _config_path
            os.remove(_config_path)

def write_config_file():
    config = open(_config_path, 'w')
    cPickle.dump(constants.VERSION, config, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(prefs, config, cPickle.HIGHEST_PROTOCOL)
    config.close()

