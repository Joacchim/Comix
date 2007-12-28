# ============================================================================
# thumbbar.py - Thumbnail sidebar for Comix.
# ============================================================================

import time

import gtk
import Image
import ImageDraw

import image
from preferences import prefs
import pilpixbuf
import thumbnail

class ThumbnailSidebar:
    
    def __init__(self, window):
        self.window = window
        self.visible = False
        self.loaded = False
        # Set and unset by filehandler to make sure that the main image is
        # computed before the thumbnails.
        self.block = False    
        self.height = 0
        
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf)
        self.treeview = gtk.TreeView(self.liststore)
        self.column = gtk.TreeViewColumn(None)
        self.cellrenderer = gtk.CellRendererPixbuf()
        self.layout = gtk.Layout()
        self.layout.put(self.treeview, 0, 0)
        self.column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column.set_fixed_width(prefs['thumbnail size'] + 7)
        self.treeview.append_column(self.column)
        self.column.pack_start(self.cellrenderer, True)
        self.column.set_attributes(self.cellrenderer, pixbuf=0)
        self.layout.set_size_request(prefs['thumbnail size'] + 7, 0)
        self.treeview.set_headers_visible(False)
        self.vadjust = self.layout.get_vadjustment()
        self.vadjust.step_increment = 15
        self.vadjust.page_increment = 1
        self.scroll = gtk.VScrollbar(None)
        self.scroll.set_adjustment(self.vadjust)
        self.selection = self.treeview.get_selection()

        self.selection.connect('changed', self._selection_event)
        self.layout.connect('scroll_event', self._scroll_event)

    def get_width(self):
        return self.layout.size_request()[0] + self.scroll.size_request()[0]

    def show(self):
        self.layout.show_all()
        self.scroll.show()
        if not self.loaded:
            self.load_thumbnails()
        if not self.visible:
            self.layout.set_size(0, self.height)
            self.visible = True
    
    def hide(self):
        self.layout.hide_all()
        self.scroll.hide()
        self.visible = False

    def clear(self):
        self.liststore.clear()
        self.layout.set_size(0, 0)
        self.height = 0
        self.loaded = False

    def load_thumbnails(self):
        if (not prefs['show thumbnails'] or prefs['hide all'] or
          not self.window.file_handler.file_loaded or
          self.loaded or self.block):
            return
        
        t = time.time()

        self.loaded = True
        for i, path in enumerate(self.window.file_handler.image_files):
            if self.window.file_handler.archive_type:
                create = False
            else:
                create = prefs['create thumbnails']
            pixbuf = thumbnail.get_thumbnail(path, create)
            if pixbuf == None:
                pixbuf = gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE,
                    gtk.ICON_SIZE_BUTTON).get_pixbuf()
            pixbuf = image.fit_in_rectangle(pixbuf, prefs['thumbnail size'],
                                            prefs['thumbnail size'])
            if prefs['show page numbers on thumbnails']:
                _add_page_number(pixbuf, i + 1)
            pixbuf = image.add_border(pixbuf, 1)
            self.liststore.append([pixbuf])
            self.height += pixbuf.get_height() + 4

            while gtk.events_pending():
                gtk.main_iteration(False)

            self.layout.set_size(0, self.height)
        self.update_select()

        print time.time() - t

    def update_select(self):
        if not self.loaded:
            return
        self.selection.select_path(self.window.file_handler.current_image)
        rect = self.treeview.get_background_area(
            self.window.file_handler.current_image, self.column)
        if (rect.y < self.vadjust.get_value() or rect.y + rect.height > 
          self.vadjust.get_value() + self.vadjust.page_size):
            value = rect.y + (rect.height // 2) - (self.vadjust.page_size // 2)
            value = max(0, value)
            value = min(self.vadjust.upper - self.vadjust.page_size, value)
            self.vadjust.set_value(value)

    def _selection_event(self, widget):
        print 'select'
        try:
            selected = widget.get_selected_rows()[1][0][0]
            self.window.set_page(selected)
        except:
            pass

    def _scroll_event(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.vadjust.set_value(self.vadjust.get_value() - 60)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            upper = self.vadjust.upper - self.vadjust.page_size
            self.vadjust.set_value(min(self.vadjust.get_value() + 60, upper))


def _add_page_number(pixbuf, page):
    
    """ 
    Add page number <page> in a black rectangle in the top left corner of
    <pixbuf>. This is highly dependent on the dimensions of the built-in 
    font in PIL (bad). If the PIL font was changed, this function would
    likely produce badly positioned numbers on the pixbuf.

    Adding page numbers on thumbnails introduces a small but measurable
    delay overhead when we have a large number of pages. Making this
    function more efficient would be a good idea.
    """

    text = str(page)
    width = 6 * len(text) + 2
    height = 10
    im = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.text((1, -1), text, fill=(255, 255, 255))
    num_pixbuf = pilpixbuf.pil_to_pixbuf(im)
    num_pixbuf.copy_area(0, 0, width, height, pixbuf, 0, 0)

