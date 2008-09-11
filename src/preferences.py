"""preferences.py - Preference handler."""

import os
import cPickle

import gtk

import constants
import labels

# ------------------------------------------------------------------------
# All the preferences are stored here.
# ------------------------------------------------------------------------
prefs = {
    'comment extensions': ['txt', 'nfo'],
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
    'lens magnification': 2,
    'lens size': 200,
    'library cover size': 128,
    'auto add books into collections': True,
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
    'smart bg': False,
    'space scroll percent': 90,
    'store recent file info': True,
    'window height': gtk.gdk.screen_get_default().get_height() * 3 // 4,
    'window width': gtk.gdk.screen_get_default().get_width() // 2
}

_config_path = os.path.join(constants.COMIX_DIR, 'preferences.pickle')
_dialog = None


class _PreferencesDialog(gtk.Dialog):

    def __init__(self, window):
        self._window = window
        gtk.Dialog.__init__(self, _('Preferences'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.connect('response', self._response)
        self.set_has_separator(False)
        self.set_resizable(True)
        self.set_default_response(gtk.RESPONSE_CLOSE)
        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook)
        self.set_border_width(4)
        notebook.set_border_width(6)
        
        # ----------------------------------------------------------------
        # The "Appearance" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(80)
        page.new_section(_('Background'))
        fixed_bg_button = gtk.RadioButton(None, '%s:' %
            _('Use this colour as background'))
        color_button = gtk.ColorButton(gtk.gdk.Color(*prefs['bg colour']))
        page.add_row(fixed_bg_button, color_button)
        dynamic_bg_button = gtk.RadioButton(fixed_bg_button,
            _('Use dynamic background colour.'))
        page.add_row(dynamic_bg_button)

        page.new_section(_('Thumbnails'))
        label = gtk.Label('%s:' % _('Thumbnail size (in pixels)'))
        thumb_size_spinner = gtk.SpinButton()
        thumb_size_spinner.set_range(40, 128)
        page.add_row(label, thumb_size_spinner)
        thumb_number_button = gtk.CheckButton(
            _('Show page numbers on thumbnails.'))
        page.add_row(thumb_number_button)
        
        page.new_section(_('Magnifying Glass'))
        label = gtk.Label('%s:' % _('Magnifying glass size (in pixels)'))
        glass_size_spinner = gtk.SpinButton()
        glass_size_spinner.set_range(40, 400)
        page.add_row(label, glass_size_spinner)
        label = gtk.Label('%s:' % _('Magnification'))
        glass_magnification_spinner = gtk.SpinButton(digits=1)
        glass_magnification_spinner.set_range(1.1, 10.0)
        page.add_row(label, glass_magnification_spinner)
        notebook.append_page(page, gtk.Label(_('Appearance')))
        
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(150)
        page.new_section(_('Behaviour'))
        auto_open_next_button = gtk.CheckButton(
            _('Automatically open the next archive.'))
        page.add_row(auto_open_next_button)
        smart_space_button = gtk.CheckButton(
            _('Use smart space-button scrolling.'))
        page.add_row(smart_space_button)
        label = gtk.Label('%s:' % _('Slideshow delay (in seconds)'))
        delay_spinner = gtk.SpinButton(digits=1)
        delay_spinner.set_range(0.5, 3600.0)
        page.add_row(label, delay_spinner)

        page.new_section(_('Files'))
        store_recent_button = gtk.CheckButton(
            _('Store information about recently opened files.'))
        page.add_row(store_recent_button)
        create_thumbs_button = gtk.CheckButton(
            _('Store thumbnails for opened files.'))
        page.add_row(create_thumbs_button)
        cache_button = gtk.CheckButton(_('Use a cache to speed up reading.'))
        page.add_row(cache_button)

        page.new_section(_('Comments'))
        label = gtk.Label('%s:' % _('Comment extensions'))
        extensions_entry = gtk.Entry()
        page.add_row(label, extensions_entry)
        notebook.append_page(page, gtk.Label(_('Behaviour')))

        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(200)
        page.new_section(_('Defaults'))
        double_page_button = gtk.CheckButton(
            _('Use double page mode by default.'))
        page.add_row(double_page_button)
        fullscreen_button = gtk.CheckButton(_('Use fullscreen by default.'))
        page.add_row(fullscreen_button)
        manga_button = gtk.CheckButton(_('Use manga mode by default.'))
        page.add_row(manga_button)
        label = gtk.Label('%s:' % _('Default zoom mode'))
        zoom_combo = gtk.ComboBox()
        page.add_row(label, zoom_combo)

        page.new_section(_('Fullscreen'))
        hide_in_fullscreen_button = gtk.CheckButton(
            _('Automatically hide all toolbars in fullscreen.'))
        page.add_row(hide_in_fullscreen_button)

        page.new_section(_('Image scaling'))
        stretch_button = gtk.CheckButton(_('Stretch small images.'))
        page.add_row(stretch_button)
        notebook.append_page(page, gtk.Label(_('Display')))
        self.show_all()

    def _response(self, dialog, response):
        _close_dialog()


class _PreferencePage(gtk.VBox):
    
    """The _PreferencePage is a conveniece class for making one "page"
    in a preferences-style dialog that contains one or more
    _PreferenceSections.
    """
    
    def __init__(self, right_column_width):
        """Create a new page where any possible right columns have the
        width request <right_column_width>.
        """
        gtk.VBox.__init__(self, False, 12)
        self.set_border_width(12)
        self._right_column_width = right_column_width
        self._section = None
    
    def new_section(self, header):
        """Start a new section in the page, with the header text from
        <header>.
        """
        self._section = _PreferenceSection(header, self._right_column_width)
        self.pack_start(self._section, False, False)

    def add_row(self, left_item, right_item=None):
        """Add a row to the page (in the latest section), containing one
        or two items. If the left item is a label it is automatically
        aligned properly.
        """
        if isinstance(left_item, gtk.Label):
            left_item.set_alignment(0, 0.5)
        if right_item is None:
            self._section.contentbox.pack_start(left_item)
        else:
            left_box, right_box = self._section.new_split_vboxes()
            left_box.pack_start(left_item)
            right_box.pack_start(right_item)


class _PreferenceSection(gtk.VBox):
    
    """The _PreferenceSection is a convenience class for making one
    "section" of a preference-style dialog, e.g. it has a bold header
    and a number of rows which are indented with respect to that header.
    """
    
    def __init__(self, header, right_column_width=150):
        """Contruct a new section with the header set to the text in
        <header>, and the width request of the (possible) right columns
        set to that of <right_column_width>.
        """
        gtk.VBox.__init__(self, False, 0)
        self._right_column_width = right_column_width
        self.contentbox = gtk.VBox(False, 6)
        label = labels.bold_label(header)
        label.set_alignment(0, 0.5)
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(gtk.HBox(), False, False, 6)
        hbox.pack_start(self.contentbox)
        self.pack_start(label, False, False)
        self.pack_start(hbox, False, False, 6)

    def new_split_vboxes(self):
        """Return two new VBoxes that are automatically put in the section
        after the previously added items. The right one has a width request
        equal to the right_column_width value passed to the class contructor,
        in order to make it easy for  all "right column items" in a page to
        line up nicely.
        """
        left_box = gtk.VBox(False, 6)
        right_box = gtk.VBox(False, 6)
        right_box.set_size_request(self._right_column_width, -1)
        hbox = gtk.HBox(False, 12)
        hbox.pack_start(left_box)
        hbox.pack_start(right_box, False, False)
        self.contentbox.pack_start(hbox)
        return left_box, right_box


def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        _dialog = _PreferencesDialog(window)
    else:
        _dialog.present()


def _close_dialog(*args):
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
            print '! Corrupt preferences file "%s", deleting...' % _config_path
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
