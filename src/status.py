# ============================================================================
# status.py - Statusbar for Comix.
# ============================================================================

import gtk

import encoding

class Statusbar(gtk.Statusbar):

    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.set_has_resize_grip(True)
        self.page_info = ''
        self.resolution = ''
        self.filename = ''

    def set_message(self, message):
        
        """ 
        Sets a specific message (such as an error message) on the statusbar,
        replacing whatever was there earlier.
        """

        self.pop(0)
        self.push(0, ' %s' % encoding.to_unicode(message))

    def set_page_number(self, page, total, double_page=False):

        """ Updates the page number. """

        if double_page:
            self.page_info = '%d,%d / %d' % (page, page + 1, total)
        else:
            self.page_info = '%d / %d' % (page, total)

    def set_resolution(self, left_dimensions, right_dimensions=None):
        
        """
        Updates the resolution data.

        Takes one or two tuples, (x, y, scale), describing the original 
        resolution of an image as well as the currently displayed scale
        in percent.
        """

        self.resolution = '%dx%d (%.1f%%)' % left_dimensions
        if right_dimensions != None:
            self.resolution += ', %dx%d (%.1f%%)' % right_dimensions

    def set_filename(self, filename):
        
        """ Updates the filename. """
        
        self.filename = encoding.to_unicode(filename)

    def update(self):
        
        """ Updates the statusbar to display the current state. """

        self.pop(0)
        self.push(0, ' %s      |      %s      |      %s' %
            (self.page_info, self.resolution, self.filename))

