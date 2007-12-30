# ============================================================================
# filehandler.py - File handler for Comix. Opens files and keeps track
# of images, pages and caches.
# ============================================================================

import os
import sys
import shutil
import locale
import tempfile
import gc
import shutil

import gtk

import archive
import cursor
import encoding
from preferences import prefs

class FileHandler:

    def __init__(self, window):
        self.file_loaded = False
        self.archive_type = None
        
        self._base_path = None
        self._window = window
        self._tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
        self._image_files = []
        self._current_image_index = None
        self._comment_files = []
        self._current_comment_index = None
        self._raw_pixbufs = {}

    def _get_pixbuf(self, page):
        
        """
        Returns the pixbuf for <page> from cache.
        Pixbufs not found in cache are fetched from disk first. 
        """

        if not self._raw_pixbufs.has_key(page):
            try:
                self._raw_pixbufs[page] = gtk.gdk.pixbuf_new_from_file(
                    self._image_files[page])
            except:
                self._raw_pixbufs[page] = gtk.image_new_from_stock(
                    gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON).get_pixbuf()
        return self._raw_pixbufs[page]

    def get_pixbufs(self, single=False):

        """
        Returns the pixbuf(s) for the current image(s) from cache.
        Returns two pixbufs in double-page mode unless <single> is True.
        Pixbufs not found in cache are fetched from disk first. 
        """

        if not self._window.displayed_double() or single:
            return self._get_pixbuf(self._current_image_index)
        return (self._get_pixbuf(self._current_image_index),
                self._get_pixbuf(self._current_image_index + 1))

    def do_cacheing(self):

        """
        Makes sure that the correct pixbufs are stored in cache. These
        are the current image(s) and if cacheing is enabled also the one or two
        pixbufs before and after them. All other pixbufs are deleted and
        garbage collected in order to save memory.
        """
        
        # Get list of wanted pixbufs.
        viewed = self._window.is_double_page and 2 or 1
        if prefs['cache']:
            wanted_pixbufs = range(max(0, self._current_image_index - viewed), 
                min(self._current_image_index + viewed * 2,
                    self.number_of_pages()))
        else:
            wanted_pixbufs = range(self._current_image_index, 
                min(self._current_image_index + viewed, self.number_of_pages()))
        
        # Remove old pixbufs.
        for page in self._raw_pixbufs.keys()[:]:
            if not page in wanted_pixbufs:
                del self._raw_pixbufs[page]
        if sys.version_info[:3] >= (2, 5, 0):
            gc.collect(0)  # FIXME: Try this!
        else:
            gc.collect()

        # Cache new pixbufs if not already cached.
        for wanted in wanted_pixbufs:
            self._get_pixbuf(wanted)

    def number_of_pages(self):
        
        """ Returns the number of pages in the current archive/directory. """

        return len(self._image_files)

    def current_page(self):
        
        """ Returns the current page number. """

        return self._current_image_index + 1

    def is_last_page(self):
        
        """ Returns True if at the last page. """

        return self.current_page() == self.number_of_pages()

    def number_of_comments(self):
        
        """
        Returns the number of comments in the current archive/directory.
        """

        return len(self._comment_files)

    def current_comment(self):
        
        """ Returns the current comment number. """

        return self._current_comment_index + 1

    def next_page(self):

        """
        Sets up filehandler to the next page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        old_image = self.current_page()
        step = self._window.is_double_page and 2 or 1
        if self.current_page() + step > self.number_of_pages():
            if prefs['auto open next archive']:
                #open_file(NEXT_ARCHIVE)
                print 'open next archive'
            return False
        self._current_image_index += step
        self._current_image_index = min(self.number_of_pages() - 1,
            self._current_image_index)
        return old_image != self.current_page()

    def previous_page(self):

        """
        Sets up filehandler to the previous page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        if self.current_page() == 1:
            if prefs['auto open next archive']:
                #open_file(PREVIOUS_ARCHIVE)
                print 'open previous archive'
            return False
        old_image = self.current_page()
        step = self._window.is_double_page and 2 or 1
        self._current_image_index -= step
        self._current_image_index = max(0, self._current_image_index)
        return old_image != self.current_page()

    def first_page(self):

        """
        Sets up filehandler to the first page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        old_image = self.current_page()
        self._current_image_index = 0
        return old_image != self.current_page()

    def last_page(self):

        """ 
        Sets up filehandler to the last page. Returns True if this is not
        the same page, False otherwise.
        """
        
        if not self.file_loaded:
            return False
        old_image = self.current_page()
        offset = self._window.is_double_page and 2 or 1
        self._current_image_index = max(0, self.number_of_pages() - offset)
        return old_image != self.current_page()

    def set_page(self, page_num):

        """ 
        Sets up filehandler to the page <page_num>. Returns True if this is
        not the same page, False otherwise.
        """

        old_image = self.current_page()
        if not 0 < page_num <= self.number_of_pages():
            return False
        self._current_image_index = page_num - 1
        return old_image != self.current_page()

    def open_file(self, path, start_page=1):

        """
        If <path> is an image we add all images in its directory to the
        image_files and all comments to the comment_files. We set current_image
        to point to <path>.

        If <path> is an archive we decompresses it to the tmp_dir and adds all
        images in the decompressed tree to image_files and all comments to
        comment_files. If <start_image> is not set we set current page to 1
        (first page), if it is set we set it to the value of <start_page>.
        If <start_page> is non-positive it means the last image.
        """
        
        # --------------------------------------------------------------------
        # If the given <path> is invalid we update the statusbar.
        # --------------------------------------------------------------------
        if not os.path.isfile(path):
            if os.path.isdir(path):
                self._window.statusbar.set_message(_('"%s" is not a file.') % 
                    os.path.basename(path))
            else:
                self._window.statusbar.set_message(_('"%s" does not exist.') % 
                    os.path.basename(path))
            return False

        self.archive_type = archive.archive_mime_type(path)
            
        if not self.archive_type and not is_image_file(path):
            self._window.statusbar.set_message(
                _('Filetype of "%s" not recognized.') % os.path.basename(path))
            return False

        cursor.set_cursor_type(cursor.WAIT)
        self.close_file()
        while gtk.events_pending():
            gtk.main_iteration(False)

        # --------------------------------------------------------------------
        # If <path> is an archive we extract it and walk down the extracted
        # tree to find images and comments.
        # --------------------------------------------------------------------
        if self.archive_type:
            self._base_path = path
            archive.extract_archive(path, self._tmp_dir)
            # FIXME: Nested archives
            for dirname, dirs, files in os.walk(self._tmp_dir):
                for f in files:
                    if is_image_file(os.path.join(dirname, f)):
                        self._image_files.append(os.path.join(dirname, f))
                    elif (os.path.splitext(f)[1].lower() in
                      prefs['comment extensions']):
                        self._comment_files.append(os.path.join(dirname, f))
            self._image_files.sort()  # We don't sort archives after locale
            if start_page <= 0:
                if self._window.is_double_page:
                    self._current_image_index = self.number_of_pages() - 2
                else:
                    self._current_image_index = self.number_of_pages() - 1
            else:
                self._current_image_index = start_page - 1
            self._current_image_index = max(0, self._current_image_index)

        # --------------------------------------------------------------------
        # If <path> is an image we scan it's directory for more images and
        # comments.
        # --------------------------------------------------------------------
        else:
            self._base_path = os.path.dirname(path)
            for f in os.listdir(os.path.dirname(path)):
                fpath = os.path.join(os.path.dirname(path), f)
                if os.path.isdir(fpath):
                    continue
                if is_image_file(fpath):
                    self._image_files.append(fpath)
                elif (os.path.splitext(f)[1].lower() in 
                  prefs['comment extensions']):
                    self._comment_files.append(fpath)
            self._image_files.sort(locale.strcoll)
            self._current_image_index = self._image_files.index(path)

        # --------------------------------------------------------------------
        # If there are no viewable image files found.
        # --------------------------------------------------------------------
        if not self._image_files:
            self._window.statusbar.set_message(_('No images in "%s"') % 
                os.path.basename(path))
            self.file_loaded = False
        else:
            self.file_loaded = True

        self._window.thumbnailsidebar.block()
        self._window.new_page()
        cursor.set_cursor_type(cursor.NORMAL)
        while gtk.events_pending():
            gtk.main_iteration(False)
        self._window.thumbnailsidebar.unblock()
        self._window.thumbnailsidebar.load_thumbnails()
        self._comment_files.sort()

    def close_file(self, *args):
        self.file_loaded = False
        self._base_path = None
        shutil.rmtree(self._tmp_dir)
        self._tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
        self._image_files = []
        self._current_image_index = None
        self._comment_files = []
        self._current_comment_index = None
        self._raw_pixbufs.clear()
        self._window.thumbnailsidebar.clear()
        self._window.draw_image()
        gc.collect()

    def cleanup(self):
        shutil.rmtree(self._tmp_dir)

    def get_pretty_current_filename(self):
        
        """
        Returns a string with the name of the currently viewed file that is
        suitable for printing.
        """

        if self.archive_type:
            return os.path.basename(self._base_path)
        return os.path.join(os.path.basename(self._base_path),
            os.path.basename(self._image_files[self._current_image_index]))

    def get_path_to_page(self, page=None):
        
        """
        Returns the full path to the image file for <page>, or the current
        page if <page> is None.
        """

        if page == None:
            return self._image_files[self._current_image_index]
        return self._image_files[page - 1]

    def get_path_to_base(self):
        
        """
        Returns the full path to the current base (path to archive or
        image directory.
        """

        return self._base_path

def is_image_file(path):
    
    ''' Returns the mime type if <path> is an image file in a
    supported format, else False.
    '''
    
    if os.path.isfile(path): 
        info = gtk.gdk.pixbuf_get_file_info(path)
        if (info != None and info[0]['mime_types'][0]
            in ['image/jpeg', 'image/bmp', 'image/gif',
            'image/png', 'image/tiff', 'image/x-icon',
            'image/x-xpixmap', 'image/x-xbitmap', 'image/svg+xml',
            'image/svg', 'image/svg-xml', 'image/vnd.adobe.svg+xml',
            'text/xml-svg', 'image/x-portable-anymap',
            'image/x-portable-bitmap', 'image/x-portable-graymap',
            'image/x-portable-pixmap', 'image/x-pcx',
            'image/x-cmu-raster', 'image/x-sun-raster', 
            'image/x-tga']):
                return info[0]['mime_types'][0]
    return False

