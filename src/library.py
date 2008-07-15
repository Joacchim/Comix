"""library.py - Comic book library."""

import gtk

import librarybackend
from preferences import prefs
import image

_dialog = None

class _LibraryDialog(gtk.Window):

    def __init__(self, window):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_size_request(300, 300)
        self.resize(prefs['lib window width'], prefs['lib window height'])
        self.set_title(_('Library'))
        self.connect('delete_event', self._close)
        
        self._window = window
        self._backend = librarybackend.LibraryBackend()
        self._destroy = False
        
        self._main_liststore = gtk.ListStore(gtk.gdk.Pixbuf, int)
        self._iconview = gtk.IconView(self._main_liststore)
        self._iconview.set_pixbuf_column(0)
        #self._iconview.set_item_width(80)
        self._iconview.connect('item_activated', self._open_book)
        #cell = self._iconview.get_cells()[0]
        #cell.set_property('cell-background', '#000')
        #cell.set_property('cell-background-set', True)
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self._iconview)
        self._iconview.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0))

        self._sidebox = gtk.VBox(False, 6)
        self._bottombox = gtk.HBox(False, 6)
        self._statusbar = gtk.Statusbar()
        self._statusbar.set_has_resize_grip(True)

        self._table = gtk.Table(2, 2, False)
        self._table.attach(self._sidebox, 0, 1, 0, 2, gtk.FILL,
            gtk.EXPAND|gtk.FILL)
        self._table.attach(scrolled, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL,
            gtk.EXPAND|gtk.FILL)
        self._table.attach(self._bottombox, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL,
            gtk.FILL)
        self._table.attach(self._statusbar, 0, 2, 2, 3, gtk.FILL, gtk.FILL)
        self.add(self._table)
        
        self.show_all()

    def load_covers(self):
        for i, book in enumerate(self._backend.get_books_in_collection()):
            pixbuf = self._backend.get_book_cover(book[0])
            pixbuf = image.fit_in_rectangle(pixbuf, 90, 128)
            pixbuf = image.add_border(pixbuf, 2, 0xFFFFFFFF)
            self._main_liststore.append([pixbuf, book[0]])
            if i % 15 == 0:
                while gtk.events_pending():
                    gtk.main_iteration(False)
                if self._destroy:
                    return

    def _open_book(self, iconview, path):
        iterator = self._main_liststore.get_iter(path)
        book = self._main_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        path = info[2]
        self._close()
        self._window.file_handler.open_file(path)

    def _close(self, *args):
        self._destroy = True
        self._backend.close()
        close_dialog()


def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        _dialog = _LibraryDialog(window)
        _dialog.load_covers()

def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None

