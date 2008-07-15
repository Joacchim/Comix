"""filechooser.py - FileChooserDialog implementation."""

import os

import gtk
import pango

import image
from preferences import prefs
import thumbnail

_dialog = None

# We roll our own FileChooserDialog because the one in GTK is buggy
# with the preview widget.
class _ComicFileChooserDialog(gtk.Dialog):
    
    def __init__(self, file_handler):
        gtk.Dialog.__init__(self, _('Open'), None, 0, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        self._file_handler = file_handler
        self.connect('response', self._response)
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_has_separator(False)

        self._filechooser = gtk.FileChooserWidget()
        self._filechooser.connect('file-activated', self._response, 
            gtk.RESPONSE_OK)
        self._filechooser.set_size_request(680, 420)
        self.vbox.pack_start(self._filechooser)
        self.set_border_width(4)
        self._filechooser.set_border_width(6)
        
        preview_box = gtk.VBox(False, 10)
        preview_box.set_size_request(130, 0)
        self._preview_image = gtk.Image()
        self._preview_image.set_size_request(130, 130)
        preview_box.pack_start(self._preview_image, False, False)
        self._filechooser.set_preview_widget(preview_box)
        self._namelabel = gtk.Label()
        self._namelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self._namelabel, False, False)
        self._sizelabel = gtk.Label()
        self._sizelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self._sizelabel, False, False)
        self._filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self._filechooser.connect('update-preview', self._update_preview)

        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(_('All files'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_pixbuf_formats()
        ffilter.set_name(_('All images'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-zip')
        ffilter.add_mime_type('application/zip')
        ffilter.add_mime_type('application/x-rar')
        ffilter.add_mime_type('application/x-tar')
        ffilter.add_mime_type('application/x-gzip')
        ffilter.add_mime_type('application/x-bzip2')
        ffilter.add_mime_type('application/x-cbz')
        ffilter.add_mime_type('application/x-cbr')
        ffilter.add_mime_type('application/x-cbt')
        ffilter.set_name(_('All archives'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/jpeg')
        ffilter.set_name(_('JPEG images'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/png')
        ffilter.set_name(_('PNG images'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-zip')
        ffilter.add_mime_type('application/zip')
        ffilter.add_mime_type('application/x-cbz')
        ffilter.set_name(_('Zip archives'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-rar')
        ffilter.add_mime_type('application/x-cbr')
        ffilter.set_name(_('RAR archives'))
        self._filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-tar')
        ffilter.add_mime_type('application/x-gzip')
        ffilter.add_mime_type('application/x-bzip2')
        ffilter.add_mime_type('application/x-cbt')
        ffilter.set_name(_('tar archives'))
        self._filechooser.add_filter(ffilter)

        self._filechooser.set_current_folder(prefs['path of last browsed'])

        self.show_all()

    def _update_preview(self, *args):
        path = self._filechooser.get_preview_filename()
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

    def _response(self, widget, response):
        if response == gtk.RESPONSE_OK:
            path = self._filechooser.get_filename()
            if os.path.isdir(path):
                self._filechooser.set_current_folder(path)
                return
            close_dialog()
            while gtk.events_pending():
                gtk.main_iteration(False)
            self._file_handler.open_file(path)
            prefs['path of last browsed'] = os.path.dirname(path)
        elif response in [gtk.RESPONSE_CANCEL, gtk.RESPONSE_DELETE_EVENT]:
            close_dialog()


def open_dialog(action, file_handler):
    global _dialog
    if _dialog is None:
        _dialog = _ComicFileChooserDialog(file_handler)

def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None

