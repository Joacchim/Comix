"""librarybackend.py - Comic book library backend using sqlite."""

import os
try:
    from sqlite3 import dbapi2
except ImportError:
    try:
        from pysqlite2 import dbapi2
    except ImportError:
        print '! Could not find pysqlite2 or sqlite3'
        dbapi2 = None

import archive
import constants
import thumbnail

_db_path = os.path.join(constants.COMIX_DIR, 'library.db')
_cover_dir = os.path.join(constants.COMIX_DIR, 'library_covers')

class LibraryBackend:
    
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
        return thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)

    def get_detailed_book_info(self, book):
        cur = self._con.execute('''select * from Book
            where id=?''', (book,))
        return cur.fetchone()

    def get_books_in_collection(self, collection=None):
        if collection is None:
            cur = self._con.execute('''select id from Book
                order by path''')
        else:
            cur = self._con.execute('''select id from Book
                where id in (select book from Contain where collection=?)
                order by path''', (collection,))
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

