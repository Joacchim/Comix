# ========================================================================
# thumbnail.py - Thumbnail module for Comix implementing the 
# freedesktop.org "standard" at http://jens.triq.net/thumbnail-spec/
# ========================================================================

import os
from urllib import pathname2url, url2pathname
import md5

import gtk
import Image

import constants

thumbdir = os.path.join(os.getenv('HOME'), '.thumbnails/normal')

def _uri_to_thumbpath(uri):
    md5hash = md5.new(uri).hexdigest()
    thumbpath = os.path.join(thumbdir, md5hash + '.png')
    return thumbpath

def _get_pixbuf128(path):
    try:
        return gtk.gdk.pixbuf_new_from_file_at_size(path, 128, 128)
    except:
        return None

def create_thumbnail(path):
    pixbuf = _get_pixbuf128(path)
    uri = 'file://' + pathname2url(path)
    thumbpath = _uri_to_thumbpath(uri)
    stat = os.stat(path)
    mtime = str(stat.st_mtime)
    size = str(stat.st_size)
    mime, width, height = gtk.gdk.pixbuf_get_file_info(path)
    mime = mime['mime_types'][0]
    width = str(width)
    height = str(height)
    tEXt_data = {
        'tEXt::Thumb::URI':           uri,
        'tEXt::Thumb::MTime':         mtime,
        'tEXt::Thumb::Size':          size,
        'tEXt::Thumb::Mimetype':      mime,
        'tEXt::Thumb::Image::Width':  width,
        'tEXt::Thumb::Image::Height': height,
        'tEXt::Software':             'Comix ' + str(constants.version)
    }
    try:
        if not os.path.isdir(thumbdir):
            os.makedirs(thumbdir, 0700)
        pixbuf.save(thumbpath + 'comixtemp', 'png', tEXt_data)
        os.rename(thumbpath + 'comixtemp', thumbpath)
        os.chmod(thumbpath, 0600)
    except:
        print 'thumbnail.py: Could not write', thumbpath
        return None
    return pixbuf

def get_thumbnail(path, create=True):
    uri = 'file://' + pathname2url(path)
    thumbpath = _uri_to_thumbpath(uri)
    if not os.path.exists(thumbpath):
        if create:
            return create_thumbnail(path)
        return _get_pixbuf128(path)
    thumbnail = gtk.gdk.pixbuf_new_from_file(thumbpath)
    info = Image.open(thumbpath).info
    if (not info.has_key('Thumb::MTime') or 
      os.stat(path).st_mtime != int(info['Thumb::MTime'])):
        if create:
            return create_thumbnail(path)
        return _get_pixbuf128(path)
    return thumbnail

