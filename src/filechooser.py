import os

import gtk

import main
import filehandler
import preferences
import thumbnail

dialog = None

class ComicFileChooserDialog(gtk.FileChooserDialog):
    
    def __init__(self):
        gtk.FileChooserDialog.__init__(self, title=_('Open'),
            parent=main.window, action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        self.connect('response', dialog_response)
        self.connect('delete_event', dialog_close)
        self.set_default_response(gtk.RESPONSE_OK)
        
        #preview_box = gtk.VBox(False, 2)
        self.preview_image = gtk.Image()
        self.preview_image.set_size_request(128, 128)
        #preview_image.show()
        #preview_box.add(preview_image)
        #preview_box.set_size_request(100, 1)
        #preview_box.show()
        self.set_preview_widget(self.preview_image)
        #self.set_use_preview_label(False)
        self.connect('update-preview', self.update_preview)

        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(_('All files'))
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_pixbuf_formats()
        ffilter.set_name(_('All images'))
        self.add_filter(ffilter)
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
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/jpeg')
        ffilter.set_name(_('JPEG images'))
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('image/png')
        ffilter.set_name(_('PNG images'))
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-zip')
        ffilter.add_mime_type('application/zip')
        ffilter.add_mime_type('application/x-cbz')
        ffilter.set_name(_('ZIP archives'))
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-rar')
        ffilter.add_mime_type('application/x-cbr')
        ffilter.set_name(_('RAR archives'))
        self.add_filter(ffilter)
        ffilter = gtk.FileFilter()
        ffilter.add_mime_type('application/x-tar')
        ffilter.add_mime_type('application/x-gzip')
        ffilter.add_mime_type('application/x-bzip2')
        ffilter.add_mime_type('application/x-cbt')
        ffilter.set_name(_('tar archives'))
        self.add_filter(ffilter)

    def update_preview(self, *args):
        path = self.get_preview_filename()
        if path and os.path.isfile(path):
            pixbuf = thumbnail.get_thumbnail(path,
                preferences.prefs['create thumbnails'])
            if pixbuf == None:
                self.preview_image.clear()
            else:
                self.preview_image.set_from_pixbuf(pixbuf)
        else:
            self.preview_image.clear()

def dialog_open(*args):
    global dialog
    dialog = ComicFileChooserDialog()
    if preferences.prefs['open defaults to last browsed']:
        dialog.set_current_folder(preferences.prefs['path of last browsed'])
    dialog.run()

def dialog_close(*args):
    global dialog
    if dialog != None:
        dialog.destroy()
        dialog = None

def dialog_response(widget, response):
    if response == gtk.RESPONSE_OK:
        path = dialog.get_filename()
        dialog_close()
        while gtk.events_pending():
            gtk.main_iteration(False)
        filehandler.open_file(path)
        main.window.draw_image()
        if preferences.prefs['open defaults to last browsed']:
            preferences.prefs['path of last browsed'] = os.path.dirname(path)
    elif response == gtk.RESPONSE_CANCEL:
        dialog_close()

