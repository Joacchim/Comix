# ============================================================================
# scale.py - Image scaling module for Comix.
# ============================================================================

import gtk

import preferences

def fit_in_rectangle(src, width, height, interp=None, scale_up=False,
  rotation=0):
    
    """
    Returns a pixbuf from <src> scaled to fit into a rectangle with
    dimensions <width> x <height>. A negative <width> or <height> means an
    unbounded dimension, both cannot be negative.

    If rotation is 90, 180 or 270 we rotate <src> so that the rotated
    pixbuf is fitted in the rectangle.
    
    If <interp> is set it is used as the scaling method, otherwise the
    default value from preferences is used.
    
    Unless <scale_up> is True we don't stretch images smaller than the
    given rectangle.

    If <src> has an alpha channel it gets a checkboard background.
    """
    
    # "Unbounded" really means "bounded to 10000 px" - for simplicity.
    # Comix would choke on larger images anyway.
    if width < 0:
        width = 10000
    elif height < 0:
        height = 10000
    width = max(width, 1)
    height = max(height, 1)
    
    if rotation in [90, 270]:
        width, height = height, width

    if not scale_up and src.get_width() <= width and src.get_height() <= height:
        if src.get_has_alpha():
            src = src.composite_color_simple(src.get_width(), src.get_height(),
                gtk.gdk.INTERP_TILES, 255, 8, 0x777777, 0x999999)
    else:
        if float(src.get_width()) / width > float(src.get_height()) / height:
            height = max(src.get_height() * width / src.get_width(), 1)
        else:
            width = max(src.get_width() * height / src.get_height(), 1)

        if interp == None:
            interp = preferences.prefs['interp mode']
        if src.get_has_alpha():
            src = src.composite_color_simple(width, height, interp, 255, 8,
                0x777777, 0x999999)
        else:
            src = src.scale_simple(width, height, interp)

    if rotation == 90:
        src = src.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
    elif rotation == 180:
        src = src.rotate_simple(gtk.gdk.PIXBUF_ROTATE_UPSIDEDOWN)
    elif rotation == 270:
        src = src.rotate_simple(gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)
    return src

def fit_2_in_rectangle(src1, src2, width, height, interp=None, scale_up=False,
  rotation=0):
    
    """
    Returns a 2-tuple with two pixbufs scaled from <src1> and <src2>
    to fit together (side-by-side) into a rectangle with dimensions
    <width> x <height>. A negative <width> or <height> means an
    unbounded dimension, both cannot be negative.

    If rotation is 90, 180 or 270 we rotate the pixbufs.
    
    If <interp> is set it is used as the scaling method, otherwise the
    default value from preferences is used.
    
    Unless <scale_up> is True we don't stretch images smaller than the
    given rectangle.
    """

    # "Unbounded" really means "bounded to 10000 px" - for simplicity.
    # Comix would choke on larger images anyway.
    if width < 0:
        width = 10000
    elif height < 0:
        height = 10000
    
    width -= 2              # We got a 2 px gap between images
    width = max(width, 2)   # We need at least 1 px per image
    height = max(height, 1)

    total_width = src1.get_width() + src2.get_width()
    src1s_part = max(src1.get_width() * width / total_width, 1)
    
    src1s_max_scale = min(height / float(src1.get_height()), 
        src1s_part / float(src1.get_width()))
    src1s_part = round(src1.get_width() * src1s_max_scale)
    src1s_part = max(src1s_part, 1)

    src2s_part = max(width - src1s_part, 1)

    src2s_max_scale = min(height / float(src2.get_height()), 
        src2s_part / float(src2.get_width()))
    src2s_part = int(round(src2.get_width() * src2s_max_scale))

    src1s_part = int(max(width - src2s_part, 1))
    
    # FIXME: "Smart" scaling doesn't work properly when rotated
    return (
        fit_in_rectangle(src1, src1s_part, height, interp, scale_up, rotation),
        fit_in_rectangle(src2, src2s_part, height, interp, scale_up, rotation))

def add_border(pixbuf, thickness, colour=0x000000FF):

    """
    Returns a pixbuf from <pixbuf> with a <thickness> px border of 
    <colour> added.
    """

    canvas = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8,
        pixbuf.get_width() + thickness * 2,
        pixbuf.get_height() + thickness * 2)
    canvas.fill(colour)
    pixbuf.copy_area(0, 0, pixbuf.get_width(), pixbuf.get_height(),
        canvas, thickness, thickness)
    return canvas

