# ========================================================================
# pilpixbuf.py - PIL/pixbuf conversion for Comix.
# ========================================================================

import gtk
import Image

def pil_to_pixbuf(image):
    imagestr = image.tostring()
    IS_RGBA =image.mode == 'RGBA'
    return gtk.gdk.pixbuf_new_from_data(imagestr, gtk.gdk.COLORSPACE_RGB,
        IS_RGBA, 8, image.size[0], image.size[1],
        (IS_RGBA and 4 or 3) * image.size[0])

def pixbuf_to_pil(pixbuf):
    dimensions = pixbuf.get_width(), pixbuf.get_height()
    stride = pixbuf.get_rowstride()
    pixels = pixbuf.get_pixels()
    mode = pixbuf.get_has_alpha() and 'RGBA' or 'RGB'
    return Image.frombuffer(mode, dimensions, pixels, 'raw', mode, stride, 1)

