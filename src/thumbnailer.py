import gtk

import scale

def pixbuf_to_pixbuf(src, width, height, border=0, border_colour=0x00000000):
    
    ''' Returns a gtk.gdk.Pixbuf made from the gtk.gdk.Pixbuf <src> fitted 
    into a rectangle with dimensions <width> and <height>. If <border> is 
    not None, a <border> pixel thick border with <border_colour> is added. '''
    
    if border > width / 2:
        border = width / 2 - 1
    if border > height / 2:
        border = height / 2 - 1

    thumb = scale.fit_in_rectangle(src, width - border * 2, height - border * 2, 
        interp=gtk.gdk.INTERP_TILES, scale_up=True)
    if border != 0:
        border_thumb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
            thumb.get_width() + border * 2, thumb.get_height() + border * 2)
        border_thumb.fill(border_colour)
        thumb.copy_area(0, 0, thumb.get_width(), thumb.get_height(),
            border_thumb, border, border)
        return border_thumb
    return thumb

def file_to_pixbuf(path, width, height, border=0, border_colour=0x00000000):
    if border > width / 2:
        border = width / 2 - 1
    if border > height / 2:
        border = height / 2 - 1

    try:
        thumb = gtk.gdk.pixbuf_new_from_file_at_size(path, width - border * 2,
            height - border * 2)
    except:
        print 'thumbnailer.py: Failed to load', path
        return
    if border != 0:
        border_thumb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
            thumb.get_width() + border * 2, thumb.get_height() + border * 2)
        border_thumb.fill(border_colour)
        thumb.copy_area(0, 0, thumb.get_width(), thumb.get_height(),
            border_thumb, border, border)
        return border_thumb
    return thumb

def pixbuf_to_file(src, width, height, dst_path, border=0, 
  border_colour=0x00000000):
    thumb = pixbuf_to_pixbuf(src, width, height, border, border_colour)
    try:
        thumb.save(dst_path, 'png') #FIXME: extra thumb data
    except:
        print 'thumbnailer.py: Failed to save', dst_path

def file_to_file(src_path, width, height, dst_path, border=0,
  border_colour=0x00000000):
    thumb = file_to_pixbuf(src_path, width, height, border, border_colour)
    try:
        thumb.save(dst_path, 'png') #FIXME: extra thumb data
    except:
        print 'thumbnailer.py: Failed to save', dst_path

