# ============================================================================
# histogram.py - Draws histograms from pixbufs for Comix.
# ============================================================================

import gtk
import Image
import ImageDraw
import ImageOps

import pilpixbuf

def get_histogram(pixbuf, height=150, fill=170, text=True):
    
    """
    Draws a histogram from <pixbuf> and returns it as another pixbuf.

    The returned prixbuf will be 256x<height> px. 

    The value of <fill> determines the colour intensity of the filled graphs,
    valid values are between 0 and 255.

    If <text> is True a label with the maximum pixel value will be added to
    one corner.

    FIXME: Could probably be optimized.
    """
    
    im = Image.new('RGB', (256, height - 1), (30, 30, 30))
    hist_data = pilpixbuf.pixbuf_to_pil(pixbuf).histogram()
    maximum = max(hist_data[:768] + [1])
    y_scale = float(height - 2) / maximum
    r = [int(hist_data[n] * y_scale) for n in xrange(256)]
    g = [int(hist_data[n] * y_scale) for n in xrange(256, 512)]
    b = [int(hist_data[n] * y_scale) for n in xrange(512, 768)]
    im_data = im.getdata()
    # Draw the filling colours
    for x in xrange(256):
        for y in xrange(0, max(r[x], g[x], b[x]) + 1):
            r_px = y <= r[x] and fill or 0
            g_px = y <= g[x] and fill or 0 
            b_px = y <= b[x] and fill or 0 
            im_data.putpixel((x, height - 2 - y), (r_px, g_px, b_px))
    # Draw the outlines
    for x in xrange(1, 256):
        for y in range(r[x-1] + 1, r[x] + 1) + [r[x]]:
            r_px, g_px, b_px = im_data.getpixel((x, height - 2 - y))
            im_data.putpixel((x, height - 2 - y), (255, g_px, b_px))
        for y in range(r[x] + 1, r[x-1] + 1):
            r_px, g_px, b_px = im_data.getpixel((x - 1, height - 2 - y))
            im_data.putpixel((x - 1, height - 2 - y), (255, g_px, b_px))
        for y in range(g[x-1] + 1, g[x] + 1) + [g[x]]:
            r_px, g_px, b_px = im_data.getpixel((x, height - 2 - y))
            im_data.putpixel((x, height - 2 - y), (r_px, 255, b_px))
        for y in range(g[x] + 1, g[x-1] + 1):
            r_px, g_px, b_px = im_data.getpixel((x - 1, height - 2 - y))
            im_data.putpixel((x - 1, height - 2 - y), (r_px, 255, b_px))
        for y in range(b[x-1] + 1, b[x] + 1) + [b[x]]:
            r_px, g_px, b_px = im_data.getpixel((x, height - 2 - y))
            im_data.putpixel((x, height - 2 - y), (r_px, g_px, 255))
        for y in range(b[x] + 1, b[x-1] + 1):
            r_px, g_px, b_px = im_data.getpixel((x - 1, height - 2 - y))
            im_data.putpixel((x - 1, height - 2 - y), (r_px, g_px, 255))
    if text:
        maxstr = 'max: ' + str(maximum)
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, len(maxstr) * 6 + 2, 10), fill=(0, 0, 0))
        draw.text((2, 0), maxstr, fill=(255, 255, 255))
    im = ImageOps.expand(im, 1, (0, 0, 0))
    return pilpixbuf.pil_to_pixbuf(im)

