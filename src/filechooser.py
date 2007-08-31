import os

import gtk

import main
import filehandler
import preferences

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
        
        #self.file_select_preview_box = gtk.VBox(False, 2)
        #self.file_select_preview_box.set_size_request(130, 0)
        #self.file_select_preview_box.show()
        #self.file_select.set_preview_widget(self.file_select_preview_box)
        #self.file_select.set_use_preview_label(False)

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
    global dialog
    
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

