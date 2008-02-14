# ============================================================================
# properties.py - Properties dialog.
# ============================================================================

import os
import time
import stat
import pwd

import gtk
import pango

import archive
import encoding
import image

_dialog = None

class _Page(gtk.VBox):
    
    """
    A page to put in the gtk.Notebook. Contains info about a file (an image
    or an archive.)
    """
    
    def __init__(self):
        gtk.VBox.__init__(self, False, 12)
        
        self.set_border_width(12)
        topbox = gtk.HBox(False, 12)
        self.pack_start(topbox, False)
        self._thumb = gtk.Image()
        topbox.pack_start(self._thumb, False, False)
        borderbox = gtk.EventBox()
        borderbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333'))
        borderbox.set_size_request(-1, 130)
        topbox.pack_start(borderbox)
        insidebox = gtk.EventBox()
        insidebox.set_border_width(1)
        insidebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddb'))
        borderbox.add(insidebox)
        self._mainbox = gtk.VBox(False, 5)
        self._mainbox.set_border_width(10)
        insidebox.add(self._mainbox)

    def set_thumbnail(self, pixbuf):
        pixbuf = image.add_border(pixbuf, 1)
        self._thumb.set_from_pixbuf(pixbuf)

    def set_filename(self, filename):
        
        """
        Set the filename to be displayed to <filename>. Call this before
        set_main_info().
        """

        label = gtk.Label(encoding.to_unicode(filename))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrlist)
        self._mainbox.pack_start(label, False, False)
        self._mainbox.pack_start(gtk.VBox()) # Just to add space (better way?)

    def set_main_info(self, info):
        
        """
        Set the information in the main info box (below the filename) to
        the values in the sequence <info>.
        """

        for text in info:
            label = gtk.Label(text)
            label.set_alignment(0, 0.5)
            self._mainbox.pack_start(label, False, False)

    def set_secondary_info(self, info):
        
        """
        Set the information below the main info box to the values in the
        sequence <info>. Each entry in info should be a tuple (desc, value).
        """

        for desc, value in info:
            label = gtk.Label('%s:  %s' % (desc, value))
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(desc) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            self.pack_start(label, False, False)


class _PropertiesDialog(gtk.Dialog):

    def __init__(self, window):
        
        gtk.Dialog.__init__(self, _('Properties'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        
        self.set_resizable(False)
        self.set_has_separator(False)
        self.connect('response', close_dialog)
        self.set_default_response(gtk.RESPONSE_CLOSE)
        notebook = gtk.Notebook()
        self.set_border_width(4)
        notebook.set_border_width(6)
        self.vbox.pack_start(notebook, False, False, 0)
        
        if window.file_handler.archive_type:
            # ------------------------------------------------------------
            # Archive tab
            # ------------------------------------------------------------
            page = _Page()
            thumb = window.file_handler.get_thumbnail(1, width=200, height=128)
            page.set_thumbnail(thumb)
            filename = window.file_handler.get_pretty_current_filename()
            page.set_filename(filename)
            try:
                stats = os.stat(window.file_handler.get_path_to_base())
                main_info = (
                    _('%d pages') % window.file_handler.get_number_of_pages(),
                    _('%d comments') %
                        window.file_handler.get_number_of_comments(),
                    archive.get_name(window.file_handler.archive_type),
                    '%.1f MiB' % (stats.st_size / 1048576.0))
                page.set_main_info(main_info)
                try:
                    uid = pwd.getpwuid(stats.st_uid)[0]
                except:
                    uid = str(stats.st_uid)
                secondary_info = (
                    (_('Location'), encoding.to_unicode(os.path.dirname(
                    window.file_handler.get_path_to_base()))),
                    (_('Accessed'), time.strftime('%Y-%m-%d [%H:%M:%S]',
                    time.localtime(stats.st_atime))),
                    (_('Modified'), time.strftime('%Y-%m-%d [%H:%M:%S]',
                    time.localtime(stats.st_mtime))),
                    (_('Permissions'), oct(stat.S_IMODE(stats.st_mode))),
                    (_('Owner'), uid))
                page.set_secondary_info(secondary_info)
            except:
                pass
            notebook.append_page(page, gtk.Label(_('Archive')))
        
        # ----------------------------------------------------------------
        # Image tab
        # ----------------------------------------------------------------
        path = window.file_handler.get_path_to_page()
        page = _Page()
        thumb = window.file_handler.get_thumbnail(width=200, height=128)
        page.set_thumbnail(thumb)       
        filename = os.path.basename(path)
        page.set_filename(filename)
        try:
            stats = os.stat(path)
            width, height = window.file_handler.get_size()
            main_info = ( 
                '%dx%d px' % (width, height),
                window.file_handler.get_mime_name(),
                '%.1f KiB' % (stats.st_size / 1024.0))
            page.set_main_info(main_info)
            try:
                uid = pwd.getpwuid(stats.st_uid)[0]
            except:
                uid = str(stats.st_uid)
            secondary_info = (
                (_('Location'), encoding.to_unicode(os.path.dirname(path))),
                (_('Accessed'), time.strftime('%Y-%m-%d [%H:%M:%S]',
                time.localtime(stats.st_atime))),
                (_('Modified'), time.strftime('%Y-%m-%d [%H:%M:%S]',
                time.localtime(stats.st_mtime))),
                (_('Permissions'), oct(stat.S_IMODE(stats.st_mode))),
                (_('Owner'), uid))
            page.set_secondary_info(secondary_info)
        except:
            pass
        notebook.append_page(page, gtk.Label(_('Image')))
        self.show_all()

def open_dialog(action, window):
    global _dialog
    if _dialog == None:
        _dialog = _PropertiesDialog(window)

def close_dialog(*args):
    global _dialog
    if _dialog != None:
        _dialog.destroy()
        _dialog = None 

