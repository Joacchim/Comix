"""mobiunpack.py - MobiPocket handling (extract pictures) for Comix.

Based on code from mobiunpack by Charles M. Hannum et al.
"""
from __future__ import absolute_import

import imghdr
import re
import struct


class unpackException(Exception):
    pass

class Sectionizer:
    def __init__(self, f):
        self.f = f
        header = self.f.read(78)
        self.ident = header[0x3C:0x3C+8]
        self.num_sections, = struct.unpack_from('>H', header, 76)
        sections = self.f.read(self.num_sections*8)
        self.sections = struct.unpack_from('>%dL' % (self.num_sections*2), sections, 0)[::2] + (0x7fffffff, )

    def loadSection(self, section, limit=0x7fffffff):
        before, after = self.sections[section:section+2]
        self.f.seek(before)
        if limit > after - before:
            limit = after - before
        return self.f.read(limit)

class MobiFile:
    def __init__(self, filename):
        f = file(filename, 'rb')
        try:
            self.file = f
            self.sect = Sectionizer(self.file)
            if self.sect.ident != 'BOOKMOBI':
                raise unpackException('invalid file format')

            self.header = self.sect.loadSection(0)
            self.crypto_type, = struct.unpack_from('>H', self.header, 0xC)
            if self.crypto_type != 0:
                raise unpackException('file is encrypted')
            self.firstimg, = struct.unpack_from('>L', self.header, 0x6C)
        except:
            self.file = None
            f.close()
            raise

    def getnames(self):
        names = []
        for i in xrange(self.firstimg, self.sect.num_sections):
            header = self.sect.loadSection(i, 32)
            imgtype = imghdr.what(None, header)
            if imgtype is not None:
                names.append("image%05d.%s" % (1+i-self.firstimg, imgtype))
        return names

    def extract(self, name, dst):
        fnparts = re.split('^image([0-9]*)\.', name)
        if len(fnparts) != 3:
            return
        i = int(fnparts[1])-1+self.firstimg
        data = self.sect.loadSection(i)
        f = open(dst, 'wb')
        f.write(data)
        f.close()

    def close(self):
        self.file.close()
