# coding=utf-8
"""librarybackend.py - Comic book library backend using sqlite."""
from __future__ import absolute_import

import os
from sqlite3 import dbapi2

from src import archive
from src import constants
from src import encoding
from src import thumbnail

_db_path = os.path.join(constants.DATA_DIR, 'library.db')
_cover_dir = os.path.join(constants.DATA_DIR, 'library_covers')


class LibraryBackend(object):
    """The LibraryBackend handles the storing and retrieval of library
    data to and from disk.
    """

    def __init__(self):

        def row_factory(cursor, row):
            """Return rows as sequences only when they have more than
            one element.
            """
            if len(row) == 1:
                return row[0]
            return row

        self._con = dbapi2.connect(_db_path)
        self._con.row_factory = row_factory
        self._con.text_factory = str
        if not self._con.execute('PRAGMA table_info(Book)').fetchall():
            self._create_table_book()
        if not self._con.execute('PRAGMA table_info(Collection)').fetchall():
            self._create_table_collection()
        if not self._con.execute('PRAGMA table_info(Contain)').fetchall():
            self._create_table_contain()

    def get_books_in_collection(self, collection=None, filter_string=None):
        """Return a sequence with all the books in <collection>, or *ALL*
        books if <collection> is None. If <filter_string> is not None, we
        only return books where the <filter_string> occurs in the path.
        """
        if collection is None:
            if filter_string is None:
                cur = self._con.execute('''SELECT id FROM Book
                    ORDER BY path''')
            else:
                cur = self._con.execute('''SELECT id FROM Book
                    WHERE path LIKE ?
                    ORDER BY path''', ("%%%s%%" % filter_string,))
        else:
            if filter_string is None:
                cur = self._con.execute('''SELECT id FROM Book
                    WHERE id IN (SELECT book FROM Contain WHERE collection = ?)
                    ORDER BY path''', (collection,))
            else:
                cur = self._con.execute('''SELECT id FROM Book
                    WHERE id IN (SELECT book FROM Contain WHERE collection = ?)
                    AND path LIKE ?
                    ORDER BY path''', (collection, "%%%s%%" % filter_string))
        return cur.fetchall()

    def get_book_cover(self, book):
        """Return a pixbuf with a thumbnail of the cover of <book>, or
        None if the cover can not be fetched.
        """
        try:
            path = self._con.execute('''SELECT path FROM Book
                WHERE id = ?''', (book,)).fetchone()
        except Exception:
            print('! Non-existant book #{:d}'.format(book))
            return None
        thumb = thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)
        if thumb is None:
            print('! Could not get cover for {}'.format(path))
        return thumb

    def get_book_path(self, book):
        """Return the filesystem path to <book>, or None if <book> isn't
        in the library.
        """
        cur = self._con.execute('''SELECT path FROM Book
            WHERE id = ?''', (book,))
        return cur.fetchone()

    def get_book_name(self, book):
        """Return the name of <book>, or None if <book> isn't in the
        library.
        """
        cur = self._con.execute('''SELECT name FROM Book
            WHERE id = ?''', (book,))
        name = cur.fetchone()
        if name is None:
            return None
        return encoding.to_unicode(name)

    def get_book_pages(self, book):
        """Return the number of pages in <book>, or None if <book> isn't
        in the library.
        """
        cur = self._con.execute('''SELECT pages FROM Book
            WHERE id = ?''', (book,))
        return cur.fetchone()

    def get_book_format(self, book):
        """Return the archive format of <book>, or None if <book> isn't
        in the library.
        """
        cur = self._con.execute('''SELECT format FROM Book
            WHERE id = ?''', (book,))
        return cur.fetchone()

    def get_book_size(self, book):
        """Return the size of <book> in bytes, or None if <book> isn't
        in the library.
        """
        cur = self._con.execute('''SELECT size FROM Book
            WHERE id = ?''', (book,))
        return cur.fetchone()

    def get_collections_in_collection(self, collection=None):
        """Return a sequence with all the subcollections in <collection>,
        or all top-level collections if <collection> is None.
        """
        if collection is None:
            cur = self._con.execute('''SELECT id FROM Collection
                WHERE supercollection ISNULL
                ORDER BY name''')
        else:
            cur = self._con.execute('''SELECT id FROM Collection
                WHERE supercollection = ?
                ORDER BY name''', (collection,))
        return cur.fetchall()

    def get_all_collections(self):
        """Return a sequence with all collections (flattened hierarchy).
        The sequence is sorted alphabetically by collection name.
        """
        cur = self._con.execute('''SELECT id FROM Collection
            ORDER BY name''')
        return cur.fetchall()

    def get_collection_name(self, collection):
        """Return the name field of the <collection>, or None if the
        collection does not exist.
        """
        cur = self._con.execute('''SELECT name FROM Collection
            WHERE id = ?''', (collection,))
        name = cur.fetchone()
        if name is None:
            return None
        return unicode(name)

    def get_collection_by_name(self, name):
        """Return the collection called <name>, or None if no such
        collection exists. Names are unique, so at most one such collection
        can exist.
        """
        cur = self._con.execute('''SELECT id FROM Collection
            WHERE name = ?''', (name,))
        return cur.fetchone()

    def get_supercollection(self, collection):
        """Return the supercollection of <collection>."""
        cur = self._con.execute('''SELECT supercollection FROM Collection
            WHERE id = ?''', (collection,))
        return cur.fetchone()

    def add_book(self, path, collection=None):
        """Add the archive at <path> to the library. If <collection> is
        not None, it is the collection that the books should be put in.
        Return True if the book was successfully added (or was already
        added).
        """
        path = os.path.abspath(path)
        name = os.path.basename(path)
        info = archive.get_archive_info(path)
        if info is None:
            return False
        format, pages, size = info
        thumbnail.get_thumbnail(path, create=True, dst_dir=_cover_dir)
        old = self._con.execute('''SELECT id FROM Book
            WHERE path = ?''', (path,)).fetchone()
        try:
            if old is not None:
                self._con.execute('''UPDATE Book SET
                    name = ?, pages = ?, format = ?, size = ?
                    WHERE path = ?''', (name, pages, format, size, path))
            else:
                self._con.execute('''INSERT INTO Book
                    (name, path, pages, format, size)
                    VALUES (?, ?, ?, ?, ?)''',
                                  (name, path, pages, format, size))
        except dbapi2.Error:
            print('! Could not add book {} to the library'.format(path))
            return False
        if collection is not None:
            book = self._con.execute('''SELECT id FROM Book
                WHERE path = ?''', (path,)).fetchone()
            self.add_book_to_collection(book, collection)
        return True

    def add_collection(self, name):
        """Add a new collection with <name> to the library. Return True
        if the collection was successfully added.
        """
        try:
            self._con.execute('''INSERT INTO Collection
                (name) VALUES (?)''', (name,))
            return True
        except dbapi2.Error:
            print('! Could not add collection {}'.format(name))
        return False

    def add_book_to_collection(self, book, collection):
        """Put <book> into <collection>."""
        try:
            self._con.execute('''INSERT INTO Contain
                (collection, book) VALUES (?, ?)''', (collection, book))
        except dbapi2.DatabaseError:  # E.g. book already in collection.
            pass
        except dbapi2.Error:
            print('! Could not add book {} to collection {}'.format(book,
                                                                    collection))

    def add_collection_to_collection(self, subcollection, supercollection):
        """Put <subcollection> into <supercollection>, or put
        <subcollection> in the root if <supercollection> is None.
        """
        if supercollection is None:
            self._con.execute('''UPDATE Collection
                SET supercollection = NULL
                WHERE id = ?''', (subcollection,))
        else:
            self._con.execute('''UPDATE Collection
                SET supercollection = ?
                WHERE id = ?''', (supercollection, subcollection))

    def rename_collection(self, collection, name):
        """Rename the <collection> to <name>. Return True if the renaming
        was successful.
        """
        try:
            self._con.execute('''UPDATE Collection SET name = ?
                WHERE id = ?''', (name, collection))
            return True
        except dbapi2.DatabaseError:  # E.g. name taken.
            pass
        except dbapi2.Error:
            print('! Could not rename collection to {}'.format(name))
        return False

    def duplicate_collection(self, collection):
        """Duplicate the <collection> by creating a new collection
        containing the same books. Return True if the duplication was
        successful.
        """
        name = self.get_collection_name(collection)
        if name is None:  # Original collection does not exist.
            return False
        copy_name = name + ' ' + _('(Copy)')
        while self.get_collection_by_name(copy_name):
            copy_name = copy_name + ' ' + _('(Copy)')
        if self.add_collection(copy_name) is None:  # Could not create the new.
            return False
        copy_collection = self._con.execute('''SELECT id FROM Collection
            WHERE name = ?''', (copy_name,)).fetchone()
        self._con.execute('''INSERT OR IGNORE INTO Contain (collection, book)
            SELECT ?, book FROM Contain
            WHERE collection = ?''', (copy_collection, collection))
        return True

    def remove_book(self, book):
        """Remove the <book> from the library."""
        path = self.get_book_path(book)
        if path is not None:
            thumbnail.delete_thumbnail(path, dst_dir=_cover_dir)
        self._con.execute('DELETE FROM Book WHERE id = ?', (book,))
        self._con.execute('DELETE FROM Contain WHERE book = ?', (book,))

    def remove_collection(self, collection):
        """Remove the <collection> (sans books) from the library."""
        self._con.execute('DELETE FROM Collection WHERE id = ?', (collection,))
        self._con.execute('DELETE FROM Contain WHERE collection = ?',
                          (collection,))
        self._con.execute('''UPDATE Collection SET supercollection = NULL
            WHERE supercollection = ?''', (collection,))

    def remove_book_from_collection(self, book, collection):
        """Remove <book> from <collection>."""
        self._con.execute('''DELETE FROM Contain
            WHERE book = ? AND collection = ?''', (book, collection))

    def close(self):
        """Commit changes and close cleanly."""
        self._con.commit()
        self._con.close()

    def _create_table_book(self):
        self._con.execute('''CREATE TABLE book (
            id INTEGER PRIMARY KEY,
            name string,
            path string UNIQUE,
            pages INTEGER,
            format INTEGER,
            size INTEGER,
            added DATE DEFAULT current_date)''')

    def _create_table_collection(self):
        self._con.execute('''CREATE TABLE collection (
            id INTEGER PRIMARY KEY,
            name string UNIQUE,
            supercollection INTEGER)''')

    def _create_table_contain(self):
        self._con.execute('''CREATE TABLE contain (
            collection INTEGER NOT NULL,
            book INTEGER NOT NULL,
            PRIMARY KEY (collection, book))''')
