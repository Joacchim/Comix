# ========================================================================
# event.py - Event handling (keyboard, mouse, etc.) for Comix.
# ========================================================================

import gtk

import main
import preferences

def resize_event(widget, event):
        
    ''' Handles events from resizing and moving the main window. '''
    
    #print dir(event)

    #if not main.window.is_fullscreen:
    #    preferences.prefs['window x'], preferences.prefs['window y'] = \
    #        main.window.get_position()
    if (event.width != main.window.width or
        event.height != main.window.height):
        print 'resize'
        #if not main.window.is_fullscreen:
        #    preferences.prefs['window width'] = event.width
        #    preferences.prefs['window height'] = event.height
        main.window.width = event.width
        main.window.height = event.height
        #self.resize_event = 1
        main.window.draw_image()
        #self.resize_event = 0

def key_press_event(widget, event, *args):
    
    ''' Catches key press events and takes the appropriate
    actions. '''
    
    #if self.slideshow_started:
    #    self.stop_slideshow()
    #    self.window.emit_stop_by_name("key_press_event")
    #    return True
    
    # =======================================================
    # Delete key deletes an image (duh...)
    # =======================================================
    #if event.keyval == gtk.keysyms.Delete:
    #    self.delete_file()
    
    # =======================================================
    # Numpad aligns the image depending on the key. 
    # =======================================================
    if event.keyval == gtk.keysyms.KP_1:
        main.scroll_to_fixed(horiz='left', vert='bottom')
    elif event.keyval == gtk.keysyms.KP_2:
        main.scroll_to_fixed(horiz='middle', vert='bottom')
    elif event.keyval == gtk.keysyms.KP_3:
        main.scroll_to_fixed(horiz='right', vert='bottom')
    elif event.keyval == gtk.keysyms.KP_4:
        main.scroll_to_fixed(horiz='left', vert='middle')
    elif event.keyval == gtk.keysyms.KP_5:
        main.scroll_to_fixed(horiz='middle', vert='middle')
    elif event.keyval == gtk.keysyms.KP_6:
        main.scroll_to_fixed(horiz='right', vert='middle')
    elif event.keyval == gtk.keysyms.KP_7:
        main.scroll_to_fixed(horiz='left', vert='top')
    elif event.keyval == gtk.keysyms.KP_8:
        main.scroll_to_fixed(horiz='middle', vert='top')
    elif event.keyval == gtk.keysyms.KP_9:
        main.scroll_to_fixed(horiz='right', vert='top')
    
    # =======================================================
    # Enter/exit fullscreen. 'f' is also a valid key,
    # defined as an accelerator elsewhere.
    # =======================================================
    elif event.keyval == gtk.keysyms.Escape:
        main.window.actiongroup.get_action('fullscreen').set_active(False)
    elif event.keyval == gtk.keysyms.F11:
        main.window.actiongroup.get_action('fullscreen').activate()

    # =======================================================
    # Zooming commands for manual zoom mode. These keys 
    # complement others (with the same action) defined as 
    # accelerators.
    # =======================================================
    elif event.keyval in [gtk.keysyms.plus, gtk.keysyms.equal]:
        main.window.actiongroup.get_action('zin').activate()
    elif event.keyval == gtk.keysyms.minus:
        main.window.actiongroup.get_action('zout').activate()
    elif (event.keyval in [gtk.keysyms._0, gtk.keysyms.KP_0] and 
      'GDK_CONTROL_MASK' in event.state.value_names):
        main.window.actiongroup.get_action('zoriginal').activate()
    
    # =======================================================
    # Arrow keys scroll the image, except in
    # fit-to-screen mode where they flip pages.
    # =======================================================
    elif event.keyval == gtk.keysyms.Down:
        if not main.window.zoom_mode == 'fit':
            main.scroll(0, 30)
        else:
            main.next_page()
    elif event.keyval == gtk.keysyms.Up:
        if not main.window.zoom_mode == 'fit':
            main.scroll(0, -30)
        else:
            main.previous_page()
    elif event.keyval == gtk.keysyms.Right:
        if not main.window.zoom_mode == 'fit':
            main.scroll(30, 0)
        else:
            main.next_page()
    elif event.keyval == gtk.keysyms.Left:
        if not main.window.zoom_mode == 'fit':
            main.scroll(-30, 0)
        else:
            main.previous_page()

    # =======================================================
    # Space key scrolls down a percentage of the window height
    # or the image height at a time.
    # When at the bottom it flips to the next page. 
    # 
    # It also has a "smart scrolling mode" in which we try
    # to follow the flow of the comic.
    # =======================================================
    elif event.keyval == gtk.keysyms.space:
        if preferences.prefs['space scroll type'] == 'window':
            x_step, y_step = main.window.get_layout_size()
        elif preferences.prefs['space scroll type'] == 'image':
            x_step, y_step = main.window.main_layout.get_size()
        x_step = x_step * preferences.prefs['space scroll length'] // 100
        y_step = y_step * preferences.prefs['space scroll length'] // 100
        if 'GDK_SHIFT_MASK' in event.state.value_names:
            next_page_function = main.previous_page
            startfirst = 'endfirst'
            x_step *= -1
            y_step *= -1
        else:
            next_page_function = main.next_page
            startfirst = 'startfirst'
            
        
        if main.window.manga_mode:
            x_step *= -1
        # FIXME: Smart space in DP mode is not implemented
        if preferences.prefs['smart space scroll']:
            if not main.is_double():
                if not main.scroll(x_step, 0):
                    if not main.scroll(0, y_step):
                        next_page_function()
                    else:
                        main.scroll_to_fixed(horiz=startfirst)

        else:           
            if main.window.zoom_mode == 'fit' or not main.scroll(0, y_step):
                next_page_function()

    # =======================================================
    # We kill the signals here for the Up, Down, Space and 
    # Enter keys. Otherwise they will start fiddling with
    # the thumbnail selector - we don't want that.
    # =======================================================
    if (event.keyval in [gtk.keysyms.Up, gtk.keysyms.Down,
      gtk.keysyms.space, gtk.keysyms.KP_Enter] or 
      (event.keyval == gtk.keysyms.Return and not
      'GDK_MOD1_MASK' in event.state.value_names)):
        main.window.emit_stop_by_name("key_press_event")
        return True
    else:
        return False

