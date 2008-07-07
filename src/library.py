"""library.py - Comic book library."""

import os
import md5
try:
    from sqlite3 import dbapi2
except ImportError:
    try:
        from pysqlite2 import dbapi2
    except ImportError:
        print '! Could not find pysqlite2 or sqlite3'
        dbapi2 = None

import gtk

import archive
import constants
from preferences import prefs
import thumbnail
import image

_dialog = None
_db_path = os.path.join(constants.COMIX_DIR, 'library.db')
_cover_dir = os.path.join(constants.COMIX_DIR, 'library_covers')

class _LibraryBackend:
    
    def __init__(self):
        self._con = dbapi2.connect(_db_path)
        if not self._con.execute('pragma table_info(Book)').fetchall():
            self._create_table_book()
        if not self._con.execute('pragma table_info(Collection)').fetchall():
            self._create_table_collection()
        if not self._con.execute('pragma table_info(Contain)').fetchall():
            self._create_table_contain()

    def get_book_cover(self, book):
        path = self._con.execute('''select path from Book
            where id=?''', (book,)).fetchone()[0]
        return thumbnail.get_thumbnail(path, create=False, dst_dir=_cover_dir)

    def get_detailed_book_info(self, book):
        cur = self._con.execute('''select * from Book
            where id=?''', (book,))
        return cur.fetchone()

    def get_books_in_collection(self, collection=None):
        if collection is None:
            cur = self._con.execute('''select id from Book
                order by name''')
        else:
            cur = self._con.execute('''select id from Book
                where id in (select book from Contain where collection=?)
                order by name''', (collection,))
        return cur

    def get_collections_in_collection(self, collection):
        cur = self._con.execute('''select id, name from Collection
            where supercollection=? 
            order by name''', (collection,))
        return cur

    def add_book(self, path):
        if not archive.archive_mime_type(path):
            return
        path = os.path.abspath(path)
        name = os.path.basename(path)
        format, pages, size = archive.get_archive_info(path)
        thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)
        try:
            self._con.execute('''insert into Book
                (name, path, pages, format, size) values (?, ?, ?, ?, ?)''',
                (name, path, pages, format, size))
        except dbapi2.Error:
            pass

    def add_collection(self, name):
        try:
            self._con.execute('''insert into Collection
                (name) values (?)''', (name,))
        except dbapi2.Error:
            pass

    def add_book_to_collection(self, book, collection):
        try:
            self._con.execute('''insert into Contain
                (collection, book) values (?, ?)''', (collection, book))
        except dbapi2.Error:
            pass

    def add_collection_to_collection(self, supercollection, subcollection):
        self._con.execute('''update Collection set supercollection = ?
            where id = ?''', (supercollection, subcollection))
    
    def remove_book(self, book):
        self._con.execute('delete from Book where id = ?', (book,))
        self._con.execute('delete from Contain where book = ?', (book,))

    def remove_collection(self, collection):
        self._con.execute('delete from Collection where id = ?', (collection,))
        self._con.execute('delete from Contain where collection = ?',
            (collection,))

    def remove_book_from_collection(self, book, collection):
        self._con.execute('''delete from Contain
            where book = ? and collection = ?''', (book, collection))

    def remove_collection_from_collection(self, subcollection):
        self._con.execute('''update Collection
            set supercollection = NULL
            where id = ?''', (subcollection,))

    def close(self):
        self._con.commit()
        self._con.close()

    def _create_table_book(self):
        print 'creating table Book...'
        self._con.execute('''create table book (
            id integer primary key,
            name string,
            path string unique,
            pages integer,
            format string,
            size integer,
            added date default current_date,
            read integer default 0,
            rating integer default 0)''')

    def _create_table_collection(self):
        print 'creating table Collection...'
        self._con.execute('''create table collection (
            id integer primary key,
            name string unique,
            supercollection integer)''')

    def _create_table_contain(self):
        print 'creating table Contain...'
        self._con.execute('''create table contain (
            collection integer not null,
            book integer not null,
            primary key (collection, book))''')

class _LibraryDialog(gtk.Window):

    def __init__(self, window):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_size_request(300, 300)
        self.resize(prefs['lib window width'], prefs['lib window height'])
        self.set_title(_('Library'))
        self.connect('delete_event', close_dialog)
        
        self._window = window
        self._backend = _LibraryBackend()
        
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
        self._iconview.modify_base(gtk.STATE_NORMAL,
            gtk.gdk.colormap_get_system().alloc_color(gtk.gdk.Color(
            *prefs['bg colour']), False, True))

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

        while gtk.events_pending():
            gtk.main_iteration(False)
        for i, book in enumerate(self._backend.get_books_in_collection()):
            pixbuf = self._backend.get_book_cover(book[0])
            pixbuf = image.fit_in_rectangle(pixbuf, 90, 128)
            pixbuf = image.add_border(pixbuf, 2, 0xFFFFFFFF)
            self._main_liststore.append([pixbuf, book[0]])
            if i % 15 == 0:
                while gtk.events_pending():
                    gtk.main_iteration(False)

    def _open_book(self, iconview, path):
        iterator = self._main_liststore.get_iter(path)
        book = self._main_liststore.get_value(iterator, 1)
        info = self._backend.get_detailed_book_info(book)
        path = info[2]
        close_dialog()
        self._window.file_handler.open_file(path)

    def close(self):
        self._backend.close()
        self.destroy()

def open_dialog(action, window):
    global _dialog
    if _dialog is None:
        _dialog = _LibraryDialog(window)

def close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.close()
        _dialog = None 

