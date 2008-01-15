# ============================================================================
# slideshow.py - Slideshow module for Comix.
# ============================================================================

import gobject

from preferences import prefs

class Slideshow:
    
    def __init__(self, window):
        self._window = window
        self._running = False
        self._id = None

    def _start(self):
        if self._running == False:
            self._id = gobject.timeout_add(prefs['slideshow delay'], self._next)
            self._running = True

    def _stop(self):
        if self._running == True:
            gobject.source_remove(self._id)
            self._running = False

    def _next(self):
        if self._window.file_handler.is_last_page():
            self._window.ui_manager.get_action(
                '/Menu/menu_go/slideshow').set_active(False)
            self._running = False
            return False
        self._window.next_page()
        return True
    
    def toggle(self, action):
        active = action.get_active()
        if active:
            self._start()
        else:
            self._stop()

