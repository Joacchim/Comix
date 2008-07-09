"""labels.py - gtk.Label convenience functions."""

import gtk
import pango

def bold_label(text):
    """Return a bold gtk.Label with <text>."""
    label = gtk.Label(text)
    attrlist = pango.AttrList()
    attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
        len(text)))
    label.set_attributes(attrlist)
    return label

def italic_label(text):
    """Return an italic gtk.Label with <text>."""
    label = gtk.Label(text)
    attrlist = pango.AttrList()
    attrlist.insert(pango.AttrStyle(pango.STYLE_ITALIC, 0,
        len(text)))
    label.set_attributes(attrlist)
    return label

