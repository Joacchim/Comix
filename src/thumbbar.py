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

class ThumbnailSidebar(gtk.HBox):
    
    def __init__(self, window):
        gtk.HBox.__init__(self, False, 0)
        self._window = window
        self._block = False    
        self._visible = False
        self._loaded = False
        self._height = 0
        self._counter = None
        
        self._liststore = gtk.ListStore(gtk.gdk.Pixbuf)
        self._treeview = gtk.TreeView(self._liststore)
        self._column = gtk.TreeViewColumn(None)
        cellrenderer = gtk.CellRendererPixbuf()
        self._layout = gtk.Layout()
        self._layout.put(self._treeview, 0, 0)
        self._column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._column.set_fixed_width(prefs['thumbnail size'] + 7)
        self._treeview.append_column(self._column)
        self._column.pack_start(cellrenderer, True)
        self._column.set_attributes(cellrenderer, pixbuf=0)
        self._layout.set_size_request(prefs['thumbnail size'] + 7, 0)
        self._treeview.set_headers_visible(False)
        self._vadjust = self._layout.get_vadjustment()
        self._vadjust.step_increment = 15
        self._vadjust.page_increment = 1
        self._scroll = gtk.VScrollbar(None)
        self._scroll.set_adjustment(self._vadjust)
        self._selection = self._treeview.get_selection()

        self.pack_start(self._layout)
        self.pack_start(self._scroll)

        self._selection.connect('changed', self._selection_event)
        self._layout.connect('scroll_event', self._scroll_event)

    def get_width(self):
        return self._layout.size_request()[0] + self._scroll.size_request()[0]

    def show(self):
        self.show_all()
        if not self._loaded:
            self.load_thumbnails()
        if not self._visible:
            self._layout.set_size(0, self._height)
            self._visible = True
    
    def hide(self):
        self._layout.hide_all()
        self._scroll.hide()
        self._visible = False

    def clear(self):
        self._liststore.clear()
        self._layout.set_size(0, 0)
        self._height = 0
        self._loaded = False
        self._counter = _Counter(0)

    def load_thumbnails(self):
        if (not prefs['show thumbnails'] or prefs['hide all'] or
          not self._window.file_handler.file_loaded or
          self._loaded or self._block):
            return
        
        self._loaded = True
        self._counter = _Counter(
            self._window.file_handler.get_number_of_pages())
        while self._counter.incr():
            i = self._counter.get()
            if self._window.file_handler.archive_type:
                create = False
            else:
                create = prefs['create thumbnails']
            pixbuf = self._window.file_handler.get_thumbnail(i,
                prefs['thumbnail size'], prefs['thumbnail size'], create)
            if prefs['show page numbers on thumbnails']:
                _add_page_number(pixbuf, i)
            pixbuf = image.add_border(pixbuf, 1)
            self._liststore.append([pixbuf])
            self._height += pixbuf.get_height() + 4
            self._layout.set_size(0, self._height)

            while gtk.events_pending():
                gtk.main_iteration(False)

        self.update_select()

    def update_select(self):
        if not self._loaded:
            return
        self._selection.select_path(
            self._window.file_handler.get_current_page() - 1)
        rect = self._treeview.get_background_area(
            self._window.file_handler.get_current_page() - 1, self._column)
        if (rect.y < self._vadjust.get_value() or rect.y + rect.height > 
          self._vadjust.get_value() + self._vadjust.page_size):
            value = rect.y + (rect.height // 2) - (self._vadjust.page_size // 2)
            value = max(0, value)
            value = min(self._vadjust.upper - self._vadjust.page_size, value)
            self._vadjust.set_value(value)

    def block(self):
        self._block = True

    def unblock(self):
        self._block = False

    def _selection_event(self, widget):
        try:
            selected = widget.get_selected_rows()[1][0][0]
            self._window.set_page(selected + 1)
        except:
            pass

    def _scroll_event(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self._vadjust.set_value(self._vadjust.get_value() - 60)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            upper = self._vadjust.upper - self._vadjust.page_size
            self._vadjust.set_value(min(self._vadjust.get_value() + 60, upper))


class _Counter:

    def __init__(self, roof):
        self._roof = roof
        self._num = 0
    
    def get(self):
        return self._num

    def incr(self):
        self._num += 1
        return self._num <= self._roof


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

