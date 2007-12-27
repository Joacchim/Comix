# ============================================================================
# main.py - Main window for Comix.
# ============================================================================

import sys
import os
import shutil

import gtk

import event
import filehandler
import icons
import pilpixbuf
from preferences import prefs
import ui
import scale
import thumbbar

class MainWindow(gtk.Window):

    def __init__(self): 
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title('Comix')
        self.realize() # XXX

        self.is_fullscreen = False
        self.is_double_page = False 
        self.is_manga_mode = False
        self.keep_rotation = False
        self.zoom_mode = 'fit'          # 'fit', 'width', 'height' or 'manual'
        self.manual_zoom = 100          # In percent of original image size
        self.rotation = 0               # In degrees, clockwise
        self.left_image = gtk.Image()
        self.right_image = gtk.Image()
        self.image_box = gtk.HBox(False, 2)
        self.table = gtk.Table(2, 2, False)
        self.comment_label = gtk.Label()
        self.statusbar = gtk.Statusbar()
        self.main_layout = gtk.Layout()
        self.thumbnailsidebar = thumbbar.ThumbnailSidebar(self)
        self.file_handler = filehandler.FileHandler(self)
        self.event_handler = event.EventHandler(self)
        self.ui_manager = ui.MainUI(self)
        self.menubar = self.ui_manager.get_widget('/Menu')
        self.toolbar = self.ui_manager.get_widget('/Tool')
        self.actiongroup = self.ui_manager.get_action_groups()[0]
        self.vadjust = self.main_layout.get_vadjustment()
        self.hadjust = self.main_layout.get_hadjustment()
        self.vscroll = gtk.VScrollbar(self.vadjust)
        self.hscroll = gtk.HScrollbar(self.hadjust)

        if prefs['save window pos']:
            self.move(prefs['window x'], prefs['window y'])
        self.set_size_request(300, 300) # Avoid making the window *too* small
        self.resize(prefs['window width'], prefs['window height'])
        self.width, self.height = self.get_size()

        # This is a hack to get the focus away from the toolbar so that
        # we don't activate it with space or some other key.
        self.toolbar.set_focus_child(
            self.ui_manager.get_widget('/Tool/expander'))
        
        self.add_accel_group(self.ui_manager.get_accel_group())
        self.image_box.add(self.left_image)
        self.image_box.add(self.right_image)
        self.image_box.show_all()
        
        self.main_layout.put(self.image_box, 0, 0)
        self.main_layout.put(self.comment_label, 0, 0)
        self.main_layout.modify_bg(gtk.STATE_NORMAL,
            gtk.gdk.colormap_get_system().alloc_color(gtk.gdk.Color(
            prefs['red bg'], prefs['green bg'], prefs['blue bg']), False, True))

        self.vadjust.step_increment = 15
        self.vadjust.page_increment = 1
        self.hadjust.step_increment = 15
        self.hadjust.page_increment = 1
        
        self.table.attach(self.thumbnailsidebar.layout, 0, 1, 2, 5, gtk.FILL,
                          gtk.FILL|gtk.EXPAND, 0, 0)
        self.table.attach(self.thumbnailsidebar.scroll, 1, 2, 2, 4,
                          gtk.FILL|gtk.SHRINK, gtk.FILL|gtk.SHRINK, 0, 0)
        self.table.attach(self.main_layout, 2, 3, 2, 3, gtk.FILL|gtk.EXPAND,
                          gtk.FILL|gtk.EXPAND, 0, 0)
        self.table.attach(self.vscroll, 3, 4, 2, 3, gtk.FILL|gtk.SHRINK,
                          gtk.FILL|gtk.SHRINK, 0, 0)
        self.table.attach(self.hscroll, 2, 3, 4, 5, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        self.table.attach(self.toolbar, 0, 4, 1, 2, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        self.table.attach(self.statusbar, 0, 4, 5, 6, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)
        self.table.attach(self.menubar, 0, 4, 0, 1, gtk.FILL|gtk.SHRINK,
                          gtk.FILL, 0, 0)

        if prefs['default double page']:
            self.actiongroup.get_action('double').activate()
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

        self.add(self.table)
        self.table.show()
        self.main_layout.show()
        self.display_active_widgets()

        self.main_layout.set_events(gtk.gdk.BUTTON1_MOTION_MASK |
                                    gtk.gdk.BUTTON2_MOTION_MASK | 
                                    gtk.gdk.BUTTON_RELEASE_MASK |
                                    gtk.gdk.POINTER_MOTION_MASK)

        self.connect('delete_event',
            self.terminate_program)
        self.connect('key_press_event',
            self.event_handler.key_press_event)
        self.main_layout.connect('scroll_event',
            self.event_handler.scroll_wheel_event)
        self.connect('configure_event',
            self.event_handler.resize_event)
        self.main_layout.connect('button_press_event',
            self.event_handler.mouse_press_event)
        self.connect('button_release_event',
            self.event_handler.mouse_release_event)
        self.main_layout.connect('motion_notify_event',
            self.event_handler.mouse_move_event)
        
        self.show()

    def display_active_widgets(self):
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
                self.vscroll.show_all()
                self.hscroll.hide_all()
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'height'):
                self.vscroll.hide_all()
                self.hscroll.show_all()
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'manual'):
                self.vscroll.show_all()
                self.hscroll.show_all()
            else:
                self.vscroll.hide_all()
                self.hscroll.hide_all()
        else:
            self.toolbar.hide_all()
            self.menubar.hide_all()
            self.statusbar.hide_all()
            self.thumbnailsidebar.hide()
            self.vscroll.hide_all()
            self.hscroll.hide_all()

    def get_layout_size(self):
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
            if (prefs['show scrollbar'] and
              self.zoom_mode == 'width'):
                width -= self.vscroll.size_request()[0]
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'height'):
                height -= self.hscroll.size_request()[1]
            elif (prefs['show scrollbar'] and
              self.zoom_mode == 'manual'):
                width -= self.vscroll.size_request()[0]
                height -= self.hscroll.size_request()[1]
        return width, height

    def draw_image(self, at_bottom=False):
        self.display_active_widgets()
        if not self.file_handler.file_loaded:
            self.left_image.clear()
            self.right_image.clear()
            self.thumbnailsidebar.clear()
            self.set_title('Comix')
            return
        print 'draw'
        width, height = self.get_layout_size()
        scale_width = self.zoom_mode == 'height' and -1 or width
        scale_height = self.zoom_mode == 'width' and -1 or height
        scale_up = prefs['stretch']
        
        if self.displayed_double():
            if self.is_manga_mode:
                right_pixbuf, left_pixbuf = self.file_handler.get_pixbufs()
            else:
                left_pixbuf, right_pixbuf = self.file_handler.get_pixbufs()

            if self.zoom_mode == 'manual':
                if self.rotation in [90, 270]:
                    scale_width = int(self.manual_zoom *
                        (left_pixbuf.get_height() +
                        right_pixbuf.get_height()) // 100)
                    scale_height = int(self.manual_zoom * max(
                        left_pixbuf.get_width(),
                        right_pixbuf.get_width()) // 100)
                else:
                    scale_width = int(self.manual_zoom * 
                        (left_pixbuf.get_width() +
                        right_pixbuf.get_width()) // 100)
                    scale_height = int(self.manual_zoom * max(
                        left_pixbuf.get_height(),
                        right_pixbuf.get_height()) // 100)
                
                scale_up = True

            left_pixbuf, right_pixbuf = scale.fit_2_in_rectangle(
                left_pixbuf, right_pixbuf, scale_width, scale_height,
                scale_up=scale_up, rotation=self.rotation)
            self.left_image.set_from_pixbuf(left_pixbuf)
            self.right_image.set_from_pixbuf(right_pixbuf)
            x_padding = (width - left_pixbuf.get_width() -
                right_pixbuf.get_width()) / 2
            y_padding = (height - max(left_pixbuf.get_height(),
                right_pixbuf.get_height())) / 2
            self.right_image.show()
        else:
            pixbuf = self.file_handler.get_pixbufs()

            if self.zoom_mode == 'manual':
                scale_width = int(self.manual_zoom * pixbuf.get_width() // 100)
                scale_height = int(self.manual_zoom * pixbuf.get_height()
                    // 100)
                if self.rotation in [90, 270]:
                    scale_width, scale_height = scale_height, scale_width
                scale_up = True

            pixbuf = scale.fit_in_rectangle(pixbuf, scale_width, scale_height,
                scale_up=scale_up, rotation=self.rotation)

            #im = pilpixbuf.pixbuf_to_pil(pixbuf)
            #pixbuf = pilpixbuf.pil_to_pixbuf(im)

            self.left_image.set_from_pixbuf(pixbuf)
            self.right_image.clear()
            self.right_image.hide()
            x_padding = (width - pixbuf.get_width()) / 2
            y_padding = (height - pixbuf.get_height()) / 2
        
        self.main_layout.move(self.image_box, max(0, x_padding),
            max(0, y_padding))
        self.main_layout.set_size(*self.image_box.size_request())
        if at_bottom:
            self.vadjust.set_value(self.vadjust.upper - height)
            if self.is_manga_mode:
                self.hadjust.set_value(0)
            else:
                self.hadjust.set_value(self.hadjust.upper - width)
        else:
            self.vadjust.set_value(0)
            if self.is_manga_mode:
                self.hadjust.set_value(self.hadjust.upper - width)
            else:
                self.hadjust.set_value(0)
        
        self.set_title(os.path.basename(self.file_handler.archive_path) + 
            '  [%d / %d]  -  Comix' % (self.file_handler.current_image + 1,
            len(self.file_handler.image_files)))

        while gtk.events_pending():
            gtk.main_iteration(False)
        self.file_handler.do_cacheing()

    def _new_page(self, at_bottom=False):
        if not self.keep_rotation:
                self.rotation = 0
        self.thumbnailsidebar.update_select()
        self.draw_image(at_bottom)

    def next_page(self, *args):
        if self.file_handler.next_page():
            self._new_page()

    def previous_page(self, *args):
        if self.file_handler.previous_page():
            self._new_page(at_bottom=True)

    def first_page(self, *args):
        if self.file_handler.first_page():
            self._new_page()

    def last_page(self, *args):
        if self.file_handler.last_page():
            self._new_page()

    def set_page(self, num):
        if self.file_handler.set_page(num):
            self._new_page()

    def rotate90(self, *args):
        self.rotation = (self.rotation + 90) % 360
        self.draw_image()

    def rotate180(self, *args):
        self.rotation = (self.rotation + 180) % 360
        self.draw_image()

    def rotate270(self, *args):
        self.rotation = (self.rotation + 270) % 360
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
        else:
            self.unfullscreen()

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
        self.keep_rotation = not self.keep_rotation

    def manual_zoom_in(self, *args):
        new_zoom = self.manual_zoom * 1.15
        if 95 < new_zoom < 105: # To compensate for rounding errors
            new_zoom = 100
        if new_zoom > 1000:
            return
        self.manual_zoom = new_zoom
        self.draw_image()

    def manual_zoom_out(self, *args):
        new_zoom = self.manual_zoom / 1.15
        if 95 < new_zoom < 105: # To compensate for rounding errors
            new_zoom = 100
        if new_zoom < 10:
            return
        self.manual_zoom = new_zoom
        self.draw_image()

    def manual_zoom_original(self, *args):
        self.manual_zoom = 100
        self.draw_image()

    def scroll(self, x, y):

        """
        Scrolls <x> px horizontally and <y> px vertically.
        Returns True if call resulted in new adjustment values, False otherwise.
        """

        old_hadjust = self.hadjust.get_value()
        old_vadjust = self.vadjust.get_value()
        layout_width, layout_height = self.get_layout_size()
        hadjust_upper = self.hadjust.upper - layout_width
        vadjust_upper = self.vadjust.upper - layout_height
        new_hadjust = old_hadjust + x
        new_vadjust = old_vadjust + y
        new_hadjust = max(0, new_hadjust)
        new_vadjust = max(0, new_vadjust)
        new_hadjust = min(hadjust_upper, new_hadjust)
        new_vadjust = min(vadjust_upper, new_vadjust)
        self.vadjust.set_value(new_vadjust)
        self.hadjust.set_value(new_hadjust)
        return old_vadjust != new_vadjust or old_hadjust != new_hadjust

    def scroll_to_fixed(self, horiz=None, vert=None):
        
        """
        If either <horiz> or <vert> is as below, the display is scrolled as
        follows:

        horiz: 'left'        = left end of display
               'middle'      = middle of the display
               'right'       = rigth end of display
               'startfirst'  = start of first page
               'endfirst'    = end of first page
               'startsecond' = start of second page
               'endsecond'   = end of second page
        
        vert:  'top'         = top of display
               'middle'      = middle of display
               'bottom'      = bottom of display

        Scrolling to the second page is, of course, only applicable in double
        page mode. What is considered "start" and "end" depends on whether we
        are using manga mode or not.
        """

        layout_width, layout_height = self.get_layout_size()
        vadjust_upper = self.vadjust.upper - layout_height
        hadjust_upper = self.hadjust.upper - layout_width

        if vert == 'top':
            self.vadjust.set_value(0)
        elif vert == 'middle':
            self.vadjust.set_value(vadjust_upper / 2)
        elif vert == 'bottom':
            self.vadjust.set_value(vadjust_upper)
        
        # Manga transformations.
        if self.is_manga_mode and self.displayed_double():
            horiz = {'left':        'left',
                     'middle':      'middle',
                     'right':       'right',
                     'startfirst':  'endsecond',
                     'endfirst':    'startsecond',
                     'startsecond': 'endfirst',
                     'endsecond':   'startfirst'}[horiz]
        elif self.is_manga_mode:
            horiz = {'left':        'left',
                     'middle':      'middle',
                     'right':       'right',
                     'startfirst':  'endfirst',
                     'endfirst':    'startfirst'}[horiz]
        
        if horiz == 'left':
            self.hadjust.set_value(0)
        elif horiz == 'middle':
            self.hadjust.set_value(hadjust_upper / 2)
        elif horiz == 'right':
            self.hadjust.set_value(hadjust_upper)
        elif horiz == 'startfirst':
            self.hadjust.set_value(0)
        elif horiz == 'endfirst':
            if self.displayed_double():
                self.hadjust.set_value(
                    self.left_image.size_request()[0] - layout_width)
            else:
                self.hadjust.set_value(hadjust_upper)
        elif horiz == 'startsecond':
            self.hadjust.set_value(self.left_image.size_request()[0] + 2)
        elif horiz == 'endsecond':
            self.hadjust.set_value(vadjust_upper)

    def displayed_double(self):
        
        """ Returns True if two pages are currently displayed. """

        return self.is_double_page and not self.file_handler.is_last_page()

    def terminate_program(self, *args):
        
        """ Runs clean-up tasks and exits the program. """

        print 'Bye!'
        gtk.main_quit()
        shutil.rmtree(self.file_handler.tmp_dir)
        sys.exit(0)

