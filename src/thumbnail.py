# ============================================================================
# thumbnail.py - Thumbnail module for Comix implementing (most of) the
# freedesktop.org "standard" at http://jens.triq.net/thumbnail-spec/
#
# Only 128x128 px thumbnails are supported.
# ============================================================================

import os
from urllib import pathname2url, url2pathname
import md5

import gtk
import Image

import constants
import filehandler

_thumbdir = os.path.join(os.getenv('HOME'), '.thumbnails/normal')

def _uri_to_thumbpath(uri):
    md5hash = md5.new(uri).hexdigest()
    thumbpath = os.path.join(_thumbdir, md5hash + '.png')
    return thumbpath

def _get_pixbuf128(path):
    try:
        return gtk.gdk.pixbuf_new_from_file_at_size(path, 128, 128)
    except:
        return None

def create_thumbnail(path):
    
    """
    Create a thumbnail from the file at <path> and store it in the standard
    thumbnail directory. A pixbuf for the thumbnail is returned.
    """

    pixbuf = _get_pixbuf128(path)
    if pixbuf == None:
        return None
    mime, width, height = gtk.gdk.pixbuf_get_file_info(path)
    if width <= 128 and height <= 128:
        return pixbuf
    mime = mime['mime_types'][0]
    uri = 'file://' + pathname2url(os.path.normpath(path))
    thumbpath = _uri_to_thumbpath(uri)
    stat = os.stat(path)
    mtime = str(stat.st_mtime)
    size = str(stat.st_size)
    width = str(width)
    height = str(height)
    tEXt_data = {
        'tEXt::Thumb::URI':           uri,
        'tEXt::Thumb::MTime':         mtime,
        'tEXt::Thumb::Size':          size,
        'tEXt::Thumb::Mimetype':      mime,
        'tEXt::Thumb::Image::Width':  width,
        'tEXt::Thumb::Image::Height': height,
        'tEXt::Software':             'Comix ' + str(constants.VERSION)
    }
    try:
        if not os.path.isdir(_thumbdir):
            os.makedirs(_thumbdir, 0700)
        pixbuf.save(thumbpath + 'comixtemp', 'png', tEXt_data)
        os.rename(thumbpath + 'comixtemp', thumbpath)
        os.chmod(thumbpath, 0600)
    except:
        print '! thumbnail.py: Could not write', thumbpath, '\n'
    return pixbuf

def get_thumbnail(path, create=True):
    
    """
    Get a thumbnail pixbuf for the file at <path> by looking in the
    directory of stored thumbnails. If a thumbnail for the file doesn't
    exist we create a thumbnail pixbuf from the original. If <create>
    is True we also save this new thumbnail in the thumbnail directory.
    If no thumbnail for <path> can be produced (for whatever reason), 
    return None.
    """

    uri = 'file://' + pathname2url(os.path.normpath(path))
    thumbpath = _uri_to_thumbpath(uri)
    if not os.path.exists(thumbpath):
        if create:
            return create_thumbnail(path)
        return _get_pixbuf128(path)
    try:
        info = Image.open(thumbpath).info
        if (not info.has_key('Thumb::MTime') or 
        os.stat(path).st_mtime != int(info['Thumb::MTime'])):
            if create:
                return create_thumbnail(path)
            return _get_pixbuf128(path)
        return gtk.gdk.pixbuf_new_from_file(thumbpath)
    except:
        return None

