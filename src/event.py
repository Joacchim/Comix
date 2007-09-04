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
    
    #print event.keyval
    
    layout_width, layout_height = main.window.get_layout_size()
    vadjust_upper = main.window.vadjust.upper - layout_height
    hadjust_upper = main.window.hadjust.upper - layout_width

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
    #
    # FIXME: Nobody knows about this, I don't even think about
    # it myself. Write that damn documentation some time!
    # =======================================================
    if event.keyval == gtk.keysyms.KP_1:
        main.window.vadjust.set_value(vadjust_upper)
        main.window.hadjust.set_value(0)
    elif event.keyval == gtk.keysyms.KP_2:
        main.window.vadjust.set_value(vadjust_upper)
        main.window.hadjust.set_value(hadjust_upper / 2)
    elif event.keyval == gtk.keysyms.KP_3:
        main.window.vadjust.set_value(vadjust_upper)
        main.window.hadjust.set_value(hadjust_upper)
    elif event.keyval == gtk.keysyms.KP_4:
        main.window.vadjust.set_value(vadjust_upper / 2)
        main.window.hadjust.set_value(0)
    elif event.keyval == gtk.keysyms.KP_5:
        main.window.vadjust.set_value(vadjust_upper / 2)
        main.window.hadjust.set_value(hadjust_upper / 2)
    elif event.keyval == gtk.keysyms.KP_6:
        main.window.vadjust.set_value(vadjust_upper / 2)
        main.window.hadjust.set_value(hadjust_upper)
    elif event.keyval == gtk.keysyms.KP_7:
        main.window.vadjust.set_value(0)
        main.window.hadjust.set_value(0)
    elif event.keyval == gtk.keysyms.KP_8:
        main.window.vadjust.set_value(0)
        main.window.hadjust.set_value(hadjust_upper / 2)
    elif event.keyval == gtk.keysyms.KP_9:
        main.window.vadjust.set_value(0)
        main.window.hadjust.set_value(hadjust_upper)
    
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
    # It also has a "smart scrolling mode", in which we also
    # scroll sideways.
    # =======================================================
    elif event.keyval == gtk.keysyms.space:
        if preferences.prefs['space scroll type'] == 'window':
            distance = preferences.prefs['space scroll length'] * \
                main.window.get_layout_size()[1] // 100
        elif preferences.prefs['space scroll type'] == 'image':
            distance = preferences.prefs['space scroll length'] * \
                main.window.main_layout.get_size()[1] // 100
        if 'GDK_SHIFT_MASK' in event.state.value_names:
            distance *= -1

        if main.window.zoom_mode == 'fit' or not main.scroll(0, distance):
            if 'GDK_SHIFT_MASK' in event.state.value_names:
                main.previous_page()
            else:
                main.next_page()


    # =======================================================
    # We kill the signals here for the Up, Down, Space and 
    # Enter keys. Otherwise they will start moving
    # the thumbnail selector, we don't want that.
    # =======================================================
    if (event.keyval in [gtk.keysyms.Up, gtk.keysyms.Down,
      gtk.keysyms.space, gtk.keysyms.KP_Enter] or 
      (event.keyval == gtk.keysyms.Return and not
      'GDK_MOD1_MASK' in event.state.value_names)):
        main.window.emit_stop_by_name("key_press_event")
        return True
    else:
        return False

