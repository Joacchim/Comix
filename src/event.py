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
    # FIXME: Not pixel-exact
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
        #if main.window.is_fullscreen:
        main.window.actiongroup.get_action('fullscreen').set_active(False)
    elif event.keyval == gtk.keysyms.F11:
        #if main.window.is_fullscreen:
        main.window.actiongroup.get_action('fullscreen').activate()
        #else:
        #    main.window.actiongroup.get_action('fullscreen').set_active(True)

    # =======================================================
    # Zooming commands for manual zoom mode. These keys 
    # complement others (with the same action) defined as 
    # accelerators.
    # =======================================================
    elif event.keyval in [gtk.keysyms.plus, gtk.keysyms.equal]:
        self.zoom_in(None)
    elif event.keyval == gtk.keysyms.minus:
        self.zoom_out(None)
    elif (event.keyval in [gtk.keysyms._0, gtk.keysyms.KP_0] and 
        'GDK_CONTROL_MASK' in event.state.value_names):
        self.zoom_original(None)
    
    # =======================================================
    # Arrow keys scroll the image, except in
    # fit-to-screen mode where they flip pages.
    # =======================================================
    elif event.keyval == gtk.keysyms.Down:
        self.scroll_events_up = 0
        if not self.prefs['zoom mode'] == 1 or self.show_comments:
            height = self.layout.get_size()[1]
            if (self.vadjust.get_value() >= height - self.main_layout_y_size):
                 if self.prefs['flip with wheel']:
                     self.scroll_events_down += 1
                     if self.scroll_events_down > 2:
                         self.next_page(None)
                         self.scroll_events_down = 0
            elif (self.vadjust.get_value() + 20 > height -
                self.main_layout_y_size):
                self.vadjust.set_value(height - self.main_layout_y_size)
            else:
                self.vadjust.set_value(self.vadjust.get_value() + 20)
        else:
            self.next_page(None)
    elif event.keyval == gtk.keysyms.Up:
        self.scroll_events_down = 0
        if not self.prefs['zoom mode'] == 1 or self.show_comments:
            if self.vadjust.get_value() <= 0:
                if self.prefs['flip with wheel']:
                    self.scroll_events_up += 1
                    if self.scroll_events_up > 2:
                        self.previous_page(None)
                        self.scroll_events_up = 0
            elif self.vadjust.get_value() - 20 < 0:
                self.vadjust.set_value(0)
            else:
                self.vadjust.set_value(self.vadjust.get_value() - 20)
        else:
            self.previous_page(None)
    elif event.keyval == gtk.keysyms.Right:
        if not self.prefs['zoom mode'] == 1 or self.show_comments:
            if (self.hadjust.get_value() + 20 >
                self.layout.get_size()[0] - self.main_layout_x_size):
                self.hadjust.set_value(self.layout.get_size()[0] -
                    self.main_layout_x_size)
            else:
                self.hadjust.set_value(self.hadjust.get_value() + 20)
        else:
            self.next_page(None)
    elif event.keyval == gtk.keysyms.Left:
        if not self.prefs['zoom mode'] == 1 or self.show_comments:
            if self.hadjust.get_value() - 20 < 0:
                self.hadjust.set_value(0)
            else:
                self.hadjust.set_value(self.hadjust.get_value() - 20)
        else:
            self.previous_page(None)
    
    # =======================================================
    # Space key scrolls down one "window height" at the time,
    # or a predefined percentage of the image height.
    # When at the bottom it flips to the next page. 
    # 
    # It also has a "smart scrolling mode", in which we also
    # scroll sideways.
    # See the tooltip for the preference for more info.
    #
    # FIXME: Can't this be made cleaner? And get rid of the
    # damn Indentations-From-Outer-Space (TM) as well.
    # =======================================================
    elif event.keyval == gtk.keysyms.space:
        if self.prefs['zoom mode'] == 1 and not self.show_comments:
            self.next_page(None)
        else:
            height = self.layout.get_size()[1]
            max_vadjust_value = height - self.main_layout_y_size
            if self.prefs['space scroll type']:
                vscroll = \
                    self.prefs['space scroll length'] * 0.01 * height
            else:
                vscroll = \
                    self.prefs['space scroll length'] * 0.01 * \
                    self.main_layout_y_size
            # =======================================================
            # No smart scrolling, simply go down or flip page.
            # =======================================================
            if not self.prefs['smart space scroll']:
                if self.vadjust.get_value() >= max_vadjust_value:
                    self.next_page(None)
                else:
                    if (self.vadjust.get_value() + vscroll >=
                       max_vadjust_value):
                       self.vadjust.set_value(max_vadjust_value)
                    else:
                        self.vadjust.set_value(
                            self.vadjust.get_value() + vscroll)
            else:
                # =======================================================
                # Smart scrolling, this is trickier. We now go 
                # left to right before going down, and keeps double page
                # mode in mind (which can be emulated).
                # =======================================================
                if (self.prefs['double page'] and self.file_number < 
                    len(self.file) - 1):
                    double_page = True
                    im1_width = self.image1_scaled_width
                    im2_width = self.image2_scaled_width
                elif self.prefs['emulate double page']:
                    double_page = True
                    # When emulating double page mode we assume both
                    # pages are the same size.
                    im1_width = self.image1_scaled_width // 2
                    im2_width = im1_width
                else:
                    double_page = False
                    im1_width = self.image1_scaled_width
                    im2_width = 0
                width = im1_width + im2_width + 2
                max_hadjust_value = width - self.main_layout_x_size
                middle_hadjust_value = \
                    min(im1_width, max_hadjust_value)
                if self.prefs['space scroll type']:
                    hscroll = \
                        self.prefs['space scroll length'] * 0.01 * width
                else:
                    hscroll = \
                        self.prefs['space scroll length'] * 0.01 * \
                        self.main_layout_x_size
                # =======================================================
                # Single page mode.
                # =======================================================
                if not double_page:
                    # No manga mode.
                    if not self.prefs['manga']:
                        if self.hadjust.get_value() >= max_hadjust_value:
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.next_page(None)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(0)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(0)
                        else:
                            if (self.hadjust.get_value() + hscroll >=
                                max_hadjust_value):
                                self.hadjust.set_value(max_hadjust_value)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() + hscroll)
                    # Manga mode.
                    else:
                        if self.hadjust.get_value() <= 0:
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.next_page(None)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(max_hadjust_value)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(max_hadjust_value)
                        else:
                            if self.hadjust.get_value() - hscroll <= 0:
                                self.hadjust.set_value(0)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() - hscroll)
                # =======================================================
                # Double page mode.
                # =======================================================
                else:
                    # No manga mode.
                    if not self.prefs['manga']:
                        # Move right on first page.
                        if (self.hadjust.get_value() <
                            middle_hadjust_value -
                            self.main_layout_x_size):
                            if (self.hadjust.get_value() + hscroll >=
                                middle_hadjust_value - 
                                self.main_layout_x_size):
                                self.hadjust.set_value(
                                    middle_hadjust_value -
                                    self.main_layout_x_size)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() + hscroll)
                        # Move right on second page.
                        elif (self.hadjust.get_value() < 
                            max_hadjust_value and 
                            self.hadjust.get_value() >=
                            middle_hadjust_value):
                            if (self.hadjust.get_value() + hscroll >=
                                max_hadjust_value):
                                self.hadjust.set_value(
                                    max_hadjust_value)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() + hscroll)
                        # Move down on first page.
                        elif (middle_hadjust_value - 
                            self.main_layout_x_size <=
                            self.hadjust.get_value() < 
                            middle_hadjust_value):
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.vadjust.set_value(0)
                                self.hadjust.set_value(
                                    middle_hadjust_value)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(0)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(0)
                        # Move down on second page.
                        elif (self.hadjust.get_value() >= 
                            max_hadjust_value):
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.next_page(None)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(
                                    middle_hadjust_value)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(
                                    middle_hadjust_value)
                    # Manga mode.
                    else:
                        # Move left on first page.
                        if (self.hadjust.get_value() >
                            max(0, middle_hadjust_value)):
                            if (self.hadjust.get_value() - hscroll <=
                                middle_hadjust_value):
                                self.hadjust.set_value(
                                    middle_hadjust_value)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() - hscroll)
                        # Move left on second page.
                        elif (self.hadjust.get_value() <=  
                            middle_hadjust_value - 
                            self.main_layout_x_size and 
                            self.hadjust.get_value() > 0):
                            if self.hadjust.get_value() - hscroll <= 0:
                                self.hadjust.set_value(0)
                            else:
                                self.hadjust.set_value(
                                    self.hadjust.get_value() - hscroll)
                        # Move down on first page.
                        elif (middle_hadjust_value -
                            self.main_layout_x_size <
                            self.hadjust.get_value() <= 
                            middle_hadjust_value and 
                            self.hadjust.get_value() > 0):
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.vadjust.set_value(0)
                                self.hadjust.set_value(
                                    middle_hadjust_value - 
                                    self.main_layout_x_size)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(max_hadjust_value)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(max_hadjust_value)
                        # Move down on second page.
                        elif self.hadjust.get_value() <= 0:
                            if (self.vadjust.get_value() >=
                                max_vadjust_value):
                                self.next_page(None)
                            elif (self.vadjust.get_value() + vscroll >=
                                max_vadjust_value):
                                self.vadjust.set_value(max_vadjust_value)
                                self.hadjust.set_value(
                                    middle_hadjust_value - 
                                    self.main_layout_x_size)
                            else:
                                self.vadjust.set_value(
                                    self.vadjust.get_value() + vscroll)
                                self.hadjust.set_value(
                                    middle_hadjust_value -
                                    self.main_layout_x_size)

    # =======================================================
    # We kill the signals here for the Up, Down, Space and 
    # Enter keys. Otherwise they will start moving
    # the thumbnail selector, we don't want that.
    # =======================================================
    if (event.keyval in [gtk.keysyms.Up, gtk.keysyms.Down,
        gtk.keysyms.space, gtk.keysyms.KP_Enter] or 
        (event.keyval == gtk.keysyms.Return and not
        'GDK_MOD1_MASK' in event.state.value_names)):
        self.window.emit_stop_by_name("key_press_event")
        return True
    else:
        return False

