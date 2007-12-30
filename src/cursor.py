# ============================================================================
# cursor.py - Cursor handler for Comix.
# ============================================================================

import gtk

NORMAL = None
GRAB = gtk.gdk.Cursor(gtk.gdk.FLEUR)
WAIT = gtk.gdk.Cursor(gtk.gdk.WATCH)

def set_cursor_type(mode):
    
    """ 
    Sets the cursor to type <MODE>. Abbreviations of common cursor types
    are available in this module.
    """
    
    for window in gtk.gdk.window_get_toplevels():
        window.set_cursor(mode)

