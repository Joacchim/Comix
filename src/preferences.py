"""preferences.py - Preference handler."""

import os
import cPickle

import gtk

import constants

# ------------------------------------------------------------------------
# All the preferences are stored here.
# ------------------------------------------------------------------------
prefs = {
    #'auto comments': False,
    'comment extensions': ['txt',  'nfo'],
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
    'hide all': False,
    'hide all in fullscreen': True,
    'stored hide all values': (True, True, True, True, True),
    #'last convert type': 'zip',
    'lens magnification': 2,
    'lens size': 180,
    'library cover size': 128,
    'lib window height': gtk.gdk.screen_get_default().get_height() * 3 // 5,
    'lib window width': gtk.gdk.screen_get_default().get_width() * 2 // 3,
    'last library collection': None,
    #'no double page for wide images': True,
    'path of last browsed': os.getenv('HOME'),
    'show menubar': True,
    'show scrollbar': True,
    'show statusbar': True,
    'show toolbar': True,
    'show thumbnails': True,
    'show page numbers on thumbnails': True,
    'thumbnail size': 80,
    'create thumbnails': True,
    'slideshow delay': 3000,
    'smart space scroll': True,
    'space scroll percent': 90,
    'store recent file info': True,
    'window height': gtk.gdk.screen_get_default().get_height() * 3 // 4, 
    'window width': gtk.gdk.screen_get_default().get_width() // 2
}

_config_path = os.path.join(constants.COMIX_DIR, 'preferences.pickle')
_dialog = None

class _PreferencesDialog(gtk.Dialog):
    
    #XXX: Incomplete

    def __init__(self, window):
        self._window = window
        gtk.Dialog.__init__(self, _('Preferences'), window, 0,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK,
            gtk.RESPONSE_OK))
        self.connect('response', self._response)
        self.set_has_separator(False)
        self.set_resizable(True)
        self.set_default_response(gtk.RESPONSE_OK)
        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook)
        self.set_border_width(4)
        notebook.set_border_width(6)
        
        page = gtk.VBox(False, 12)

        self.show_all()

    def _response(self, dialog, response):
        if response == gtk.RESPONSE_CANCEL:
            print 'cancel'
        elif response == gtk.RESPONSE_OK:
            print 'ok'
        elif response == gtk.RESPONSE_DELETE_EVENT:
            print 'close'
        close_dialog()


def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        _dialog = _PreferencesDialog(window)

def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None

def read_preferences_file():
    """Read preferences data from disk."""
    if os.path.isfile(_config_path):
        try:
            config = open(_config_path)
            version = cPickle.load(config)
            old_prefs = cPickle.load(config)
            config.close()
        except Exception:
            print '! Error in preferences file "%s", deleting...' % _config_path
            os.remove(_config_path)
        else:
            for key in old_prefs:
                if key in prefs:
                    prefs[key] = old_prefs[key]

def write_preferences_file():
    """Write preference data to disk."""
    config = open(_config_path, 'w')
    cPickle.dump(constants.VERSION, config, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(prefs, config, cPickle.HIGHEST_PROTOCOL)
    config.close()

