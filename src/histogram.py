# ============================================================================
# histogram.py - Draws histograms from image data for Comix.
# ============================================================================

import gtk
import Image
import ImageDraw
import ImageOps
import ImageStat

def draw_histogram(pixbuf):
    
    ''' Draws a histogram from <pixbuf> and returns it as another
    pixbuf together with some statistics from PIL. '''

    dimensions = pixbuf.get_width(), pixbuf.get_height()
    stride = pixbuf.get_rowstride()
    pixels = pixbuf.get_pixels()
    mode = pixbuf.get_has_alpha() and 'RGBA' or 'RGB'
    pil_image = \
        Image.frombuffer(mode, dimensions, pixels, 'raw', mode, stride, 1)
    hist_data = pil_image.histogram()
    hist_rgb_im = Image.new('RGB', (256, 150), (50, 50, 50))
    maximum = \
        max(hist_data[:768] + [1])
    y_scale = float(150) / maximum
    for x in xrange(256):
        r = int(hist_data[x] * y_scale)
        g = int(hist_data[x + 256] * y_scale)
        b = int(hist_data[x + 512] * y_scale)
        for y, val in enumerate(reversed(xrange(150))):
            hist_rgb_im.putpixel((x, y), (255 * (r > val),
                255 * (g > val), 255 * (b > val)))
    maxstr = 'max: ' + str(maximum)
    draw = ImageDraw.Draw(hist_rgb_im)
    draw.rectangle((0, 0, len(maxstr) * 6 + 2, 10), fill=(0, 0, 0))
    draw.text((2, 0), maxstr, fill=(255, 255, 255))
    hist_rgb_im = ImageOps.expand(hist_rgb_im, 2, (50, 50, 50))
    hist_rgb_im = ImageOps.expand(hist_rgb_im, 1, (0, 0, 0))
    imagestr = hist_rgb_im.tostring()
    IS_RGBA = hist_rgb_im.mode == 'RGBA'
    hist_rgb_pixbuf = \
        gtk.gdk.pixbuf_new_from_data(imagestr,
        gtk.gdk.COLORSPACE_RGB, IS_RGBA, 8,
        hist_rgb_im.size[0], hist_rgb_im.size[1],
        (IS_RGBA and 4 or 3) * hist_rgb_im.size[0])
    stat = ImageStat.Stat(pil_image)
    return (hist_rgb_pixbuf, stat.mean, stat.median, stat.stddev,
        stat.count[0], stat.sum, stat.extrema)

