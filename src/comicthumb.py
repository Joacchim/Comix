#!/usr/bin/env python

"""comicthumb - Thumbnailer for comic book archives, bundled with Comix.

comicthumb is dependent on the Python Imaging Library (PIL).

comicthumb was originally written by Christoph Wolk, this version was
re-written from scratch for Comix 4 by Pontus Ekberg. 

Supported formats: ZIP, RAR, 7Z and tar (.cbz, .cbr, .cb7, .cbt)

Usage: comicthumb INFILE OUTFILE [SIZE]
"""

import sys

try:
    import Image
except ImportError:
    print '! Could not import the Image module (PIL).'
    print __doc__
    sys.exit(1)


from archive import Extractor
from thumbnail import _guess_cover as guess_cover

if __name__ == '__main__':
    try:
        in_path = sys.argv[1]
        out_path = sys.argv[2]
        if len(sys.argv) == 4:
            size = int(sys.argv[3])
        else:
            size = 128
    except:
        print __doc__
        sys.exit(1)
    extractor = Extractor()
    extractor.setup(in_path, None)
    files = extractor.get_files()
    chosen = guess_cover(files)
    fd = extractor.extract_file_io(chosen)
    im = Image.open(fd)
    if im.size[0] > im.size[1]:
        x = size
        y = size * im.size[1] / im.size[0]
    else:
        x = size * im.size[0] / im.size[1]
        y = size
    x = max(1, x)
    y = max(1, y)
    im.thumbnail((x, y), Image.ANTIALIAS)
    im = im.convert('RGB')
    im.save(out_path, 'PNG')
    sys.exit(0)
