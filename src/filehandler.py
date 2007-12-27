# ============================================================================
# filehandler.py - File handler for Comix. Opens files and keeps track
# of images, pages and caches.
# ============================================================================

import os
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
        self.window = window
        self.file_loaded = False
        self.archive_type = None
        self.archive_path = None
        self.tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
        self.image_files = []
        self.current_image = None
        self.comment_files = []
        self.current_comment = None
        self.raw_pixbufs = {}

    def _get_pixbuf(self, page):
        
        """
        Returns the pixbuf for <page> from cache.
        Pixbufs not found in cache are fetched from disk first. 
        """

        if not self.raw_pixbufs.has_key(page):
            try:
                self.raw_pixbufs[page] = gtk.gdk.pixbuf_new_from_file(
                    self.image_files[page])
            except:
                self.raw_pixbufs[page] = \
                    gtk.image_new_from_stock(
                    gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON).get_pixbuf()
        return self.raw_pixbufs[page]

    def get_pixbufs(self):

        """
        Returns the pixbuf for the current image from cache.
        Returns two pixbufs if needed in double_page mode.
        Pixbufs not found in cache are fetched from disk first. 
        """

        if not self.window.displayed_double():
            return self._get_pixbuf(self.current_image)
        return (self._get_pixbuf(self.current_image),
                self._get_pixbuf(self.current_image + 1))

    def do_cacheing(self):

        """
        Makes sure that the correct pixbufs are stored in cache. These
        are the current image(s) and if cacheing is enabled also the one or two
        pixbufs after them. All other pixbufs are deleted and garbage collected
        in order to save memory.
        """

        offset = self.window.is_double_page and 2 or 1
        if prefs['cache']:
            offset *= 2
        wanted_pixbufs = range(self.current_image, 
            min(self.current_image + offset, len(self.image_files)))
        
        # --------------------------------------------------------------------
        # Remove old pixbufs.
        # --------------------------------------------------------------------
        for page in self.raw_pixbufs.keys()[:]:
            if not page in wanted_pixbufs:
                del self.raw_pixbufs[page]
        gc.collect() # FIXME: Add generation for Python >= 2.5
        
        # --------------------------------------------------------------------
        # Cache new pixbufs if not already cached.
        # --------------------------------------------------------------------
        for wanted in wanted_pixbufs:
            if not self.raw_pixbufs.has_key(wanted):
                try:
                    self.raw_pixbufs[wanted] = gtk.gdk.pixbuf_new_from_file(
                        self.image_files[wanted])
                except:
                    self.raw_pixbufs[wanted] = gtk.image_new_from_stock(
                        gtk.STOCK_MISSING_IMAGE,
                        gtk.ICON_SIZE_BUTTON).get_pixbuf()

    def is_last_page(self):
        
        """ Returns True if at the last page. """

        return self.current_image == len(self.image_files) - 1

    def next_page(self):

        """
        Sets up filehandler to the next page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        old_image = self.current_image
        step = self.window.is_double_page and 2 or 1
        if self.current_image >= len(self.image_files) - step:
            if prefs['go to next archive']:
                #open_file(NEXT_ARCHIVE)
                print 'open next archive'
                return True
            else:
                return False
        self.current_image += step
        self.current_image = min(len(self.image_files) - 1, self.current_image)
        return old_image != self.current_image

    def previous_page(self):

        """
        Sets up filehandler to the previous page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        old_image = self.current_image
        step = self.window.is_double_page and 2 or 1
        if self.current_image <= step - 1:
            if prefs['go to next archive']:
                #open_file(PREVIOUS_ARCHIVE)
                print 'open previous archive'
                return True
            else:
                return False
        self.current_image -= step
        self.current_image = max(0, self.current_image)
        return old_image != self.current_image

    def first_page(self):

        """
        Sets up filehandler to the first page. Returns True if this is not
        the same page, False otherwise.
        """

        if not self.file_loaded:
            return False
        old_image = self.current_image
        self.current_image = 0
        return old_image != self.current_image

    def last_page(self):

        """ 
        Sets up filehandler to the last page. Returns True if this is not
        the same page, False otherwise.
        """
        
        if not self.file_loaded:
            return False
        old_image = self.current_image
        offset = self.window.is_double_page and 2 or 1
        self.current_image = max(0, len(self.image_files) - offset)
        return old_image != self.current_image

    def set_page(self, page_num):

        """ 
        Sets up filehandler to the page <page_num>. Returns True if this is
        not the same page, False otherwise.
        """

        old_image = self.current_image
        if not 0 <= page_num < len(self.image_files):
            return
        self.current_image = page_num
        return old_image != self.current_image

    def open_file(self, path, start_image=0):

        """
        If <path> is an image we add all images in its directory to the
        image_files and all comments to the comment_files. We set current_image
        to point to <path>.

        If <path> is an archive we decompresses it to the tmp_dir and adds all
        images in the decompressed tree to image_files and all comments to
        comment_files. If <start_image> is not set we set current_image to 0
        (first image), if it is set we set it to the value of <start_image>.
        If <start_image> is negative it means the last image.
        """
        
        # --------------------------------------------------------------------
        # If the given path is invalid.
        # --------------------------------------------------------------------
        if not os.path.isfile(path):
            if os.path.isdir(path):
                self.window.statusbar.push(0, _('"%s" is not a file.') % 
                    encoding.to_unicode(os.path.basename(path)))
            else:
                self.window.statusbar.push(0, _('"%s" does not exist.') % 
                    encoding.to_unicode(os.path.basename(path)))
            return False

        self.archive_type = archive.archive_mime_type(path)
            
        if not self.archive_type and not is_image_file(path):
            self.window.statusbar.push(0,
                _('Filetype of "%s" not recognized.') %
                encoding.to_unicode(os.path.basename(path)))
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
            self.archive_path = path
            archive.extract_archive(path, self.tmp_dir)
            # FIXME: Nested archives
            for dirname, dirs, files in os.walk(self.tmp_dir):
                for f in files:
                    if is_image_file(os.path.join(dirname, f)):
                        self.image_files.append(os.path.join(dirname, f))
                    elif (os.path.splitext(f)[1].lower() in
                      prefs['comment extensions']):
                        self.comment_files.append(os.path.join(dirname, f))
            self.image_files.sort() # We don't sort archives after locale
            if start_image < 0:
                if self.window.is_double_page:
                    self.current_image = len(self.image_files) - 2
                else:
                    self.current_image = len(self.image_files) - 1
            else:
                self.current_image = start_image
            self.current_image = max(0, self.current_image)

        # --------------------------------------------------------------------
        # If <path> is an image we scan it's directory for more images and
        # comments.
        # --------------------------------------------------------------------
        else:
            self.archive_path = os.path.dirname(path)
            for f in os.listdir(os.path.dirname(path)):
                fpath = os.path.join(os.path.dirname(path), f)
                if os.path.isdir(fpath):
                    continue
                if is_image_file(fpath):
                    self.image_files.append(fpath)
                elif (os.path.splitext(f)[1].lower() in 
                  prefs['comment extensions']):
                    self.comment_files.append(fpath)
            self.image_files.sort(locale.strcoll)
            self.current_image = self.image_files.index(path)

        # --------------------------------------------------------------------
        # If there are no viewable image files found.
        # --------------------------------------------------------------------
        if not self.image_files:
            self.window.statusbar.push(0, _('No images in "%s"') % 
                encoding.to_unicode(os.path.basename(path)))
            self.file_loaded = False
        else:
            self.file_loaded = True

        if not self.window.keep_rotation:
            self.window.rotation = 0
        self.window.thumbnailsidebar.block = True
        self.window.draw_image()
        cursor.set_cursor_type(cursor.NORMAL)
        while gtk.events_pending():
            gtk.main_iteration(False)
        self.window.thumbnailsidebar.block = False
        self.window.thumbnailsidebar.load_thumbnails()
        self.comment_files.sort()

    def close_file(self, *args):
        self.file_loaded = False
        self.archive_path = None
        shutil.rmtree(self.tmp_dir)
        self.tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
        self.image_files = []
        self.current_image = None
        self.comment_files = []
        self.current_comment = None
        self.raw_pixbufs.clear()
        self.window.thumbnailsidebar.clear()
        self.window.draw_image()
        gc.collect()

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

