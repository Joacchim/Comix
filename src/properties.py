# ============================================================================
# properties.py - Properties dialog for Comix.
# ============================================================================

import os
import time
import stat
import pwd

import gtk
import pango

import archive
import encoding
import histogram
import scale

dialog = None

class PropertiesDialog(gtk.Dialog):

    def __init__(self, window):
        
        gtk.Dialog.__init__(self, _('Properties'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        
        self.mainwindow = window
        self.set_resizable(False)
        self.set_has_separator(False)
        self.connect('response', dialog_close)
        self.connect('delete_event', dialog_close)
        self.set_default_response(gtk.RESPONSE_CLOSE)
        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook, False, False, 0)
        
        if self.mainwindow.file_handler.archive_type:
            # ------------------------------------------------------------
            # Archive tab
            # ------------------------------------------------------------
            stats = os.stat(self.mainwindow.file_handler.archive_path)
            page = gtk.VBox(False, 12)
            page.set_border_width(12)
            topbox = gtk.HBox(False, 12)
            page.pack_start(topbox)
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                self.mainwindow.file_handler.image_files[0], 200, 128)
            pixbuf = scale.add_border(pixbuf, 1)
            thumb = gtk.Image()
            thumb.set_from_pixbuf(pixbuf)
            topbox.pack_start(thumb, False, False)
            
            borderbox = gtk.EventBox()
            borderbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333'))
            borderbox.set_size_request(-1, 130)
            topbox.pack_start(borderbox)
            insidebox = gtk.EventBox()
            insidebox.set_border_width(1)
            insidebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddb'))
            borderbox.add(insidebox)
            infobox = gtk.VBox(False, 5)
            infobox.set_border_width(10)
            insidebox.add(infobox)
            label = gtk.Label(encoding.to_unicode(os.path.basename(
                self.mainwindow.file_handler.archive_path)))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrlist)
            infobox.pack_start(label, False, False)
            infobox.pack_start(gtk.VBox()) # Just to add space (any better way?)
            label = gtk.Label(_('%d pages') %
                len(self.mainwindow.file_handler.image_files))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label(_('%d comments') %
                len(self.mainwindow.file_handler.comment_files))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label(archive.get_name(
                self.mainwindow.file_handler.archive_type))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label('%.1f MiB' % (stats.st_size / 1048576.0))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)

            label = gtk.Label(_('Location') + ':   ' +
                encoding.to_unicode(os.path.dirname(
                self.mainwindow.file_handler.archive_path)))
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(_('Location')) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            page.pack_start(label, False, False)
            label = gtk.Label(_('Accessed') + ':   ' +
                time.strftime('%Y-%m-%d [%H:%M:%S]',
                time.localtime(stats.st_atime)))
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(_('Accessed')) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            page.pack_start(label, False, False)
            label = gtk.Label(_('Modified') + ':   ' +
                time.strftime('%Y-%m-%d [%H:%M:%S]',
                time.localtime(stats.st_mtime)))
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(_('Modified')) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            page.pack_start(label, False, False)
            label = gtk.Label(_('Permissions') + ':   ' +
                oct(stat.S_IMODE(stats.st_mode)))
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(_('Permissions')) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            page.pack_start(label, False, False)
            label = gtk.Label(_('Owner') + ':   ' +
                pwd.getpwuid(stats.st_uid)[0])
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(_('Owner')) + 1))
            label.set_attributes(attrlist)
            label.set_alignment(0, 0.5)
            page.pack_start(label, False, False)
            notebook.append_page(page, gtk.Label(_('Archive')))
        
        # ----------------------------------------------------------------
        # Image tab
        # ----------------------------------------------------------------
        stats = os.stat(self.mainwindow.file_handler.image_files[
            self.mainwindow.file_handler.current_image])
        iminfo = gtk.gdk.pixbuf_get_file_info(
            self.mainwindow.file_handler.image_files[
            self.mainwindow.file_handler.current_image])
        page = gtk.HBox(False, 12)
        page.set_border_width(12)
        leftpane = gtk.VBox(False, 12)
        page.pack_start(leftpane, False, False)
        topbox = gtk.HBox(False, 12)
        leftpane.pack_start(topbox)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
            self.mainwindow.file_handler.image_files[
            self.mainwindow.file_handler.current_image], 200, 128)
        pixbuf = scale.add_border(pixbuf, 1)
        thumb = gtk.Image()
        thumb.set_from_pixbuf(pixbuf)
        topbox.pack_start(thumb, False, False)
        
        borderbox = gtk.EventBox()
        borderbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333'))
        borderbox.set_size_request(-1, 130)
        topbox.pack_start(borderbox)
        insidebox = gtk.EventBox()
        insidebox.set_border_width(1)
        insidebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddb'))
        borderbox.add(insidebox)
        infobox = gtk.VBox(False, 5)
        infobox.set_border_width(10)
        insidebox.add(infobox)
        label = gtk.Label(os.path.basename(encoding.to_unicode(
            self.mainwindow.file_handler.image_files[
            self.mainwindow.file_handler.current_image])))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrlist)
        infobox.pack_start(label, False, False)
        infobox.pack_start(gtk.VBox()) # Just to add space (any better way?)
        label = gtk.Label('%dx%d px' % (iminfo[1], iminfo[2]))
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)
        label = gtk.Label(iminfo[0]['name'].upper())
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)
        label = gtk.Label('%.1f kiB' % (stats.st_size / 1024.0))
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)

        label = gtk.Label(_('Location') + ':   ' +
            encoding.to_unicode(os.path.dirname(
            self.mainwindow.file_handler.image_files[
            self.mainwindow.file_handler.current_image])))
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(_('Location')) + 1))
        label.set_attributes(attrlist)
        label.set_alignment(0, 0.5)
        leftpane.pack_start(label, False, False)
        label = gtk.Label(_('Accessed') + ':   ' +
            time.strftime('%Y-%m-%d [%H:%M:%S]',
            time.localtime(stats.st_atime)))
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(_('Accessed')) + 1))
        label.set_attributes(attrlist)
        label.set_alignment(0, 0.5)
        leftpane.pack_start(label, False, False)
        label = gtk.Label(_('Modified') + ':   ' +
            time.strftime('%Y-%m-%d [%H:%M:%S]',
            time.localtime(stats.st_mtime)))
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(_('Modified')) + 1))
        label.set_attributes(attrlist)
        label.set_alignment(0, 0.5)
        leftpane.pack_start(label, False, False)
        label = gtk.Label(_('Permissions') + ':   ' +
            oct(stat.S_IMODE(stats.st_mode)))
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(_('Permissions')) + 1))
        label.set_attributes(attrlist)
        label.set_alignment(0, 0.5)
        leftpane.pack_start(label, False, False)
        label = gtk.Label(_('Owner') + ':   ' +
            pwd.getpwuid(stats.st_uid)[0])
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(_('Owner')) + 1))
        label.set_attributes(attrlist)
        label.set_alignment(0, 0.5)
        leftpane.pack_start(label, False, False)
        
        page.pack_start(gtk.VSeparator(), False, False)
        expander = gtk.Expander()
        page.pack_start(expander, False, False)
        
        

        notebook.append_page(page, gtk.Label(_('Image')))
  
        self.vbox.show_all()

def dialog_open(action, window):
    global dialog
    if dialog == None:
        dialog = PropertiesDialog(window)
        dialog.show()

def dialog_close(*args):
    global dialog
    if dialog != None:
        dialog.destroy()
        dialog = None 

