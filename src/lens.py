# ============================================================================
# lens.py - Magnifying glass.
# ============================================================================

from preferences import prefs

class MagnifyingGlass:
    
    def __init__(self, window):
        self._window = window
    
    def set_lens_cursor(self, event):
        x, y = event.get_coords()
        self._layout_coords_to_pixbuf_coords(x, y)

    def _layout_coords_to_pixbuf_coords(self, x, y, pixbuf, left=True):
        
        """
        Return the coordinates on the source <pixbuf> that the coordinates
        <x>, <y> on the main layout area map to. If <first> is False,
        calculate the positions on the second source <pixbuf> (in double
        page mode.)
        """
        
        visible_x, visible_y = self._window.get_visible_area_size()
        full_x, full_y = self._window.get_full_area_size()
        padding_x = max(0, (visible_x - full_x) // 2)
        padding_y = max(0, (visible_y - full_y) // 2)
        
        x -= padding_x
        y -= padding_y
            
    
    def _get_lens_pixbuf(self):
        pass

    def _get_source_subpixbufs(self):
        pass

