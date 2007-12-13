# ============================================================================
# filehandler.py - File handler for Comix. Opens files and keeps track
# of images, pages and caches.
# ============================================================================

import os
import shutil
import locale
import tempfile
import gtk
import gc
import shutil

import archive
#import cursor
import preferences
import main
import encoding
import thumbnail

file_loaded = False
archive_type = None
archive_path = None
tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
image_files = []
current_image = None
comment_files = []
current_comment = None
raw_pixbufs = {}

def get_pixbufs():

    """
    Returns the pixbuf for the current image from cache.
    Returns two pixbufs if needed in double_page mode.
    Pixbufs not found in cache are fetched from disk first. 
    """

    global current_image
    global image_files
    global raw_pixbufs

    # --------------------------------------------------------------------
    # Get first pixbuf from disk if not in cache.
    # --------------------------------------------------------------------
    if not raw_pixbufs.has_key(current_image):
        try:
            raw_pixbufs[current_image] = gtk.gdk.pixbuf_new_from_file(
                image_files[current_image])
        except:
            raw_pixbufs[current_image] = gtk.image_new_from_stock(
                gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON).get_pixbuf()

    if not main.is_double():
        return raw_pixbufs[current_image]

    # --------------------------------------------------------------------
    # Get second pixbuf from disk if not in cache (double_page).
    # --------------------------------------------------------------------
    else:
        if not raw_pixbufs.has_key(current_image + 1):
            try:
                raw_pixbufs[current_image + 1] = gtk.gdk.pixbuf_new_from_file(
                    image_files[current_image + 1])
            except:
                raw_pixbufs[current_image + 1] = gtk.image_new_from_stock(
                    gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON).get_pixbuf()
        return raw_pixbufs[current_image], raw_pixbufs[current_image + 1]

def do_cacheing():

    """
    Makes sure that the correct pixbufs are stored in cache. These
    are the current image(s) and if cacheing is enabled also the one or two
    pixbufs after them. All other pixbufs are deleted and garbage collected
    in order to save memory.
    """

    global current_image
    global image_files
    global raw_pixbufs

    offset = main.window.double_page and 2 or 1
    if preferences.prefs['cache']:
        offset *= 2
    wanted_pixbufs = range(current_image, 
        min(current_image + offset, len(image_files)))
    
    # --------------------------------------------------------------------
    # Remove old pixbufs.
    # --------------------------------------------------------------------
    for page in raw_pixbufs.keys()[:]:
        if not page in wanted_pixbufs:
            del raw_pixbufs[page]
    gc.collect() # FIXME: Add generation for Python >= 2.5
    
    # --------------------------------------------------------------------
    # Cache new pixbufs if not already cached.
    # --------------------------------------------------------------------
    for wanted in wanted_pixbufs:
        if not raw_pixbufs.has_key(wanted):
            try:
                raw_pixbufs[wanted] = gtk.gdk.pixbuf_new_from_file(
                    image_files[wanted])
            except:
                raw_pixbufs[wanted] = gtk.image_new_from_stock(
                    gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON).get_pixbuf()

def is_last_page():
    global image_files
    global current_image
    return current_image == len(image_files) - 1

def next_page():

    """
    Sets up filehandler to the next page. Returns True if this is not
    the same page, False otherwise.
    """

    global image_files
    global current_image

    if not file_loaded:
        return False
    old_image = current_image
    step = main.window.double_page and 2 or 1
    if current_image >= len(image_files) - step:
        if preferences.prefs['go to next archive']:
            #open_file(NEXT_ARCHIVE)
            print 'open next archive'
            return True
        else:
            return False
    current_image += step
    current_image = min(len(image_files) - 1, current_image)
    return old_image != current_image

def previous_page():

    """
    Sets up filehandler to the previous page. Returns True if this is not
    the same page, False otherwise.
    """

    global image_files
    global current_image
    
    if not file_loaded:
        return False
    old_image = current_image
    step = main.window.double_page and 2 or 1
    if current_image <= step - 1:
        if preferences.prefs['go to next archive']:
            #open_file(PREVIOUS_ARCHIVE)
            print 'open previous archive'
            return True
        else:
            return False
    current_image -= step
    current_image = max(0, current_image)
    return old_image != current_image

def first_page():

    """
    Sets up filehandler to the first page. Returns True if this is not
    the same page, False otherwise.
    """

    global current_image
    
    if not file_loaded:
        return False
    old_image = current_image
    current_image = 0
    return old_image != current_image