def scroll_wheel_event(widget, event, *args):
    
    ''' Catches scroll wheel events and takes the appropriate
    actions. The scroll wheel flips pages in fit-to-screen mode
    and scrolls the scrollbars when not. With a preference set,
    three successive scrolls at the top or bottom of the page will
    flip pages when not in fit-to-screen mode as well. '''

    if event.direction == gtk.gdk.SCROLL_UP:
        if main.window.zoom_mode == 'fit':
            main.previous_page()
        else:
            main.scroll(0, -50)
    elif event.direction == gtk.gdk.SCROLL_DOWN:
        if main.window.zoom_mode == 'fit':
            main.next_page()
        else:
            main.scroll(0, 50)
    elif event.direction == gtk.gdk.SCROLL_RIGHT:
        main.next_page()
    elif event.direction == gtk.gdk.SCROLL_LEFT:
        main.previous_page()

def mouse_press_event(*args):
    
    ''' Handles mouse click events on the main window. '''

    print args
    
    if self.exit:
        return False
    
    self.scroll_events_down = 0
    self.scroll_events_up = 0
    self.set_cursor_type('normal')
    if self.slideshow_started:
        self.stop_slideshow()
        self.slideshow_stopped_by_mouse = True
        return
    
    if event.button == 3:
        self.ui.get_widget('/Pop').popup(None, None, None, event.button,
            event.time)
    elif event.button == 1:
        self.x_drag_position = event.x_root
        self.y_drag_position = event.y_root
        self.mouse_moved_while_drag = 0
        self.old_vadjust_value = self.vadjust.value
        self.old_hadjust_value = self.hadjust.value
    elif event.button == 2:
        if self.scroll_wheel_event_id != None:
            self.layout.disconnect(self.scroll_wheel_event_id)
            self.scroll_wheel_event_id = None
        self.zooming_lens(event.x, event.y, event.time)

def mouse_button_release_event(self, widget, event):
    
    ''' Handles mouse button release events on the main window. '''
    
    if self.exit:
        return False
    if self.slideshow_stopped_by_mouse:
        self.slideshow_stopped_by_mouse = False
        self.set_cursor_type('normal')
        return
    
    self.set_cursor_type('normal')
    if self.mouse_moved_while_drag == 0 and event.button == 1:
        self.next_page(None)
    if event.button == 2 and self.z_pressed:
        self.actiongroup.get_action('Lens').set_active(False)
    if self.scroll_wheel_event_id == None:
        self.scroll_wheel_event_id = \
            self.layout.connect('scroll_event', self.scroll_wheel_event)

