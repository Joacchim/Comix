# ============================================================================
# main.py - Main window.
# ============================================================================

import sys
import os
import shutil
import time

import gtk

import constants
import cursor
import encoding
import enhance
import event
import filehandler
import image
import preferences
from preferences import prefs
import ui
import slideshow
import status
import thumbbar

class MainWindow(gtk.Window):
    
    """
    The Comix main window, is created at start and terminates the program
    when closed.
    """

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        # ----------------------------------------------------------------
        # Attributes
        # ----------------------------------------------------------------
        self.is_fullscreen = False
        self.is_double_page = False 
        self.is_manga_mode = False
        self.zoom_mode = 'fit'          # 'fit', 'width', 'height' or 'manual'
        self.width = None
        self.height = None

        self._keep_rotation = False
        self._manual_zoom = 100         # In percent of original image size
        self._rotation = 0              # In degrees, clockwise
        self._horizontal_flip = False
        self._vertical_flip = False

        self.file_handler = filehandler.FileHandler(self)
        self.thumbnailsidebar = thumbbar.ThumbnailSidebar(self)
        self.statusbar = status.Statusbar()
        self.slideshow = slideshow.Slideshow(self)
        self.cursor_handler = cursor.CursorHandler(self)
        self.enhancer = enhance.ImageEnhancer(self)
        self.ui_manager = ui.MainUI(self)
        self.menubar = self.ui_manager.get_widget('/Menu')
        self.toolbar = self.ui_manager.get_widget('/Tool')
        self.popup = self.ui_manager.get_widget('/Popup')
        self.actiongroup = self.ui_manager.get_action_groups()[0]
        self.left_image = gtk.Image()
        self.right_image = gtk.Image()
        
        self._image_box = gtk.HBox(False, 2)
        self._main_layout = gtk.Layout()
        self._event_handler = event.EventHandler(self)
        self._vadjust = self._main_layout.get_vadjustment()
        self._hadjust = self._main_layout.get_hadjustment()
        self._vscroll = gtk.VScrollbar(self._vadjust)
        self._hscroll = gtk.HScrollbar(self._hadjust)
        
        # ----------------------------------------------------------------
        # Setup
        # ----------------------------------------------------------------
        self.set_title('Comix')
        self.set_size_request(300, 300)  # Avoid making the window *too* small
        self.resize(prefs['window width'], prefs['window height'])

        # This is a hack to get the focus away from the toolbar so that
        # we don't activate it with space or some other key. (alternative?)
        self.toolbar.set_focus_child(
            self.ui_manager.get_widget('/Tool/expander'))
        
        self._image_box.add(self.left_image)
        self._image_box.add(self.right_image)
        self._image_box.show_all()
        
        self._main_layout.put(self._image_box, 0, 0)
        self._main_layout.modify_bg(gtk.STATE_NORMAL,
            gtk.gdk.colormap_get_system().alloc_color(gtk.gdk.Color(
            *prefs['bg colour']), False, True))

        self._vadjust.step_increment = 15
        self._vadjust.page_increment = 1
        self._hadjust.step_increment = 15
        self._hadjust.page_increment = 1
       
        table = gtk.Table(2, 2, False)
        table.attach(self.thumbnailsidebar, 0, 1, 2, 5, gtk.FILL,
                          gtk.FILL|gtk.EXPAND, 0, 0)
        table.attach(self._main_layout, 1, 2, 2, 3, gtk.FILL|gtk.EXPAND,
                          gtk.FILL|gtk.EXPAND, 0, 0)
        table.attach(self._vscroll, 2, 3, 2, 3, gtk.FILL|gtk.SHRINK,
                          gtk.FILL|gtk.SHRINK, 0, 0)
        table.attach(self._hscroll, 1, 2, 4, 5, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        table.attach(self.menubar, 0, 3, 0, 1, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        table.attach(self.toolbar, 0, 3, 1, 2, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        table.attach(self.statusbar, 0, 3, 5, 6, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        
        if prefs['default double page']:
            self.actiongroup.get_action('double_page').activate()
        if prefs['default fullscreen']:
            self.actiongroup.get_action('fullscreen').activate()
        if prefs['default manga mode']:
            self.actiongroup.get_action('manga_mode').activate()
        if prefs['default zoom mode'] == 'manual':
            self.actiongroup.get_action('fit_manual_mode').activate()
        elif prefs['default zoom mode'] == 'fit':
            self.actiongroup.get_action('fit_screen_mode').activate()
        elif prefs['default zoom mode'] == 'width':
            self.actiongroup.get_action('fit_width_mode').activate()
        else:
            self.actiongroup.get_action('fit_height_mode').activate()
        if prefs['show toolbar']:
            prefs['show toolbar'] = False
            self.actiongroup.get_action('toolbar').activate()
        if prefs['show menubar']:
            prefs['show menubar'] = False
            self.actiongroup.get_action('menubar').activate()
        if prefs['show statusbar']:
            prefs['show statusbar'] = False
            self.actiongroup.get_action('statusbar').activate()
        if prefs['show scrollbar']:
            prefs['show scrollbar'] = False
            self.actiongroup.get_action('scrollbar').activate()
        if prefs['show thumbnails']:
            prefs['show thumbnails'] = False
            self.actiongroup.get_action('thumbnails').activate()
        if prefs['hide all']:
            prefs['hide all'] = False
            self.actiongroup.get_action('hide all').activate()

        self.add(table)
        table.show()
        self._main_layout.show()
        self._display_active_widgets()

        self._main_layout.set_events(gtk.gdk.BUTTON1_MOTION_MASK |
                                     gtk.gdk.BUTTON2_MOTION_MASK | 
                                     gtk.gdk.BUTTON_RELEASE_MASK |
                                     gtk.gdk.POINTER_MOTION_MASK)
        self._main_layout.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                        [('text/uri-list', 0, 0)],
                                        gtk.gdk.ACTION_COPY)

        self.connect('delete_event',
            self.terminate_program)
        self.connect('key_press_event',
            self._event_handler.key_press_event)
        self.connect('button_release_event',
            self._event_handler.mouse_release_event)
        self.connect('configure_event',
            self._event_handler.resize_event)
        self._main_layout.connect('scroll_event',
            self._event_handler.scroll_wheel_event)
        self._main_layout.connect('button_press_event',
            self._event_handler.mouse_press_event)
        self._main_layout.connect('motion_notify_event',
            self._event_handler.mouse_move_event)
        self._main_layout.connect('drag_data_received',
            self._event_handler.drag_n_drop_event)
        
        self.ui_manager.set_sensitivities()
        self.show()

    def draw_image(self, at_bottom=False, scroll=True):
        
        """
        Draw the current page(s) and update the titlebar and statusbar.
        """

        self._display_active_widgets()

        if not self.file_handler.file_loaded:
            return

        width, height = self.get_visible_area_size()
        scale_width = self.zoom_mode == 'height' and -1 or width
        scale_height = self.zoom_mode == 'width' and -1 or height
        scale_up = prefs['stretch']
        
        if self.displayed_double():
            if self.is_manga_mode:
                right_pixbuf, left_pixbuf = self.file_handler.get_pixbufs()
            else:
                left_pixbuf, right_pixbuf = self.file_handler.get_pixbufs()
            left_unscaled_x = left_pixbuf.get_width()
            left_unscaled_y = left_pixbuf.get_height()
            right_unscaled_x = right_pixbuf.get_width()
            right_unscaled_y = right_pixbuf.get_height()

            if self.zoom_mode == 'manual':
                if self._rotation in [90, 270]:
                    scale_width = int(self._manual_zoom *
                        (left_pixbuf.get_height() +
                        right_pixbuf.get_height()) // 100)
                    scale_height = int(self._manual_zoom * max(
                        left_pixbuf.get_width(),
                        right_pixbuf.get_width()) // 100)
                else:
                    scale_width = int(self._manual_zoom * 
                        (left_pixbuf.get_width() +
                        right_pixbuf.get_width()) // 100)
                    scale_height = int(self._manual_zoom * max(
                        left_pixbuf.get_height(),
                        right_pixbuf.get_height()) // 100)
                scale_up = True

            left_pixbuf, right_pixbuf = image.fit_2_in_rectangle(
                left_pixbuf, right_pixbuf, scale_width, scale_height,
                scale_up=scale_up, rotation=self._rotation)
            if self._horizontal_flip:
                left_pixbuf = left_pixbuf.flip(horizontal=True)
                right_pixbuf = right_pixbuf.flip(horizontal=True)
            if self._vertical_flip:
                left_pixbuf = left_pixbuf.flip(horizontal=False)
                right_pixbuf = right_pixbuf.flip(horizontal=False)
            left_pixbuf = self.enhancer.enhance(left_pixbuf)
            right_pixbuf = self.enhancer.enhance(right_pixbuf)
            
            self.left_image.set_from_pixbuf(left_pixbuf)
            self.right_image.set_from_pixbuf(right_pixbuf)
            x_padding = (width - left_pixbuf.get_width() -
                right_pixbuf.get_width()) / 2
            y_padding = (height - max(left_pixbuf.get_height(),
                right_pixbuf.get_height())) / 2

            self.statusbar.set_page_number(self.file_handler.get_current_page(),
                self.file_handler.get_number_of_pages(), double_page=True)
            self.statusbar.set_resolution((left_unscaled_x, left_unscaled_y,
                100.0 * left_pixbuf.get_width() / left_unscaled_x), 
                (right_unscaled_x, right_unscaled_y,
                100.0 * right_pixbuf.get_width() / right_unscaled_x))
        else:
            pixbuf = self.file_handler.get_pixbufs()
            unscaled_x = pixbuf.get_width()
            unscaled_y = pixbuf.get_height()

            if self.zoom_mode == 'manual':
                scale_width = int(self._manual_zoom * pixbuf.get_width()
                    // 100)
                scale_height = int(self._manual_zoom * pixbuf.get_height()
                    // 100)
                if self._rotation in [90, 270]:
                    scale_width, scale_height = scale_height, scale_width
                scale_up = True

            pixbuf = image.fit_in_rectangle(pixbuf, scale_width, scale_height,
                scale_up=scale_up, rotation=self._rotation)
            if self._horizontal_flip:
                pixbuf = pixbuf.flip(horizontal=True)
            if self._vertical_flip:
                pixbuf = pixbuf.flip(horizontal=False)
            pixbuf = self.enhancer.enhance(pixbuf)

            self.left_image.set_from_pixbuf(pixbuf)
            self.right_image.clear()
            x_padding = (width - pixbuf.get_width()) / 2
            y_padding = (height - pixbuf.get_height()) / 2

            self.statusbar.set_page_number(self.file_handler.get_current_page(),
                self.file_handler.get_number_of_pages())
            self.statusbar.set_resolution((unscaled_x, unscaled_y,
                100.0 * pixbuf.get_width() / unscaled_x))
        
        self.left_image.hide()
        self.right_image.hide()
        self._main_layout.move(self._image_box, max(0, x_padding),
            max(0, y_padding))
        self.left_image.show()
        if self.displayed_double():
            self.right_image.show()
        self._main_layout.set_size(*self._image_box.size_request())
        if scroll and at_bottom:
            self.scroll_to_fixed(horiz='endsecond', vert='bottom')
        elif scroll:
            self.scroll_to_fixed(horiz='startfirst', vert='top')
        
        self.statusbar.set_filename(
            self.file_handler.get_pretty_current_filename())
        self.statusbar.update()
        self._set_title()
        while gtk.events_pending():
            gtk.main_iteration(False)
        enhance.draw_histogram(self.left_image)
        self.file_handler.do_cacheing()

    def new_page(self, at_bottom=False):
        
        """
        Draw a *new* page correctly (as opposed to redrawing the same image
        with a new size or whatever.)
        """
        
        if not self._keep_rotation:
            self._rotation = 0
            self._horizontal_flip = False
            self._vertical_flip = False
        self.thumbnailsidebar.update_select()
        self.draw_image(at_bottom)

    def next_page(self, *args):
        if self.file_handler.next_page():
            self.new_page()

    def previous_page(self, *args):
        if self.file_handler.previous_page():
            self.new_page(at_bottom=True)

    def first_page(self, *args):
        if self.file_handler.first_page():
            self.new_page()

    def last_page(self, *args):
        if self.file_handler.last_page():
            self.new_page()

    def set_page(self, num):
        if self.file_handler.set_page(num):
            self.new_page()

    def rotate_90(self, *args):
        self._rotation = (self._rotation + 90) % 360
        self.draw_image()

    def rotate_180(self, *args):
        self._rotation = (self._rotation + 180) % 360
        self.draw_image()

    def rotate_270(self, *args):
        self._rotation = (self._rotation + 270) % 360
        self.draw_image()

    def flip_horizontally(self, *args):
        self._horizontal_flip = not self._horizontal_flip
        self.draw_image()

    def flip_vertically(self, *args):
        self._vertical_flip = not self._vertical_flip
        self.draw_image()

    def change_double_page(self, toggleaction):
        self.is_double_page = toggleaction.get_active()
        self.draw_image()

    def change_manga_mode(self, toggleaction):
        self.is_manga_mode = toggleaction.get_active()
        self.draw_image()

    def change_fullscreen(self, toggleaction):
        self.is_fullscreen = toggleaction.get_active()
        if self.is_fullscreen:
            self.fullscreen()
            self.cursor_handler.enter_fullscreen()
        else:
            self.unfullscreen()
            self.cursor_handler.exit_fullscreen()

    def change_zoom_mode(self, radioaction, *args):
        mode = radioaction.get_current_value()
        old_mode = self.zoom_mode
        if mode == 0:
            self.zoom_mode = 'manual'
        elif mode == 1:
            self.zoom_mode = 'fit'
        elif mode == 2:
            self.zoom_mode = 'width'
        else:
            self.zoom_mode = 'height'
        if old_mode != self.zoom_mode:
            self.draw_image()
    
    def change_toolbar_visibility(self, *args):
        prefs['show toolbar'] = not prefs['show toolbar']
        self.draw_image()

    def change_menubar_visibility(self, *args):
        prefs['show menubar'] = not prefs['show menubar']
        self.draw_image()

    def change_statusbar_visibility(self, *args):
        prefs['show statusbar'] = not prefs['show statusbar']
        self.draw_image()

    def change_scrollbar_visibility(self, *args):
        prefs['show scrollbar'] = not prefs['show scrollbar']
        self.draw_image()

    def change_thumbnails_visibility(self, *args):
        prefs['show thumbnails'] = not prefs['show thumbnails']
        self.draw_image()

    def change_hide_all(self, *args):
        prefs['hide all'] = not prefs['hide all']
        self.draw_image()

    def change_keep_rotation(self, *args):
        self._keep_rotation = not self._keep_rotation

    def manual_zoom_in(self, *args):
        new_zoom = self._manual_zoom * 1.15
        if 95 < new_zoom < 105: # To compensate for rounding errors
            new_zoom = 100
        if new_zoom > 1000:
            return
        self._manual_zoom = new_zoom
        self.draw_image()

    def manual_zoom_out(self, *args):
        new_zoom = self._manual_zoom / 1.15
        if 95 < new_zoom < 105: # To compensate for rounding errors
            new_zoom = 100
        if new_zoom < 10:
            return
        self._manual_zoom = new_zoom
        self.draw_image()

    def manual_zoom_original(self, *args):
        self._manual_zoom = 100
        self.draw_image()

    def scroll(self, x, y, bound=None):

        """
        Scroll <x> px horizontally and <y> px vertically. If <bound> is
        'first' or 'second', we will not scroll out of the first or second
        page respectively (dependent on manga mode). The <bound> argument
        only makes sense in double page mode.
        
        Return True if call resulted in new adjustment values, False
        otherwise.
        """

        old_hadjust = self._hadjust.get_value()
        old_vadjust = self._vadjust.get_value()
        visible_width, visible_height = self.get_visible_area_size()
        hadjust_upper = max(0, self._hadjust.upper - visible_width)
        vadjust_upper = max(0, self._vadjust.upper - visible_height)
        hadjust_lower = 0
        if bound != None and self.is_manga_mode:
            bound = {'first':  'second',
                     'second': 'first'}[bound]
        if bound == 'first':
            hadjust_upper = max(0, hadjust_upper -
                self.right_image.size_request()[0] - 2)
        elif bound == 'second':
            hadjust_lower = self.left_image.size_request()[0] + 2
        new_hadjust = old_hadjust + x
        new_vadjust = old_vadjust + y
        new_hadjust = max(hadjust_lower, new_hadjust)
        new_vadjust = max(0, new_vadjust)
        new_hadjust = min(hadjust_upper, new_hadjust)
        new_vadjust = min(vadjust_upper, new_vadjust)
        self._vadjust.set_value(new_vadjust)
        self._hadjust.set_value(new_hadjust)
        return old_vadjust != new_vadjust or old_hadjust != new_hadjust

    def scroll_to_fixed(self, horiz=None, vert=None):
        
        """
        Scroll using one of several fixed values.

        If either <horiz> or <vert> is as below, the display is scrolled as
        follows:

        horiz: 'left'        = left end of display
               'middle'      = middle of the display
               'right'       = right end of display
               'startfirst'  = start of first page
               'endfirst'    = end of first page
               'startsecond' = start of second page
               'endsecond'   = end of second page
        
        vert:  'top'         = top of display
               'middle'      = middle of display
               'bottom'      = bottom of display

        What is considered "start" and "end" depends on whether we are
        using manga mode or not.

        Return True if call resulted in new adjustment values.
        """
        
        old_hadjust = self._hadjust.get_value()
        old_vadjust = self._vadjust.get_value()
        new_vadjust = old_vadjust
        new_hadjust = old_hadjust
        visible_width, visible_height = self.get_visible_area_size()
        vadjust_upper = self._vadjust.upper - visible_height
        hadjust_upper = self._hadjust.upper - visible_width

        if vert == 'top':
            new_vadjust = 0
        elif vert == 'middle':
            new_vadjust = vadjust_upper / 2
        elif vert == 'bottom':
            new_vadjust = vadjust_upper

        if not self.displayed_double():
            horiz = {'startsecond': 'endfirst',
                     'endsecond':   'endfirst'}.get(horiz, horiz)
        
        # Manga transformations.
        if self.is_manga_mode and self.displayed_double() and horiz != None:
            horiz = {'left':        'left',
                     'middle':      'middle',
                     'right':       'right',
                     'startfirst':  'endsecond',
                     'endfirst':    'startsecond',
                     'startsecond': 'endfirst',
                     'endsecond':   'startfirst'}[horiz]
        elif self.is_manga_mode and horiz != None:
            horiz = {'left':        'left',
                     'middle':      'middle',
                     'right':       'right',
                     'startfirst':  'endfirst',
                     'endfirst':    'startfirst'}[horiz]
        
        if horiz == 'left':
            new_hadjust = 0
        elif horiz == 'middle':
            new_hadjust = hadjust_upper / 2
        elif horiz == 'right':
            new_hadjust = hadjust_upper 
        elif horiz == 'startfirst':
            new_hadjust = 0
        elif horiz == 'endfirst':
            if self.displayed_double():
                new_hadjust = self.left_image.size_request()[0] - visible_width
            else:
                new_hadjust = hadjust_upper
        elif horiz == 'startsecond':
            new_hadjust = self.left_image.size_request()[0] + 2
        elif horiz == 'endsecond':
            new_hadjust = hadjust_upper
        new_hadjust = max(0, new_hadjust)
        new_vadjust = max(0, new_vadjust)
        new_hadjust = min(hadjust_upper, new_hadjust)
        new_vadjust = min(vadjust_upper, new_vadjust)
        self._vadjust.set_value(new_vadjust)
        self._hadjust.set_value(new_hadjust)
        return old_vadjust != new_vadjust or old_hadjust != new_hadjust

    def is_on_first_page(self):
        
        """
        Return True if we are currently viewing the first page, i.e. if we
        are scrolled as far to the left as possible, or if only the left page
        is visible on the main layout. In manga mode it is the other way
        around.
        """

        if not self.displayed_double():
            return True
        width, height = self.get_visible_area_size()
        if self.is_manga_mode:
            return (self._hadjust.get_value() >= self._hadjust.upper - width or
                self._hadjust.get_value() > self.left_image.size_request()[0])
        else:
            return (self._hadjust.get_value() == 0 or
                self._hadjust.get_value() + width <=
                self.left_image.size_request()[0])

    def clear(self):
        
        """ Clear the currently displayed data (i.e. "close" the file) """

        self.left_image.clear()
        self.right_image.clear()
        self.thumbnailsidebar.clear()
        self.set_title('Comix')
        self.statusbar.set_message('')
        enhance.clear_histogram()

    def displayed_double(self):
        
        """ Return True if two pages are currently displayed. """

        return (self.is_double_page and self.file_handler.get_current_page() !=
            self.file_handler.get_number_of_pages())

    def get_visible_area_size(self):
        
        """
        Return a 2-tuple with the width and height of the visible part
        of the main layout area.
        """

        width, height = self.get_size()
        if not prefs['hide all'] and not (self.is_fullscreen and 
          prefs['hide all in fullscreen']):
            if prefs['show toolbar']:
                height -= self.toolbar.size_request()[1]
            if prefs['show statusbar']:
                height -= self.statusbar.size_request()[1]
            if prefs['show thumbnails']:
                width -= self.thumbnailsidebar.get_width()
            if prefs['show menubar']:
                height -= self.menubar.size_request()[1]
            if prefs['show scrollbar'] and self.zoom_mode == 'width':
                width -= self._vscroll.size_request()[0]
            elif prefs['show scrollbar'] and self.zoom_mode == 'height':
                height -= self._hscroll.size_request()[1]
            elif prefs['show scrollbar'] and self.zoom_mode == 'manual':
                width -= self._vscroll.size_request()[0]
                height -= self._hscroll.size_request()[1]
        return width, height

    def set_cursor(self, mode):
        
        """
        Set the cursor on the main layout area to <mode>. You should probably
        use the cursor_handler instead of using this method directly.
        """

        self._main_layout.window.set_cursor(mode)
        return False

    def _display_active_widgets(self):
        
        """ 
        Hide and/or show main window widgets depending on the current
        state.
        """

        if not prefs['hide all'] and not (self.is_fullscreen and 
          prefs['hide all in fullscreen']):
            if prefs['show toolbar']:
                self.toolbar.show_all()
            else:
                self.toolbar.hide_all()
            if prefs['show statusbar']:
                self.statusbar.show_all()
            else:
                self.statusbar.hide_all()
            if prefs['show thumbnails']:
                self.thumbnailsidebar.show()
            else:
                self.thumbnailsidebar.hide()
            if prefs['show menubar']:
                self.menubar.show_all()
            else:
                self.menubar.hide_all()
            if (prefs['show scrollbar'] and
              self.zoom_mode == 'width'):
                self._vscroll.show_all()
                self._hscroll.hide_all()
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'height'):
                self._vscroll.hide_all()
                self._hscroll.show_all()
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'manual'):
                self._vscroll.show_all()
                self._hscroll.show_all()
            else:
                self._vscroll.hide_all()
                self._hscroll.hide_all()
        else:
            self.toolbar.hide_all()
            self.menubar.hide_all()
            self.statusbar.hide_all()
            self.thumbnailsidebar.hide()
            self._vscroll.hide_all()
            self._hscroll.hide_all()
        
    def _set_title(self):
        
        """ Set the title acording to current state. """

        if self.displayed_double():
            self.set_title(encoding.to_unicode( 
                '[%d,%d / %d]  %s - Comix' %
                (self.file_handler.get_current_page(),
                self.file_handler.get_current_page() + 1,
                self.file_handler.get_number_of_pages(),
                self.file_handler.get_pretty_current_filename())))
        else:
            self.set_title(encoding.to_unicode( 
                '[%d / %d]  %s - Comix' %
                (self.file_handler.get_current_page(),
                self.file_handler.get_number_of_pages(),
                self.file_handler.get_pretty_current_filename())))

    def terminate_program(self, *args):
        
        """ Run clean-up tasks and exit the program. """

        print 'Bye!'
        gtk.main_quit()
        self.file_handler.cleanup()
        if not os.path.exists(constants.COMIX_DIR):
            os.mkdir(constants.COMIX_DIR)
        preferences.write_config_to_file()
        self.ui_manager.bookmarks.write_bookmarks_to_file()
        sys.exit(0)

