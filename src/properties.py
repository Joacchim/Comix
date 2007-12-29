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
import image

dialog = None

class PropertiesDialog(gtk.Dialog):

    def __init__(self, window):
        
        gtk.Dialog.__init__(self, _('Properties'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        
        self.set_resizable(False)
        self.set_has_separator(False)
        self.connect('response', dialog_close)
        self.connect('delete_event', dialog_close)
        self.set_default_response(gtk.RESPONSE_CLOSE)
        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook, False, False, 0)
        
        if window.file_handler.archive_type:
            # ------------------------------------------------------------
            # Archive tab
            # ------------------------------------------------------------
            stats = os.stat(window.file_handler.get_path_to_base())
            page = gtk.VBox(False, 12)
            page.set_border_width(12)
            topbox = gtk.HBox(False, 12)
            page.pack_start(topbox, False)
            # Add thumbnail
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                window.file_handler.get_path_to_page(1), 200, 128)
            pixbuf = image.add_border(pixbuf, 1)
            thumb = gtk.Image()
            thumb.set_from_pixbuf(pixbuf)
            topbox.pack_start(thumb, False, False)
            # Add coloured box for main info
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
            # Add bold archive name
            label = gtk.Label(encoding.to_unicode(
                window.file_handler.get_pretty_current_filename()))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrlist)
            infobox.pack_start(label, False, False)
            infobox.pack_start(gtk.VBox()) # Just to add space (any better way?)
            # Add the rest of the main info to the coloured box
            label = gtk.Label(_('%d pages') %
                window.file_handler.number_of_pages())
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label(_('%d comments') %
                window.file_handler.number_of_comments())
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label(archive.get_name(
                window.file_handler.archive_type))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            label = gtk.Label('%.1f MiB' % (stats.st_size / 1048576.0))
            label.set_alignment(0, 0.5)
            infobox.pack_start(label, False, False)
            # Other info below
            label = gtk.Label(_('Location') + ':   ' +
                encoding.to_unicode(os.path.dirname(
                window.file_handler.get_path_to_base())))
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
        stats = os.stat(window.file_handler.get_path_to_page())
        iminfo = gtk.gdk.pixbuf_get_file_info(
            window.file_handler.get_path_to_page())
        page = gtk.VBox(False, 12)
        page.set_border_width(12)
        topbox = gtk.HBox(False, 12)
        page.pack_start(topbox)
        # Add thumbnail
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
            window.file_handler.get_path_to_page(), 200, 128)
        pixbuf = image.add_border(pixbuf, 1)
        thumb = gtk.Image()
        thumb.set_from_pixbuf(pixbuf)
        topbox.pack_start(thumb, False, False)
        # Add coloured main info box
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
        # Add bold filename
        label = gtk.Label(encoding.to_unicode(os.path.basename(
            window.file_handler.get_path_to_page())))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrlist)
        infobox.pack_start(label, False, False)
        infobox.pack_start(gtk.VBox()) # Just to add space (any better way?)
        # Add the rest of the main info
        label = gtk.Label('%dx%d px' % (iminfo[1], iminfo[2]))
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)
        label = gtk.Label(iminfo[0]['name'].upper())
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)
        label = gtk.Label('%.1f kiB' % (stats.st_size / 1024.0))
        label.set_alignment(0, 0.5)
        infobox.pack_start(label, False, False)
        # Other info below the thumb + main info box
        label = gtk.Label(_('Location') + ':   ' +
            encoding.to_unicode(os.path.dirname(
            window.file_handler.get_path_to_page())))
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

