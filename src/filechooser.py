# ============================================================================
# filechooser.py - FileChooserDialog implementation for Comix.
# ============================================================================

import os

import gtk
import pango

from preferences import prefs
import thumbnail
import scale

dialog = None

# We roll our own FileChooserDialog because the one in GTK is buggy
# with the preview widget.
class ComicFileChooserDialog(gtk.Dialog):
    
    def __init__(self, window):
        gtk.Dialog.__init__(self, title=_('Open'),
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        self.mainwindow = window
        self.connect('response', self.dialog_response)
        self.connect('delete_event', dialog_close)
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_has_separator(False)

        self.filechooser = gtk.FileChooserWidget()
        self.filechooser.connect('file-activated', self.dialog_response, 
            gtk.RESPONSE_OK)
        self.vbox.pack_start(self.filechooser)
        self.filechooser.set_border_width(10)
        self.filechooser.set_size_request(680, 420)
        
        preview_box = gtk.VBox(False, 10)
        preview_box.set_size_request(130, 0)
        self.preview_image = gtk.Image()
        self.preview_image.set_size_request(130, 130)
        preview_box.pack_start(self.preview_image, False, False)
        self.filechooser.set_preview_widget(preview_box)
        self.namelabel = gtk.Label()
        self.namelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self.namelabel, False, False)
        self.sizelabel = gtk.Label()
        self.sizelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        preview_box.pack_start(self.sizelabel, False, False)
        self.filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self.filechooser.connect('update-preview', self.update_preview)

        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(_('All files'))
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_pixbuf_formats()
        ffilter.set_name(_('All images'))
        self.filechooser.add_filter(ffilter)
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
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/jpeg')
        ffilter.set_name(_('JPEG images'))
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/png')
        ffilter.set_name(_('PNG images'))
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-zip')
        ffilter.add_mime_type('application/zip')
        ffilter.add_mime_type('application/x-cbz')
        ffilter.set_name(_('ZIP archives'))
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-rar')
        ffilter.add_mime_type('application/x-cbr')
        ffilter.set_name(_('RAR archives'))
        self.filechooser.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-tar')
        ffilter.add_mime_type('application/x-gzip')
        ffilter.add_mime_type('application/x-bzip2')
        ffilter.add_mime_type('application/x-cbt')
        ffilter.set_name(_('tar archives'))
        self.filechooser.add_filter(ffilter)

        self.vbox.show_all()

    def update_preview(self, *args):
        path = self.filechooser.get_preview_filename()
        if path and os.path.isfile(path):
            pixbuf = thumbnail.get_thumbnail(path, prefs['create thumbnails'])
            if pixbuf == None:
                self.preview_image.clear()
                self.namelabel.set_text('')
                self.sizelabel.set_text('')
            else:
                pixbuf = scale.add_border(pixbuf, 1)
                self.preview_image.set_from_pixbuf(pixbuf)
                self.namelabel.set_text(os.path.basename(path))
                self.sizelabel.set_text(
                    '%.1f KiB' % (os.stat(path).st_size / 1024.0))
                attrlist = pango.AttrList()
                attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                    len(self.namelabel.get_text())))
                attrlist.insert(pango.AttrSize(8000, 0,
                    len(self.namelabel.get_text())))
                self.namelabel.set_attributes(attrlist)
                attrlist = pango.AttrList()
                attrlist.insert(pango.AttrSize(8000, 0,
                    len(self.sizelabel.get_text())))
                self.sizelabel.set_attributes(attrlist)
        else:
            self.preview_image.clear()
            self.namelabel.set_text('')
            self.sizelabel.set_text('')

    def dialog_response(self, widget, response):
        if response == gtk.RESPONSE_OK:
            path = self.filechooser.get_filename()
            if os.path.isdir(path):
                self.filechooser.set_current_folder(path)
                return
            dialog_close()
            while gtk.events_pending():
                gtk.main_iteration(False)
            self.mainwindow.file_handler.open_file(path)
            if prefs['open defaults to last browsed']:
                prefs['path of last browsed'] = os.path.dirname(path)
        elif response == gtk.RESPONSE_CANCEL:
            dialog_close()


def dialog_open(action, window):
    global dialog
    if dialog == None:
        dialog = ComicFileChooserDialog(window)
        if prefs['open defaults to last browsed']:
            dialog.filechooser.set_current_folder(prefs['path of last browsed'])
        dialog.run()

def dialog_close(*args):
    global dialog
    if dialog != None:
        dialog.destroy()
        dialog = None


