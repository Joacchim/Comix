# ============================================================================
# cursor.py - Cursor handler.
# ============================================================================

import gobject
import gtk

NORMAL, GRAB, WAIT = range(3)

class CursorHandler:
    
    def __init__(self, window):
        self._window = window
        self._timer_id = None
        self._fullscreen = False
        self._current_cursor = NORMAL

    def set_cursor_type(self, cursor):
        
        """ 
        Set the cursor to type <cursor>. Supported cursor types are available
        as constants in this module.
        """
        
        if cursor == NORMAL:
            mode = None
        elif cursor == GRAB:
            mode = gtk.gdk.Cursor(gtk.gdk.FLEUR)
        elif cursor == WAIT:
            mode = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self._window.set_cursor(mode)
        self._current_cursor = cursor
        if self._fullscreen:
            if cursor == NORMAL:
                self._set_hide_timer()
            else:
                self._kill_timer()
    
    def enter_fullscreen(self):
        self._fullscreen = True
        if self._current_cursor == NORMAL:
            self._set_hide_timer()

    def exit_fullscreen(self):
        self._fullscreen = False
        self._kill_timer()
        if self._current_cursor == NORMAL:
            self.set_cursor_type(NORMAL)

    def refresh(self):
        if self._fullscreen:
            self.set_cursor_type(self._current_cursor)

    def _set_hide_timer(self):
        self._kill_timer()
        self._timer_id = gobject.timeout_add(2000, self._window.set_cursor, 
            self._create_hidden_cursor())

    def _kill_timer(self):
        try:
            gobject.source_remove(self._timer_id)
        except:
            pass

    def _create_hidden_cursor(self):
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        color = gtk.gdk.Color()
        return gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)

