"""filechooser.py - Custom FileChooserDialog implementation."""

import os

import gtk
import pango

import image
from preferences import prefs
import thumbnail

_main_filechooser_dialog = None
_library_filechooser_dialog = None


class _ComicFileChooserDialog(gtk.Dialog):

    """We roll our own FileChooserDialog because the one in GTK is buggy
    with the preview widget. This is a base class for the
    _MainFileChooserDialog and the _LibraryFileChooserDialog.
    """

    def __init__(self):
        gtk.Dialog.__init__(self, _('Open'), None, 0, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_has_separator(False)

        self.filechooser = gtk.FileChooserWidget()
        self.filechooser.set_size_request(680, 420)
        self.vbox.pack_start(self.filechooser)
        self.set_border_width(4)
        self.filechooser.set_border_width(6)
        self.filechooser.connect('file-activated', self._response,
            gtk.RESPONSE_OK)

        preview_box = gtk.VBox(False, 10)
        preview_box.set_size_request(130, 0)
        self._preview_image = gtk.Image()
        self._preview_image.set_size_request(130, 130)
        preview_box.pack_start(self._preview_image, False, False)
        self.filechooser.set_preview_widget(preview_box)
        self._namelabel = gtk.Label()
        self._namelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self._namelabel, False, False)
        self._sizelabel = gtk.Label()
        self._sizelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self._sizelabel, False, False)
        self.filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self.filechooser.connect('update-preview', self._update_preview)

        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(_('All files'))
        self.filechooser.add_filter(ffilter)

        self.add_filter(_('All Archives'), 'application/x-zip application/zip '
            'application/x-rar application/x-tar application/x-gzip '
            'application/x-bzip2 application/x-cbz application/x-cbr '
            'application/x-cbt')
        self.add_filter(_('Zip archives'),
            'application/x-zip application/zip application/x-cbz')
        self.add_filter(_('RAR archives'),
            'application/x-rar application/x-cbr')
        self.add_filter(_('tar archives'),
            'application/x-tar application/x-gzip '
            'application/x-bzip2 application/x-cbt')

        self.filechooser.set_current_folder(prefs['path of last browsed'])
        self.show_all()

    def add_filter(self, name, mimes):
        """Add a filter for <mimes> called <name> to the filechooser."""
        ffilter = gtk.FileFilter()
        for mime in mimes.split():
            ffilter.add_mime_type(mime)
        ffilter.set_name(name)
        self.filechooser.add_filter(ffilter)

    def handle_response(self, response):
        """Return a list of the paths of the chosen files, or None if the 
        event only changed the current directory."""
        if response == gtk.RESPONSE_OK:
            paths = self.filechooser.get_filenames()
            if len(paths) == 1 and os.path.isdir(paths[0]):
                self.filechooser.set_current_folder(paths[0])
                return None
            prefs['path of last browsed'] = \
                self.filechooser.get_current_folder()
            return paths
        return []

    def _update_preview(self, *args):
        path = self.filechooser.get_preview_filename()
        if path and os.path.isfile(path):
            pixbuf = thumbnail.get_thumbnail(path, prefs['create thumbnails'])
            if pixbuf is None:
                self._preview_image.clear()
                self._namelabel.set_text('')
                self._sizelabel.set_text('')
            else:
                pixbuf = image.add_border(pixbuf, 1)
                self._preview_image.set_from_pixbuf(pixbuf)
                self._namelabel.set_text(os.path.basename(path))
                self._sizelabel.set_text(
                    '%.1f KiB' % (os.stat(path).st_size / 1024.0))
                attrlist = pango.AttrList()
                attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                    len(self._namelabel.get_text())))
                attrlist.insert(pango.AttrSize(8000, 0,
                    len(self._namelabel.get_text())))
                self._namelabel.set_attributes(attrlist)
                attrlist = pango.AttrList()
                attrlist.insert(pango.AttrSize(8000, 0,
                    len(self._sizelabel.get_text())))
                self._sizelabel.set_attributes(attrlist)
        else:
            self._preview_image.clear()
            self._namelabel.set_text('')
            self._sizelabel.set_text('')


