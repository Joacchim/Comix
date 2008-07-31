"""library.py - Comic book library."""

import gtk
import pango
import gobject
import Image
import ImageDraw

import archive
import encoding
import librarybackend
from preferences import prefs
import image

_dialog = None
_COLLECTION_ALL = -1


class _LibraryDialog(gtk.Window):

    def __init__(self, window):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_size_request(400, 300)
        self.resize(prefs['lib window width'], prefs['lib window height'])
        self.set_title(_('Library'))
        self.connect('delete_event', self._close)

        self._window = window
        self._backend = librarybackend.LibraryBackend()
        self._stop_update = False

        self._icon_liststore = gtk.ListStore(gtk.gdk.Pixbuf, int)
        iconview = gtk.IconView(self._icon_liststore)
        iconview.set_pixbuf_column(0)
        iconview.connect('item_activated', self._open_book)
        iconview.connect('selection_changed', self._update_info)
        iconview.connect_after('drag_begin', self._drag_book_begin)
        iconview.connect('drag_data_get', self._drag_book_data_get)
        main_scrolled = gtk.ScrolledWindow()
        main_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        main_scrolled.add(iconview)
        iconview.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color())
        iconview.enable_model_drag_source(0,
            [('book', gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_MOVE)
        iconview.set_selection_mode(gtk.SELECTION_MULTIPLE)

        self._collection_treestore = gtk.TreeStore(str, int)
        treeview = gtk.TreeView(self._collection_treestore)
        treeview.connect('cursor_changed', self._change_collection)
        treeview.connect('drag_data_received', self._drag_book_end)
        treeview.connect('drag_motion', self._drag_book_motion)
        treeview.set_headers_visible(False)
        treeview.set_rules_hint(True)
        treeview.enable_model_drag_dest([('book', gtk.TARGET_SAME_APP, 0)],
            gtk.gdk.ACTION_MOVE)
        #treeview.set_reorderable(True)
        cellrenderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None, cellrenderer, markup=0)
        treeview.append_column(column)
        sidebar = gtk.ScrolledWindow()
        sidebar.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sidebar.add(treeview)

        self._statusbar = gtk.Statusbar()
        self._statusbar.set_has_resize_grip(True)

        # The bottom box
        bottombox = gtk.HBox(False, 20)
        bottombox.set_border_width(10)
        borderbox = gtk.EventBox()
        borderbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333'))
        borderbox.set_size_request(300, -1)
        insidebox = gtk.EventBox()
        insidebox.set_border_width(1)
        insidebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddb'))
        infobox = gtk.VBox(False, 5)
        infobox.set_border_width(10)
        bottombox.pack_start(borderbox, False, False)
        borderbox.add(insidebox)
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

        table = gtk.Table(2, 2, False)
        table.attach(sidebar, 0, 1, 0, 1, gtk.FILL, gtk.EXPAND|gtk.FILL)
        table.attach(main_scrolled, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL,
            gtk.EXPAND|gtk.FILL)
        table.attach(bottombox, 0, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.FILL)
        table.attach(self._statusbar, 0, 2, 2, 3, gtk.FILL, gtk.FILL)
        self.add(table)

        self._display_collections()
        self.show_all()

    def _display_covers(self, collection):
        """Display the books in <collection> in the IconView."""
        self._stop_update = False
        self._icon_liststore.clear()
        for i, book in enumerate(self._backend.get_books_in_collection(
          collection)):
            pixbuf = self._backend.get_book_cover(book[0])
            if pixbuf is None:
                continue
            pixbuf = image.fit_in_rectangle(pixbuf,
                int(0.67 * prefs['library cover size']),
                prefs['library cover size'])
            pixbuf = image.add_border(pixbuf, 2, 0xFFFFFFFF)
            self._icon_liststore.append([pixbuf, book[0]])
            if i % 15 == 0:
                while gtk.events_pending():
                    gtk.main_iteration(False)
                if self._stop_update:
                    return
        self._stop_update = True

    def _display_collections(self):
        """Display the library collections in the sidebar."""
        
        def _add(parent_iter, supercoll):
            for coll in self._backend.get_collections_in_collection(supercoll):
                child_iter = self._collection_treestore.append(parent_iter,
                    [coll[1], coll[0]])
                _add(child_iter, coll[0])

        self._collection_treestore.clear()
        self._collection_treestore.append(None, ['<b>%s</b>' % _('All books'),
            _COLLECTION_ALL])
        _add(None, None)

    def _change_collection(self, treeview):
        """Change the viewed collection (in the IconView) to the
        currently selected one in the sidebar."""
        cursor = treeview.get_cursor()
        if cursor is None:
            return
        iterator = self._collection_treestore.get_iter(cursor[0])
        collection = self._collection_treestore.get_value(iterator, 1)
        if collection == _COLLECTION_ALL:
            collection = None
        gobject.idle_add(self._display_covers, collection)

    def _update_info(self, iconview):
        """Update the info box using the currently selected book."""
        selected = iconview.get_selected_items()
        if not selected:
            return
        path = selected[0]
        iterator = self._icon_liststore.get_iter(path)
        book = self._icon_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        self._namelabel.set_text(info[1])
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(self._namelabel.get_text())))
        self._namelabel.set_attributes(attrlist)
        self._typelabel.set_text(archive.get_name(info[4]))
        self._pageslabel.set_text(_('%d pages') % info[3])
        self._sizelabel.set_text('%.1f MiB' % (info[5] / 1048576.0))

    def _drag_book_begin(self, iconview, context):
        """Create a cursor image for drag n drop from the library.

        This method relies on implementation details regarding PIL's 
        drawing functions and default font to produce good looking results.
        If those are changed in a future release of PIL, this method might
        produce bad looking output (e.g. non-centered text).
        
        It's also used with connect_after() to overwrite the cursor
        automatically created when using enable_model_drag_source(), so in
        essence it's a hack, an ugly hack, but at least it works."""
        selected = iconview.get_selected_items()
        icon_path = selected[-1]
        num_books = len(selected)
        iterator = self._icon_liststore.get_iter(icon_path)
        book = self._icon_liststore.get_value(iterator, 1)

        cover = self._backend.get_book_cover(book)
        cover = cover.scale_simple(cover.get_width() // 2,
            cover.get_height() // 2, gtk.gdk.INTERP_TILES)
        cover = image.add_border(cover, 1, 0xFFFFFFFF)
        cover = image.add_border(cover, 1)
        
        if num_books > 1:
            pointer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 100, 100)
            pointer.fill(0x00000000)
            cover_width = cover.get_width()
            cover_height = cover.get_height()
            cover.composite(pointer, 0, 0, cover_width, cover_height, 0, 0,
            1, 1, gtk.gdk.INTERP_TILES, 255)
            im = Image.new('RGBA', (30, 30), 0x00000000)
            draw = ImageDraw.Draw(im)
            draw.ellipse((0, 0, 29, 29), outline=(0, 0, 0), fill=(128, 0, 0))
            draw = ImageDraw.Draw(im)
            text = str(num_books)
            draw.text((15 - (6 * len(text) // 2), 9), text,
                fill=(255, 255, 255))
            circle = image.pil_to_pixbuf(im)
            circle.composite(pointer, cover_width - 15, cover_height - 20,
                29, 29, cover_width - 15, cover_height - 20, 1, 1,
                gtk.gdk.INTERP_TILES, 255)
        else:
            pointer = cover

        context.set_icon_pixbuf(pointer, -5, -5)

    def _drag_book_data_get(self, iconview, context, selection, *args):
        """Fill the SelectionData with (iconview) paths for the dragged books
        formatted as a string with each path separated by a comma."""
        paths = iconview.get_selected_items()
        text = ','.join([str(path[0]) for path in paths])
        selection.set('text/plain', 8, text)

    def _drag_book_end(self, treeview, context, x, y, selection, *args):
        """Move books dragged from the IconView to the target collection."""
        self._set_status_message('')
        src_collection, dest_collection = \
            self._drag_get_src_and_dest_collections(treeview, x, y)
        if src_collection == dest_collection:
            return
        for path_string in selection.get_text().split(','):
            iterator = self._icon_liststore.get_iter(int(path_string))
            book = self._icon_liststore.get_value(iterator, 1)
            if src_collection != _COLLECTION_ALL:
                self._backend.remove_book_from_collection(book, src_collection)
                self._icon_liststore.remove(iterator)
            if dest_collection != _COLLECTION_ALL:
                self._backend.add_book_to_collection(book, dest_collection)

    def _drag_book_motion(self, treeview, context, x, y, *args):
        """Set the statusbar text when hovering a drag-n-drop over a
        collection."""
        src_collection, dest_collection = \
            self._drag_get_src_and_dest_collections(treeview, x, y)
        if src_collection == dest_collection:
            self._set_status_message('')
            return
        if src_collection != _COLLECTION_ALL:
            src_name = self._backend.get_detailed_collection_info(
                src_collection)[1]
        if dest_collection != _COLLECTION_ALL:
            dest_name = self._backend.get_detailed_collection_info(
                dest_collection)[1]
        if dest_collection == _COLLECTION_ALL:
            self._set_status_message(_('Remove book(s) from "%s".') % src_name)
        elif src_collection == _COLLECTION_ALL:
            self._set_status_message(_('Add book(s) to "%s".') % dest_name)
        else:
            self._set_status_message(
                _('Move book(s) from "%s" to "%s".') % (src_name, dest_name))
        
    def _drag_get_src_and_dest_collections(self, treeview, x, y):
        """Convenience function to get the IDs for the source and
        destination collections during a drag-n-drop."""
        cursor = treeview.get_cursor()
        if cursor is None:
            return 0, 0
        iterator = self._collection_treestore.get_iter(cursor[0])
        src_collection = self._collection_treestore.get_value(iterator, 1)
        drop_row = treeview.get_dest_row_at_pos(x, y)
        if drop_row is None:
            return 0, 0
        iterator = self._collection_treestore.get_iter(drop_row[0])
        dest_collection = self._collection_treestore.get_value(iterator, 1)
        return src_collection, dest_collection
                
    def _set_status_message(self, message):
        """Set a specific message on the statusbar, replacing whatever was
        there earlier.
        """
        self._statusbar.pop(0)
        self._statusbar.push(0, ' %s' % encoding.to_unicode(message))

    def _open_book(self, iconview, path):
        """Open the book at the (liststore) <path>."""
        iterator = self._icon_liststore.get_iter(path)
        book = self._icon_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        path = info[2]
        self._close()
        self._window.file_handler.open_file(path)

    def _close(self, *args):
        """Close the library and do required cleanup tasks."""
        prefs['lib window width'], prefs['lib window height'] = self.get_size()
        self._stop_update = True
        self._backend.close()
        close_dialog()


def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        if librarybackend.dbapi2 is None:
            print '! You need an sqlite wrapper to use the library.'
        else:
            _dialog = _LibraryDialog(window)


def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None
