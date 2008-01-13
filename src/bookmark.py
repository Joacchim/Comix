# ============================================================================
# bookmark.py - Bookmarks handler for Comix.
# ============================================================================

import os
import cPickle

import gtk

import constants
import image
import thumbnail

_pickle_path = os.path.join(constants.COMIX_DIR, 'bookmarks_pickle')

class _Bookmark(gtk.ImageMenuItem):
    
    def __init__(self, file_handler, name, path, page, numpages):
        self._name = name
        self._path = path
        self._page = page
        self._numpages = numpages
        self._file_handler = file_handler
        
        gtk.MenuItem.__init__(self, str(self), False)
        self.connect('activate', self._load)
    
    def __str__(self):
        return '%s, (%d / %d)' % (self._name, self._page, self._numpages)

    def _load(self, *args):
        self._file_handler.open_file(self._path, self._page)

    def same(self, path):
        return path == self._path

    def pack(self):
        return (self._name, self._path, self._page, self._numpages)


class BookmarksMenu(gtk.Menu):
    
    def __init__(self, ui, window):
        gtk.Menu.__init__(self)

        self._window = window
        self._bookmarks = []
        self._actiongroup = gtk.ActionGroup('comix-bookmarks')
        self._actiongroup.add_actions([
            ('add_bookmark', 'comix-add-bookmark', _('_Add bookmark'),
                '<Control>d', None, self._add_current_to_bookmarks),
            ('clear_bookmarks', gtk.STOCK_CLEAR, _('Clear bookmarks'),
                None, None, self._clear_bookmarks),
            ('edit_bookmarks', None, _('_Edit bookmarks...'),
                '<Control>b', None, self._edit_bookmarks)])
        self._separator = gtk.SeparatorMenuItem()

        action = self._actiongroup.get_action('add_bookmark')
        action.set_accel_group(ui.get_accel_group())
        self.append(action.create_menu_item())
        action = self._actiongroup.get_action('edit_bookmarks')
        action.set_accel_group(ui.get_accel_group())
        self.append(action.create_menu_item())
        self.append(self._separator)
        self.append(gtk.SeparatorMenuItem())
        action = self._actiongroup.get_action('clear_bookmarks')
        action.set_accel_group(ui.get_accel_group())
        self.append(action.create_menu_item())

        self.show_all()
        self._separator.hide()

        if os.path.isfile(_pickle_path):
            try:
                fd = open(_pickle_path)
                version = cPickle.load(fd)
                packs = cPickle.load(fd)
                for pack in packs:
                    self._add_bookmark(*pack)
                fd.close()
            except:
                print '! bookmark.py: Could not read', _pickle_path
                os.remove(_pickle_path)
                self._bookmarks = []
    
    def _add_bookmark(self, name, path, page, numpages):
        
        """ Adds a bookmark. """
        
        bookmark = _Bookmark(self._window.file_handler, name, path, page,
            numpages)
        self._bookmarks.append(bookmark)
        self.insert(bookmark, 3)
        bookmark.show()
        self._separator.show()

    def _add_current_to_bookmarks(self, *args):
        
        """ Adds the currently viewed file to the bookmarks. """
        
        name = self._window.file_handler.get_pretty_current_filename()
        path = self._window.file_handler.get_real_path()
        page = self._window.file_handler.get_current_page()
        numpages = self._window.file_handler.get_number_of_pages()
        for bookmark in self._bookmarks:
            if bookmark.same(path):
                self._remove_bookmark(bookmark)
                break
        self._add_bookmark(name, path, page, numpages)

    def _edit_bookmarks(self, *args):
        print 'edit bookmarks'

    def _remove_bookmark(self, bookmark):
        
        """ Remove the bookmark <bookmark>. """

        self.remove(bookmark)
        self._bookmarks.remove(bookmark)
        if not self._bookmarks:
            self._separator.hide()

    def _clear_bookmarks(self, *args):
        
        """ Removes all bookmarks. """

        for bookmark in self._bookmarks[:]:
            self._remove_bookmark(bookmark)

    def store_bookmarks(self):
        
        """ Stores relevant bookmark info in the comix directory """

        fd = open(_pickle_path, 'w')
        cPickle.dump(constants.VERSION, fd, cPickle.HIGHEST_PROTOCOL)
        packs = [bookmark.pack() for bookmark in self._bookmarks]
        cPickle.dump(packs, fd, cPickle.HIGHEST_PROTOCOL)
        fd.close()

    def set_sensitive(self, sensitive):
        self._actiongroup.get_action('add_bookmark').set_sensitive(sensitive)