class _MainFileChooserDialog(_ComicFileChooserDialog):
    
    """The normal FileChooserDialog used with the 'Open' menu item."""
    
    def __init__(self, file_handler):
        _ComicFileChooserDialog.__init__(self)
        self._file_handler = file_handler
        self.connect('response', self._response)

        ffilter = gtk.FileFilter()
        ffilter.add_pixbuf_formats()
        ffilter.set_name(_('All images'))
        self.filechooser.add_filter(ffilter)
        self.add_filter(_('JPEG images'), 'image/jpeg')
        self.add_filter(_('PNG images'), 'image/png')

    def _response(self, widget, response):
        paths = super(_MainFileChooserDialog, self).handle_response(response)
        if paths is None:
            return
        _close_main_filechooser_dialog()
        if paths:
            self._file_handler.open_file(paths[0])

    
class _LibraryFileChooserDialog(_ComicFileChooserDialog):
    
    """The library FileChooserDialog used when adding books to the library."""
    
    def __init__(self, library):
        _ComicFileChooserDialog.__init__(self)
        self._library = library
        self.filechooser.set_select_multiple(True)
        self.filechooser.connect('current-folder-changed',
            self._set_collection_name)
        self.connect('response', self._response)
        
        self._collection_button = gtk.CheckButton(
            '%s:' % _('Automatically add the books to this collection'), False)
        self._collection_button.set_active(
            prefs['auto add books into collections'])
        self._comboentry = gtk.combo_box_entry_new_text()
        self._comboentry.child.set_activates_default(True)
        for collection in self._library.backend.get_all_collections():
            name = self._library.backend.get_collection_name(collection)
            self._comboentry.append_text(name)
        collection_box = gtk.HBox(False, 6)
        collection_box.pack_start(self._collection_button, False, False)
        collection_box.pack_start(self._comboentry, True, True)
        collection_box.show_all()
        self.filechooser.set_extra_widget(collection_box)
    
    def _set_collection_name(self, *args):
        """Set the text in the ComboBoxEntry to the name of the current
        directory.
        """
        name = os.path.basename(self.filechooser.get_current_folder())
        self._comboentry.child.set_text(name)

    def _response(self, widget, response):
        paths = super(_LibraryFileChooserDialog, self).handle_response(response)
        if paths is None:
            return
        if not paths:
            close_library_filechooser_dialog()
        else:
            if self._collection_button.get_active():
                prefs['auto add books into collections'] = True
                collection_name = self._comboentry.get_active_text()
                if not collection_name: # No empty-string names.
                    collection_name = None
            else:
                prefs['auto add books into collections'] = False
                collection_name = None
            close_library_filechooser_dialog()
            self._library.add_books(paths, collection_name)


def open_main_filechooser_dialog(action, file_handler):
    """Open the main filechooser dialog."""
    global _main_filechooser_dialog
    if _main_filechooser_dialog is None:
        _main_filechooser_dialog = _MainFileChooserDialog(file_handler)
    else:
        _main_filechooser_dialog.present()


def _close_main_filechooser_dialog(*args):
    """Close the main filechooser dialog."""
    global _main_filechooser_dialog
    if _main_filechooser_dialog is not None:
        _main_filechooser_dialog.destroy()
        _main_filechooser_dialog = None


def open_library_filechooser_dialog(library):
    """Open the library filechooser dialog."""
    global _library_filechooser_dialog
    if _library_filechooser_dialog is None:
        _library_filechooser_dialog = _LibraryFileChooserDialog(library)
    else:
        _library_filechooser_dialog.present()


def close_library_filechooser_dialog(*args):
    """Close the library filechooser dialog."""
    global _library_filechooser_dialog
    if _library_filechooser_dialog is not None:
        _library_filechooser_dialog.destroy()
        _library_filechooser_dialog = None
