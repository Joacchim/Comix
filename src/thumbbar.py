# ============================================================================
# thumbbar.py - Thumbnail sidebar for Comix.
# ============================================================================

import time

import gtk

import main
import preferences
import filehandler
import thumbnail
import scale

class ThumbnailSidebar:
    
    def __init__(self):

        #self.visible = False
        #self.loaded = False
        
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf)
        self.treeview = gtk.TreeView(self.liststore)
        self.column = gtk.TreeViewColumn(None)
        self.cellrenderer = gtk.CellRendererPixbuf()
        self.layout = gtk.Layout()
        self.layout.put(self.treeview, 0, 0)
        self.column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column.set_fixed_width(preferences.prefs['thumbnail size'] + 7)
        self.treeview.append_column(self.column)
        self.column.pack_start(self.cellrenderer, True)
        self.column.set_attributes(self.cellrenderer, pixbuf=0)
        self.layout.set_size_request(preferences.prefs['thumbnail size'] + 7, 0)
        #self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.treeview.set_headers_visible(False)
        self.vadjust = self.layout.get_vadjustment()
        self.vadjust.step_increment = 15
        self.vadjust.page_increment = 1
        self.scroll = gtk.VScrollbar(None)
        self.scroll.set_adjustment(self.vadjust)
        self.selection = self.treeview.get_selection()

        self.selection.connect('changed', self.selection_event)
        self.layout.connect('scroll_event', self.scroll_event)

    def selection_event(self, widget):
        try:
            selected = widget.get_selected_rows()[1][0][0]
            main.set_page(selected)
        except:
            pass

    def get_width(self):
        return self.layout.size_request()[0] + self.scroll.size_request()[0]

    def show(self):
        self.layout.show_all()
        self.scroll.show()
        #self.visible = True
        #if not self.loaded:
        #    self.load_thumbnails()
        #self.layout.set_size(0, self.treeview.get_visible_rect().height)
        #self.update_select()
    
    def hide(self):
        self.layout.hide_all()
        self.scroll.hide()
        #self.visible = False

    def load_thumbnails(self):
        print 'load'
        #if not self.visible or self.loaded:
        #    return
        for i, path in enumerate(filehandler.image_files):
            if filehandler.archive_type:
                create = False
            else:
                create = preferences.prefs['create thumbnails']
            pixbuf = thumbnail.get_thumbnail(path, create)
            if pixbuf == None:
                pixbuf = gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE,
                    gtk.ICON_SIZE_BUTTON).get_pixbuf()
            pixbuf = scale.fit_in_rectangle(pixbuf, 
                preferences.prefs['thumbnail size'],
                preferences.prefs['thumbnail size'])
            pixbuf = scale.add_border(pixbuf, 1)
            self.liststore.append([pixbuf])

            while gtk.events_pending():
                gtk.main_iteration(False)

            self.layout.set_size(0, self.treeview.get_visible_rect().height)
        #self.loaded = True
        self.update_select()

    def clear(self):
        self.liststore.clear()
        self.layout.set_size(0, 0)
        #self.loaded = False

    def update_select(self):
        #if not self.visible or not filehandler.file_loaded:
        #    return
        self.selection.select_path(filehandler.current_image)
        rect = self.treeview.get_background_area(
            filehandler.current_image, self.column)
        if (rect.y < self.vadjust.get_value() or rect.y + rect.height > 
          self.vadjust.get_value() + self.vadjust.page_size):
            value = rect.y + (rect.height // 2) - (self.vadjust.page_size // 2)
            value = max(0, value)
            value = min(self.vadjust.upper - self.vadjust.page_size, value)
            self.vadjust.set_value(value)

    def scroll_event(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.vadjust.set_value(self.vadjust.get_value() - 60)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            upper = self.vadjust.upper - self.vadjust.page_size
            self.vadjust.set_value(min(self.vadjust.get_value() + 60, upper))

