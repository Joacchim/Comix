"""librarybackend.py - Comic book library backend using sqlite."""

import os
try:
    from sqlite3 import dbapi2
except ImportError:
    try:
        from pysqlite2 import dbapi2
    except ImportError:
        print '! Could neither find pysqlite2 nor sqlite3.'
        dbapi2 = None

import archive
import constants
import thumbnail

_db_path = os.path.join(constants.COMIX_DIR, 'library.db')
_cover_dir = os.path.join(constants.COMIX_DIR, 'library_covers')


class LibraryBackend:
    
    """The LibraryBackend handles the storing and retrieval of library
    data to and from disk."""

    def __init__(self):
        if not os.path.exists(constants.COMIX_DIR):
            os.mkdir(constants.COMIX_DIR)

        self._con = dbapi2.connect(_db_path)
        if not self._con.execute('pragma table_info(Book)').fetchall():
            self._create_table_book()
        if not self._con.execute('pragma table_info(Collection)').fetchall():
            self._create_table_collection()
        if not self._con.execute('pragma table_info(Contain)').fetchall():
            self._create_table_contain()

    def get_book_cover(self, book):
        """Return a pixbuf with a thumbnail of the cover of <book>, or
        None if the cover can not be fetched.
        """
        try:
            path = self._con.execute('''select path from Book
                where id = ?''', (book,)).fetchone()[0]
        except Exception:
            print '! Non-existant book #%d' % book
            return None
        thumb = thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)
        if thumb is None:
            print '! Could not get cover for %s' % path
        return thumb

    def get_detailed_book_info(self, book):
        """Return a tuple with all the information about <book>, or None
        if <book> is not in the library.
        """
        cur = self._con.execute('''select * from Book
            where id = ?''', (book,))
        return cur.fetchone()

    def get_detailed_collection_info(self, collection):
        """Return a tuple with all the information about <collection>, or
        None if <collection> is not in the library.
        """
        cur = self._con.execute('''select * from Collection
            where id = ?''', (collection,))
        return cur.fetchone()

    def get_books_in_collection(self, collection=None):
        """Return a sequence with all the books in <collection>, or *ALL*
        books if <collection> is None."""
        if collection is None:
            cur = self._con.execute('''select id from Book
                order by path''')
        else:
            cur = self._con.execute('''select id from Book
                where id in (select book from Contain where collection = ?)
                order by path''', (collection,))
        return cur.fetchall()

    def get_collections_in_collection(self, collection=None):
        """Return a sequence with all the subcollections in <collection>,
        or all top-level collections if <collection> is None."""
        if collection is None:
            cur = self._con.execute('''select id, name from Collection
                where supercollection isnull
                order by name''')
        else:
            cur = self._con.execute('''select id, name from Collection
                where supercollection = ?
                order by name''', (collection,))
        return cur.fetchall()

    def get_collection_name(self, collection):
        """Return the name field of the <collection>, or None if the
        collection does not exist."""
        cur = self._con.execute('''select name from Collection
            where id = ?''', (collection,))
        return cur.fetchone()

    def add_book(self, path):
        """Add the archive at <path> to the library. Return True if the
        book was successfully added."""
        if not archive.archive_mime_type(path):
            return False
        path = os.path.abspath(path)
        name = os.path.basename(path)
        format, pages, size = archive.get_archive_info(path)
        thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)
        try:
            self._con.execute('''insert into Book
                (name, path, pages, format, size) values (?, ?, ?, ?, ?)''',
                (name, path, pages, format, size))
            return True
        except dbapi2.DatabaseError: # E.g. book already in library
            pass
        except dbapi2.Error:
            print '! Could not add book %s to the library' % path
        return False

    def add_collection(self, name):
        """Add a new collection with <name> to the library. Return True
        if the collection was successfully added."""
        try:
            self._con.execute('''insert into Collection
                (name) values (?)''', (name,))
            return True
        except dbapi2.Error:
            print '! Could not add collection %s' % name
        return False

    def add_book_to_collection(self, book, collection):
        """Put <book> into <collection>."""
        try:
            self._con.execute('''insert into Contain
                (collection, book) values (?, ?)''', (collection, book))
        except dbapi2.DatabaseError: # E.g. book already in collection.
            pass
        except dbapi2.Error:
            print '! Could not add book %s to collection %s' % (book,
                collection)

    def add_collection_to_collection(self, subcollection, supercollection):
        """Put <subcollection> into <supercollection>."""
        self._con.execute('''update Collection set supercollection = ?
            where id = ?''', (supercollection, subcollection))

    def rename_collection(self, collection, name):
        """Rename the <collection> to <name>. Return True if the renaming
        was successful."""
        try:
            self._con.execute('''update Collection set name = ?
                where id = ?''', (name, collection))
            return True
        except dbapi2.DatabaseError: # E.g. name taken.
            pass
        except dbapi2.Error:
            print '! Could not rename collection to %s' % name
        return False

    def duplicate_collection(self, collection):
        """Duplicate the <collection> by creating a new collection
        containing the same books. Return True if the duplication was
        successful.
        """
        name = self.get_collection_name(collection)
        if name is None: # Original collection does not exist.
            return False
        copy_name = _('%s (Copy)') % name
        if self.add_collection(copy_name) is None: # Could not create the new.
            return False
        copy_collection = self._con.execute('''select id from Collection
            where name = ?''', (copy_name,)).fetchone()[0]
        self._con.execute('''insert or ignore into Contain (collection, book)
            select ?, book from Contain
            where collection = ?''', (copy_collection, collection))
        return True

    def remove_book(self, book):
        """Remove the <book> from the library."""
        info = self.get_detailed_book_info(book)
        if info is not None:
            path = info[2]
            thumbnail.delete_thumbnail(path, dst_dir=_cover_dir)
        self._con.execute('delete from Book where id = ?', (book,))
        self._con.execute('delete from Contain where book = ?', (book,))

    def remove_collection(self, collection):
        """Remove the <collection> (sans books) from the library."""
        self._con.execute('delete from Collection where id = ?', (collection,))
        self._con.execute('delete from Contain where collection = ?',
            (collection,))
        self._con.execute('''update Collection set supercollection = NULL
            where supercollection = ?''', (collection,))

    def remove_book_from_collection(self, book, collection):
        """Remove <book> from <collection>."""
        self._con.execute('''delete from Contain
            where book = ? and collection = ?''', (book, collection))

    def remove_collection_from_collection(self, subcollection):
        """Remove <subcollection> from its supercollection."""
        self._con.execute('''update Collection
            set supercollection = NULL
            where id = ?''', (subcollection,))

    def close(self):
        """Commit changes and close cleanly."""
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
