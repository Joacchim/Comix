# ============================================================================
# event.py - Event handling (keyboard, mouse, etc.) for Comix.
# ============================================================================

import gtk

import cursor
from preferences import prefs

class EventHandler:
    
    def __init__(self, window):
        self.window = window
        self.last_pointer_pos_x = None
        self.last_pointer_pos_y = None
        self.pressed_pointer_pos_x = None
        self.pressed_pointer_pos_y = None

    def resize_event(self, widget, event):
            
        """ Handles events from resizing and moving the main window. """
        
        if not self.window.is_fullscreen:
            prefs['window x'], prefs['window y'] = self.window.get_position()
        if (event.width != self.window.width or
            event.height != self.window.height):
            print 'resize'
            if not self.window.is_fullscreen:
                prefs['window width'] = event.width
                prefs['window height'] = event.height
            self.window.width = event.width
            self.window.height = event.height
            self.window.draw_image()

    def key_press_event(self, widget, event, *args):
        
        """ Catches key press events and takes the appropriate actions. """
        
        # ----------------------------------------------------------------
        # Numpad aligns the image depending on the key. 
        # ----------------------------------------------------------------
        if event.keyval == gtk.keysyms.KP_1:
            self.window.scroll_to_fixed(horiz='left', vert='bottom')
        elif event.keyval == gtk.keysyms.KP_2:
            self.window.scroll_to_fixed(horiz='middle', vert='bottom')
        elif event.keyval == gtk.keysyms.KP_3:
            self.window.scroll_to_fixed(horiz='right', vert='bottom')
        elif event.keyval == gtk.keysyms.KP_4:
            self.window.scroll_to_fixed(horiz='left', vert='middle')
        elif event.keyval == gtk.keysyms.KP_5:
            self.window.scroll_to_fixed(horiz='middle', vert='middle')
        elif event.keyval == gtk.keysyms.KP_6:
            self.window.scroll_to_fixed(horiz='right', vert='middle')
        elif event.keyval == gtk.keysyms.KP_7:
            self.window.scroll_to_fixed(horiz='left', vert='top')
        elif event.keyval == gtk.keysyms.KP_8:
            self.window.scroll_to_fixed(horiz='middle', vert='top')
        elif event.keyval == gtk.keysyms.KP_9:
            self.window.scroll_to_fixed(horiz='right', vert='top')
        
        # ----------------------------------------------------------------
        # Enter/exit fullscreen. 'f' is also a valid key, defined as an
        # accelerator elsewhere.
        # ----------------------------------------------------------------
        elif event.keyval == gtk.keysyms.Escape:
            self.window.actiongroup.get_action('fullscreen').set_active(False)
        elif event.keyval == gtk.keysyms.F11:
            self.window.actiongroup.get_action('fullscreen').activate()

        # ----------------------------------------------------------------
        # Zooming commands for manual zoom mode. These keys complement 
        # others (with the same action) defined as accelerators.
        # ----------------------------------------------------------------
        elif event.keyval in [gtk.keysyms.plus, gtk.keysyms.equal]:
            self.window.actiongroup.get_action('zin').activate()
        elif event.keyval == gtk.keysyms.minus:
            self.window.actiongroup.get_action('zout').activate()
        elif (event.keyval in [gtk.keysyms._0, gtk.keysyms.KP_0] and 
          'GDK_CONTROL_MASK' in event.state.value_names):
            self.window.actiongroup.get_action('zoriginal').activate()
        
        # ----------------------------------------------------------------
        # Arrow keys scroll the image, except in fit-to-screen mode where
        # they flip pages instead.
        # ----------------------------------------------------------------
        elif event.keyval == gtk.keysyms.Down:
            if not self.window.zoom_mode == 'fit':
                self.window.scroll(0, 30)
            else:
                self.window.next_page()
        elif event.keyval == gtk.keysyms.Up:
            if not self.window.zoom_mode == 'fit':
                self.window.scroll(0, -30)
            else:
                self.window.previous_page()
        elif event.keyval == gtk.keysyms.Right:
            if not self.window.zoom_mode == 'fit':
                self.window.scroll(30, 0)
            else:
                self.window.next_page()
        elif event.keyval == gtk.keysyms.Left:
            if not self.window.zoom_mode == 'fit':
                self.window.scroll(-30, 0)
            else:
                self.window.previous_page()

        # ----------------------------------------------------------------
        # Space key scrolls down a percentage of the window height or the
        # image height at a time. When at the bottom it flips to the next
        # page. 
        # 
        # It also has a "smart scrolling mode" in which we try to follow
        # the flow of the comic.
        #
        # If Shift is pressed we should backtrack instead.
        # ----------------------------------------------------------------
        elif event.keyval == gtk.keysyms.space:
            if prefs['space scroll type'] == 'window':
                x_step, y_step = self.window.get_layout_size()
            elif prefs['space scroll type'] == 'image':
                x_step, y_step = self.window.main_layout.get_size()
            x_step = x_step * prefs['space scroll length'] // 100
            y_step = y_step * prefs['space scroll length'] // 100
            if 'GDK_SHIFT_MASK' in event.state.value_names:
                next_page_function = self.window.previous_page
                startfirst = 'endfirst'
                x_step *= -1
                y_step *= -1
            else:
                next_page_function = self.window.next_page
                startfirst = 'startfirst'
                
            if self.window.is_manga_mode:
                x_step *= -1
            # FIXME: Smart space in DP mode is not implemented
            if prefs['smart space scroll']:
                if not self.window.is_double():
                    if not self.window.scroll(x_step, 0):
                        if not self.window.scroll(0, y_step):
                            next_page_function()
                        else:
                            self.window.scroll_to_fixed(horiz=startfirst)

            else:           
                if (self.window.zoom_mode == 'fit' or 
                  not self.window.scroll(0, y_step)):
                    next_page_function()

        # ----------------------------------------------------------------
        # We kill the signals here for the Up, Down, Space and Enter keys.
        # Otherwise they will start fiddling with the thumbnail selector.
        # ----------------------------------------------------------------
        if (event.keyval in [gtk.keysyms.Up, gtk.keysyms.Down,
          gtk.keysyms.space, gtk.keysyms.KP_Enter] or 
          (event.keyval == gtk.keysyms.Return and not
          'GDK_MOD1_MASK' in event.state.value_names)):
            self.window.emit_stop_by_name("key_press_event")
            return True
        else:
            return False

    def scroll_wheel_event(self, widget, event, *args):
        
        """
        Catches scroll wheel events and takes the appropriate
        actions. The scroll wheel flips pages in fit-to-screen mode
        and scrolls the scrollbars when not.
        """

        if event.direction == gtk.gdk.SCROLL_UP:
            if self.window.zoom_mode == 'fit':
                self.window.previous_page()
            else:
                self.window.scroll(0, -50)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            if self.window.zoom_mode == 'fit':
                self.window.next_page()
            else:
                self.window.scroll(0, 50)
        elif event.direction == gtk.gdk.SCROLL_RIGHT:
            self.window.next_page()
        elif event.direction == gtk.gdk.SCROLL_LEFT:
            self.window.previous_page()

    def mouse_press_event(self, widget, event):
        
        """ Handles mouse click events on the main window. """

        if event.button == 1:
            self.pressed_pointer_pos_x = event.x_root
            self.pressed_pointer_pos_y = event.y_root
            self.last_pointer_pos_x = event.x_root
            self.last_pointer_pos_y = event.y_root
        elif event.button == 2:
            print 2
            #if self.scroll_wheel_event_id != None:
            #    self.layout.disconnect(self.scroll_wheel_event_id)
            #    self.scroll_wheel_event_id = None
            #self.zooming_lens(event.x, event.y, event.time)
        elif event.button == 3:
            self.window.ui_manager.get_widget('/Pop').popup(
                None, None, None, event.button, event.time)

    def mouse_release_event(self, widget, event):
        
        """ Handles mouse button release events on the main window. """

        cursor.set_cursor_type(cursor.NORMAL)
        
        if (event.button == 1 and
          event.x_root == self.pressed_pointer_pos_x and
          event.y_root == self.pressed_pointer_pos_y):
            self.window.next_page()

        #if event.button == 2 and self.z_pressed:
        #    self.actiongroup.get_action('Lens').set_active(False)
        #if self.scroll_wheel_event_id == None:
        #    self.scroll_wheel_event_id = \
        #        self.layout.connect('scroll_event', self.scroll_wheel_event)

    def mouse_move_event(self, widget, event):
        
        """ Handles mouse pointer movement events. """
        
        if 'GDK_BUTTON1_MASK' in event.state.value_names:
            cursor.set_cursor_type(cursor.GRAB)
            self.window.scroll(self.last_pointer_pos_x - event.x_root,
                               self.last_pointer_pos_y - event.y_root)
            self.last_pointer_pos_x = event.x_root
            self.last_pointer_pos_y = event.y_root

