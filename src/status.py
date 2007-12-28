# ============================================================================
# status.py - Statusbar for Comix.
# ============================================================================

import gtk

class Statusbar(gtk.Statusbar):

    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.set_has_resize_grip(True)
        self.page_info = ''
        self.resolution = ''
        self.filename = ''
        self.message = ''

    def set_message(self, message):
        
        """ 
        Sets a message (such as an error message) on the statusbar, removing
        what was there earlier.
        """

        self.message = message
        self._push_message()

    def set_page_number(self, page, total, double_page=False):

        """ Updates the page number and (re)displays the reading info. """

        if double_page:
            self.page_info = '%d,%d / %d' % (page, page + 1, total)
        else:
            self.page_info = '%d / %d' % (page, total)
        self._push_reading_info()

    def set_resolution(self, left_dimensions, right_dimensions=None):
        
        """
        Updates the resolution data and (re)displays the reading info.

        Takes one or two tuples, (x, y, scale), describing the original 
        resolution of an image as well as the currently displayed scale
        in percent.
        """

        self.resolution = '%dx%d (%.1f%%)' % left_dimensions
        if right_dimensions != None:
            self.resolution += ', %dx%d (%.1f%%)' % right_dimensions
        self._push_reading_info()

    def set_filename(self, filename):   
        
        """ Updates the filename and (re)displays the reading info. """
        
        self.filename = filename
        self._push_reading_info()

    def _push_reading_info(self):
        self.pop(0)
        self.push(0, ' %s      |      %s      |      %s' %
            (self.page_info, self.resolution, self.filename))

    def _push_message(self):
        self.pop(0)
        self.push(0, ' %s' % self.message)
 