def last_page():

    """ 
    Sets up filehandler to the last page. Returns True if this is not
    the same page, False otherwise.
    """

    global current_image
    global image_files
    
    if not file_loaded:
        return False
    old_image = current_image
    offset = main.window.double_page and 2 or 1
    current_image = max(0, len(image_files) - offset)
    return old_image != current_image

def set_page(page_num):

    """ 
    Sets up filehandler to the page <page_num>. Returns True if this is
    not the same page, False otherwise.
    """

    global current_image
    global image_files

    old_image = current_image
    if not 0 <= page_num < len(image_files):
        return
    current_image = page_num
    return old_image != current_image

def open_file(path, start_image=0):

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
    
    global file_loaded
    global archive_type
    global archive_path
    global tmp_dir
    global image_files
    global current_image
    global comment_files
    global current_comment
    global raw_pixbufs

    # --------------------------------------------------------------------
    # If the given path is invalid.
    # --------------------------------------------------------------------
    if not os.path.isfile(path):
        if os.path.isdir(path):
            main.window.statusbar.push(0, _('"%s" is not a file.') % 
                encoding.to_unicode(os.path.basename(path)))
            print 'not a file'
        else:
            main.window.statusbar.push(0, _('"%s" does not exist.') % 
                encoding.to_unicode(os.path.basename(path)))
            print 'does not exist'
        return False

    archive_type = archive.archive_mime_type(path)
        
    if not archive_type and not is_image_file(path):
        main.window.statusbar.push(0, _('Filetype of "%s" not recognized.') %
            encoding.to_unicode(os.path.basename(path)))
        print 'Unknown filetype!'
        return False

    #cursor.set_cursor('watch')
    close_file()

    # --------------------------------------------------------------------
    # If <path> is an archive we extract it and walk down the extracted
    # tree to find images and comments.
    # --------------------------------------------------------------------
    if archive_type:
        archive_path = path
        archive.extract_archive(path, tmp_dir)
        # FIXME: Nested archives
        for dirname, dirs, files in os.walk(tmp_dir):
            for f in files:
                if is_image_file(os.path.join(dirname, f)):
                    image_files.append(os.path.join(dirname, f))
                elif (os.path.splitext(f)[1].lower() in
                  preferences.prefs['comment extensions']):
                    comment_files.append(os.path.join(dirname, f))
        image_files.sort() # We don't sort archives after locale
        if start_image < 0:
            if main.double_page:
                current_image = len(image_files) - 2
            else:
                current_image = len(image_files) - 1
        else:
            current_image = start_image
        current_image = max(0, current_image)

    # --------------------------------------------------------------------
    # If <path> is an image we scan it's directory for more images and
    # comments.
    # --------------------------------------------------------------------
    else:
        archive_path = os.path.dirname(path)
        for f in os.listdir(os.path.dirname(path)):
            fpath = os.path.join(os.path.dirname(path), f)
            if os.path.isdir(fpath):
                continue
            if is_image_file(fpath):
                image_files.append(fpath)
            elif (os.path.splitext(f)[1].lower() in 
              preferences.prefs['comment extensions']):
                comment_files.append(fpath)
        image_files.sort(locale.strcoll)
        current_image = image_files.index(path)

    # --------------------------------------------------------------------
    # If there are no viewable image files found.
    # --------------------------------------------------------------------
    if not image_files:
        main.window.statusbar.push(0, _('No images in "%s"') % 
            encoding.to_unicode(os.path.basename(path)))
        print 'No images in', path
        file_loaded = False
    else:
        file_loaded = True

    if not main.window.keep_rotation:
        main.window.rotation = 0
    main.window.draw_image()
    main.window.thumbnailsidebar.load_thumbnails()

    comment_files.sort()
    #cursor.set_cursor(None)

def close_file(*args):
    global file_loaded
    global archive_path
    global tmp_dir
    global image_files
    global current_image
    global comment_files
    global current_comment
    global raw_pixbufs

    file_loaded = False
    archive_path = None
    shutil.rmtree(tmp_dir)
    tmp_dir = tempfile.mkdtemp(prefix="comix.", suffix="/")
    image_files = []
    current_image = None
    comment_files = []
    current_comment = None
    raw_pixbufs.clear()
    main.window.thumbnailsidebar.clear()
    main.window.draw_image()
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

