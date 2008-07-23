"""library.py - Comic book library."""

import gtk
import pango

import archive
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
        self._iconview.connect('item_activated', self._open_book)
        self._iconview.connect('selection_changed', self._update_info)
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self._iconview)
        self._iconview.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color())

        self._statusbar = gtk.Statusbar()
        self._statusbar.set_has_resize_grip(True)
    
        # The bottom box
        bottombox = gtk.HBox(False, 20)
        bottombox.set_border_width(10)
        borderbox = gtk.EventBox()
        borderbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333'))
        borderbox.set_size_request(300, -1)
        bottombox.pack_start(borderbox, False, False)
        insidebox = gtk.EventBox()
        insidebox.set_border_width(1)
        insidebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddb'))
        borderbox.add(insidebox)
        infobox = gtk.VBox(False, 5)
        infobox.set_border_width(10)
        insidebox.add(infobox)
        self._namelabel = gtk.Label()
        self._namelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self._namelabel.set_alignment(0, 0.5)
        infobox.pack_start(self._namelabel, False, False)
        self._typelabel = gtk.Label()
        self._typelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self._typelabel.set_alignment(0, 0.5)
        infobox.pack_start(self._typelabel, False, False)
        self._pageslabel = gtk.Label()
        self._pageslabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self._pageslabel.set_alignment(0, 0.5)
        infobox.pack_start(self._pageslabel, False, False)
        self._sizelabel = gtk.Label()
        self._sizelabel.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self._sizelabel.set_alignment(0, 0.5)
        infobox.pack_start(self._sizelabel, False, False)
        vbox = gtk.VBox(False, 10)
        bottombox.pack_start(vbox, True, True)
        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False)
        self._search_entry = gtk.Entry()
        label = gtk.Label('%s:' % _('Search'))
        hbox.pack_start(label, False, False)
        hbox.pack_start(self._search_entry)
        vbox.pack_start(gtk.HBox(), True, True)
        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False)
        add_book_button = gtk.Button(_('Add books'))
        add_book_button.set_image(gtk.image_new_from_stock(
            gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON))
        hbox.pack_start(add_book_button, False, False)
        add_collection_button = gtk.Button(_('Add collection'))
        add_collection_button.set_image(gtk.image_new_from_stock(
            gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON))
        hbox.pack_start(add_collection_button, False, False)
        hbox.pack_start(gtk.HBox(), True, True)
        open_button = gtk.Button(None, gtk.STOCK_OPEN)
        #open_button.connect()
        hbox.pack_start(open_button, False, False)
        
        # The side box
        sidebox = gtk.VBox(False, 6)


        self._table = gtk.Table(2, 2, False)
        self._table.attach(sidebox, 0, 1, 0, 1, gtk.FILL,
            gtk.EXPAND|gtk.FILL)
        self._table.attach(scrolled, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL,
            gtk.EXPAND|gtk.FILL)
        self._table.attach(bottombox, 0, 2, 1, 2, gtk.EXPAND|gtk.FILL,
            gtk.FILL)
        self._table.attach(self._statusbar, 0, 2, 2, 3, gtk.FILL, gtk.FILL)
        self.add(self._table)

        self._iconview.enable_model_drag_source(0, [], gtk.gdk.ACTION_MOVE)
        
        self.show_all()

    def load_covers(self):
        for i, book in enumerate(self._backend.get_books_in_collection()):
            pixbuf = self._backend.get_book_cover(book[0])
            if pixbuf is None:
                continue 
            pixbuf = image.fit_in_rectangle(pixbuf, 90, 128)
            pixbuf = image.add_border(pixbuf, 2, 0xFFFFFFFF)
            self._main_liststore.append([pixbuf, book[0]])
            if i % 15 == 0:
                while gtk.events_pending():
                    gtk.main_iteration(False)
                if self._destroy:
                    return

    def _update_info(self, iconview):
        selected = iconview.get_selected_items()
        if not selected:
            return
        path = selected[0]
        iterator = self._main_liststore.get_iter(path)
        book = self._main_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        self._namelabel.set_text(info[1])
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(self._namelabel.get_text())))
        self._namelabel.set_attributes(attrlist)
        self._typelabel.set_text(archive.get_name(info[4]))
        self._pageslabel.set_text(_('%d pages') % info[3])
        self._sizelabel.set_text('%.1f MiB' % (info[5] / 1048576.0))

    def _set_status_message(self, message):
        """Set a specific message on the statusbar, replacing whatever was
        there earlier.
        """
        self._statusbar.pop(0)
        self._statusbar.push(0, ' %s' % encoding.to_unicode(message))

    def _open_book(self, iconview, path):
        """Open the book at the (liststore) """
        iterator = self._main_liststore.get_iter(path)
        book = self._main_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        path = info[2]
        self._close()
        self._window.file_handler.open_file(path)

    def _close(self, *args):
        prefs['lib window width'], prefs['lib window height'] = self.get_size()
        self._destroy = True
        self._backend.close()
        close_dialog()


def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        if librarybackend.dbapi2 is None:
            print '! You need an sqlite wrapper to use the library.'
        else:
            _dialog = _LibraryDialog(window)
            _dialog.load_covers()

def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None

