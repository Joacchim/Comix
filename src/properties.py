import gtk

class Propertiesdialog(gtk.Dialog)

    def __init__(self, window):
        
        ''' Creates the properties dialog and all its widgets. '''
        
        gtk.Dialog.__init__(self, _("Properties"), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)))

        self.properties_dialog.set_resizable(False)
        self.properties_label = gtk.Label()
        self.properties_label2 = gtk.Label()
        self.properties_notebook = gtk.Notebook()
        self.properties_dialog.vbox.pack_start(
            self.properties_notebook, False, False, 0)
        
        self.properties_dialog.set_has_separator(False)
        self.properties_label.set_justify(gtk.JUSTIFY_RIGHT)
        self.properties_dialog.vbox.show_all()

    def open(self, archive_type, filelist, transp_background):
        
        ''' Opens the properties dialog and updates it's information. '''
        
        if self.exit:
            return False
        
        # FIXME: This is ugly code.

        for child in self.properties_notebook.get_children():
            child.destroy()
        
        # =======================================================
        # Archive tab.
        # =======================================================
        if archive_type != '':
            main_box = gtk.VBox(False, 10)
            main_box.set_border_width(10)
            hbox = gtk.HBox(False, 10)
            main_box.pack_start(hbox, False, False, 0)
            try:
                cover_pixbuf = \
                    gtk.gdk.pixbuf_new_from_file_at_size(filelist[0], 200, 128)
                pixmap = \
                    gtk.gdk.Pixmap(self.window.window,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2, -1)
                pixmap.draw_rectangle(transp_background, True, 0, 0,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2)
                pixmap.draw_pixbuf(None, cover_pixbuf, 0, 0, 1, 1, -1, -1,
                    gtk.gdk.RGB_DITHER_MAX, 0, 0)
                gc = pixmap.new_gc(gtk.gdk.Color(0, 0, 0))
                pixmap.draw_line(gc, 0, 0, cover_pixbuf.get_width() + 1, 0)
                pixmap.draw_line(gc, 0, 0, 0, cover_pixbuf.get_height() + 1)
                pixmap.draw_line(gc, cover_pixbuf.get_width() + 1, 0,
                    cover_pixbuf.get_width() + 1,
                    cover_pixbuf.get_height() + 1)
                pixmap.draw_line(gc, 0, cover_pixbuf.get_height() + 1,
                    cover_pixbuf.get_width() + 1,
                    cover_pixbuf.get_height() + 1)
                cover_pixbuf = \
                    gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2)
                cover_pixbuf.get_from_drawable(pixmap,
                    gtk.gdk.colormap_get_system(), 0, 0, 0, 0, -1, -1)
                cover_image = gtk.Image()
                cover_image.set_from_pixbuf(cover_pixbuf)
            except:
                cover_image = None
            if cover_image != None:
                hbox.pack_start(cover_image, False, False, 2)
            vbox = gtk.VBox(False, 2)
            vbox.set_border_width(6)
            ebox = gtk.EventBox()
            ebox.set_border_width(1)
            cmap = ebox.get_colormap()
            ebox.modify_bg(gtk.STATE_NORMAL, cmap.alloc_color('#eadfc6'))
            ebox.add(vbox)
            ebox2 = gtk.EventBox()
            ebox2.modify_bg(gtk.STATE_NORMAL, cmap.alloc_color('#888888'))
            ebox2.add(ebox)
            hbox.pack_start(ebox2, True, True, 2)
            filename = \
                ' ' + self.to_unicode(os.path.basename(self.path))
            if len(filename) > 35:
                filename = filename[:32] + '...'
            label = gtk.Label(filename)
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            vbox.pack_start(gtk.Alignment(0, 0, 0, 0), True, False, 0)
            label = gtk.Label(' ' + str(len(self.file)) + ' ' + _('pages'))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            if len(self.comment) == 1:
                label = gtk.Label(' ' + '1 ' + _('comment'))
            else:
                label = \
                    gtk.Label(' ' + str(len(self.comment)) + ' ' +
                    _('comments'))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = gtk.Label(' ' + self.archive_type)
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(' ' + str('%.1f' %
                (os.path.getsize(self.path) / 1048576.0)) + ' MiB')
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            vbox = gtk.VBox(False, 6)
            main_box.pack_start(vbox, False, False, 2)
            filename = ' ' + self.to_unicode(os.path.dirname(self.path))
            if len(filename) > 45:
                filename = filename[:42] + '...'
            label = \
                gtk.Label(_('Location') + ':  ' + filename)
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            hash = md5.new()
            hash.update(self.path)
            hash = hash.hexdigest()
            if os.path.isfile(os.getenv('HOME') + '/.comix/library/' + hash):
                label = \
                    gtk.Label(_('In library') + ':  ' + _('Yes'))
            else:
                label = \
                    gtk.Label(_('In library') + ':  ' + _('No'))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            if self.path in self.bookmarks:
                label = \
                    gtk.Label(_('Bookmarked') + ':  ' + _('Yes, page') + ' ' +
                    str(self.bookmark_numbers[self.bookmarks.index(
                    self.path)]))
            else:
                label = \
                    gtk.Label(_('Bookmarked') + ':  ' + _('No'))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Accessed') + ':  ' +
                    time.strftime('%Y-%m-%d   [%H:%M:%S]',
                    time.localtime(os.stat(self.path)[stat.ST_ATIME])))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Modified') + ':  ' +
                    time.strftime('%Y-%m-%d   [%H:%M:%S]',
                    time.localtime(os.stat(self.path)[stat.ST_MTIME])))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Permissions') + ':  ' +
                    str(oct(stat.S_IMODE(os.stat(self.path)[stat.ST_MODE]))))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Owner') + ':  ' +
                    pwd.getpwuid(os.stat(self.path)[stat.ST_UID])[0])
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            self.properties_notebook.insert_page(main_box,
                gtk.Label(_('Archive')))
        
        # =======================================================
        # Image (1) tab
        # =======================================================
        top_hbox = gtk.HBox(False, 5)
        main_box = gtk.VBox(False, 10)
        top_hbox.pack_start(main_box)
        top_hbox.set_border_width(10)
        hbox = gtk.HBox(False, 10)
        main_box.pack_start(hbox, False, False, 0)
        try:
            cover_pixbuf = \
                gtk.gdk.pixbuf_new_from_file_at_size(
                self.file[self.file_number], 200, 128)
            pixmap = \
                gtk.gdk.Pixmap(self.window.window,
                cover_pixbuf.get_width() + 2,
                cover_pixbuf.get_height() + 2, -1)
            pixmap.draw_rectangle(self.gdk_gc, True, 0, 0,
                cover_pixbuf.get_width() + 2,
                cover_pixbuf.get_height() + 2)
            pixmap.draw_pixbuf(None, cover_pixbuf, 0, 0, 1, 1, -1, -1,
                gtk.gdk.RGB_DITHER_MAX, 0, 0)
            gc = pixmap.new_gc(gtk.gdk.Color(0, 0, 0))
            pixmap.draw_line(gc, 0, 0, cover_pixbuf.get_width() + 1, 0)
            pixmap.draw_line(gc, 0, 0, 0, cover_pixbuf.get_height() + 1)
            pixmap.draw_line(gc, cover_pixbuf.get_width() + 1, 0,
                cover_pixbuf.get_width() + 1, cover_pixbuf.get_height() + 1)
            pixmap.draw_line(gc, 0, cover_pixbuf.get_height() + 1,
                cover_pixbuf.get_width() + 1, cover_pixbuf.get_height() + 1)
            cover_pixbuf = \
                gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                cover_pixbuf.get_width() + 2, cover_pixbuf.get_height() + 2)
            cover_pixbuf.get_from_drawable(pixmap,
                gtk.gdk.colormap_get_system(), 0, 0, 0, 0, -1, -1)
            cover_image = gtk.Image()
            cover_image.set_from_pixbuf(cover_pixbuf)
        except:
            cover_image = None
        if cover_image != None:
            hbox.pack_start(cover_image, False, False, 2)
        vbox = gtk.VBox(False, 2)
        vbox.set_border_width(6)
        ebox = gtk.EventBox()
        ebox.set_border_width(1)
        map = ebox.get_colormap()
        ebox.modify_bg(gtk.STATE_NORMAL, map.alloc_color('#eadfc6'))
        ebox.add(vbox)
        ebox2 = gtk.EventBox()
        ebox2.modify_bg(gtk.STATE_NORMAL, map.alloc_color('#888888'))
        ebox2.add(ebox)
        hbox.pack_start(ebox2, True, True, 2)
        if self.archive_type != '':
            label = \
                gtk.Label(' ' + _('Page') + ' ' + str(self.file_number + 1))
        else:
            filename = \
                ' ' + self.to_unicode(os.path.basename(
                self.file[self.file_number]))
            if len(filename) > 35:
                filename = filename[:32] + '...'
            label = gtk.Label(filename)
        label.set_alignment(0, 0)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        vbox.pack_start(gtk.Alignment(0, 0, 0, 0), True, False, 0)
        label = \
            gtk.Label(' ' + str(self.image1_width) + 'x' +
            str(self.image1_height) + ' px')
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = \
            gtk.Label(' ' + str(self.image1_scaled_width) + 'x' +
            str(self.image1_scaled_height) + ' px (' +
            str('%.1f' % (100.0 * self.image1_scaled_width /
            self.image1_width)) + ' %)')
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = gtk.Label(' ' + gtk.gdk.pixbuf_get_file_info(self.file
            [self.file_number])[0]['mime_types'][0][6:].upper())
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = \
            gtk.Label(' ' + str('%.1f' %
            (os.path.getsize(self.file[self.file_number]) /
            1024.0)) + ' kiB')
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        
        vbox = gtk.VBox(False, 6)
        main_box.pack_start(vbox, True, True, 2)
        filename = \
            ' ' + self.to_unicode(os.path.dirname(
            self.file[self.file_number]))
        if len(filename) > 45:
            filename = filename[:42] + '...'
        label = gtk.Label(_('Location') + ':  ' + filename)
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        
        label = \
            gtk.Label(_('Accessed') + ':  ' +
                time.strftime('%Y-%m-%d   [%H:%M:%S]',
                time.localtime(os.stat(self.file[self.file_number])
                [stat.ST_ATIME])))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = \
            gtk.Label(_('Modified') + ':  ' +
                time.strftime('%Y-%m-%d   [%H:%M:%S]',
                time.localtime(os.stat(self.file[self.file_number])
                [stat.ST_MTIME])))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = \
            gtk.Label(_('Permissions') + ':  ' +
                str(oct(stat.S_IMODE(os.stat(self.file[self.file_number])
                [stat.ST_MODE]))))
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        label = \
            gtk.Label(_('Owner') + ':  ' +
                pwd.getpwuid(os.stat(self.file[self.file_number])
                [stat.ST_UID])[0])
        label.set_alignment(0, 0.5)
        attrlist = pango.AttrList()
        attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrlist)
        vbox.pack_start(label, False, False, 2)
        
        top_hbox.pack_start(gtk.VSeparator(), False, False, 5)
        expander = gtk.Expander()
        top_hbox.pack_start(expander, False, False, 0)
        hist_box = gtk.VBox(False, 2)
        hist_image, mean, median, stddev, pixels, sum, extrema, mode = \
            self.draw_histogram(self.stored_pixbuf, self.file_number)
        
        label = gtk.Label(_('Mode') + ':  ' + mode)
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        hist_box.pack_start(label, False, False, 2)
        label = gtk.Label(_('Pixel count') + ':  ' + str(pixels))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            label.get_text().index(':') + 1))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        hist_box.pack_start(label, False, False, 2)

        hist_box.pack_start(gtk.HSeparator(), False, False, 6)
        hbox = gtk.HBox(False, 30)
        hist_box.pack_start(hbox)

        label_box = gtk.VBox(False, 2)
        label = gtk.Label(_('Pixel sum'))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('R' + ':  ' + str(int(sum[0])))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('G' + ':  ' + str(int(sum[1])))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('B' + ':  ' + str(int(sum[2])))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        hbox.pack_start(label_box, False, False, 2)
        
        label_box = gtk.VBox(False, 2)
        label = gtk.Label(_('Extrema'))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('R' + ':  ' + str(extrema[0][0]) + '  -  ' +
            str(extrema[0][1]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('G' + ':  ' + str(extrema[1][0]) + '  -  ' +
            str(extrema[1][1]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = \
            gtk.Label('B' + ':  ' + str(extrema[2][0]) + '  -  ' +
            str(extrema[2][1]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        hbox.pack_start(label_box, False, False, 2)

        hist_image.set_alignment(0, 0.5)
        hist_box.pack_start(hist_image, False, False, 10)
        hbox = gtk.HBox(False, 20)
        hist_box.pack_start(hbox, False, False, 2)

        label_box = gtk.VBox(False, 2)
        label = gtk.Label(_('Mean'))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('R:  ' + '%3.1f' % mean[0])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('G:  ' + '%3.1f' % mean[1])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('B:  ' + '%3.1f' % mean[2])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        hbox.pack_start(label_box, False, False, 0)

        label_box = gtk.VBox(False, 2)
        label = gtk.Label(_('Median'))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('R:  ' + str(median[0]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('G:  ' + str(median[1]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('B:  ' + str(median[2]))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        hbox.pack_start(label_box, False, False, 0)

        label_box = gtk.VBox(False, 2)
        label = gtk.Label(_('Standard deviation'))
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
            len(label.get_text())))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('R:  ' + '%3.1f' % stddev[0])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('G:  ' + '%3.1f' % stddev[1])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        label = gtk.Label('B:  ' + '%3.1f' % stddev[2])
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
        label.set_attributes(attrs)
        label.set_alignment(0, 0.5)
        label_box.pack_start(label, False, False, 2)
        hbox.pack_start(label_box, False, False, 0)
        
        expander.add(hist_box)

        if (not self.prefs['double page'] or
            self.file_number == len(self.file) - 1):
            self.properties_notebook.insert_page(top_hbox,
                gtk.Label(_('Image')))
        else:
            self.properties_notebook.insert_page(top_hbox,
                gtk.Label(_('Image 1')))
        
        # =======================================================
        # Image (2) tab
        # =======================================================
        if (self.prefs['double page'] and 
            self.file_number != len(self.file) - 1):
            top_hbox = gtk.HBox(False, 5)
            main_box = gtk.VBox(False, 10)
            top_hbox.pack_start(main_box)
            top_hbox.set_border_width(10)
            hbox = gtk.HBox(False, 10)
            main_box.pack_start(hbox, False, False, 0)
            try:
                cover_pixbuf = \
                    gtk.gdk.pixbuf_new_from_file_at_size(
                    self.file[self.file_number + 1], 200, 128)
                pixmap = \
                    gtk.gdk.Pixmap(self.window.window,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2, -1)
                pixmap.draw_rectangle(self.gdk_gc, True, 0, 0,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2)
                pixmap.draw_pixbuf(None, cover_pixbuf, 0, 0, 1, 1, -1, -1,
                    gtk.gdk.RGB_DITHER_MAX, 0, 0)
                gc = pixmap.new_gc(gtk.gdk.Color(0, 0, 0))
                pixmap.draw_line(gc, 0, 0, cover_pixbuf.get_width() + 1, 0)
                pixmap.draw_line(gc, 0, 0, 0, cover_pixbuf.get_height() + 1)
                pixmap.draw_line(gc, cover_pixbuf.get_width() + 1, 0,
                    cover_pixbuf.get_width() + 1,
                    cover_pixbuf.get_height() + 1)
                pixmap.draw_line(gc, 0, cover_pixbuf.get_height() + 1,
                    cover_pixbuf.get_width() + 1,
                    cover_pixbuf.get_height() + 1)
                cover_pixbuf = \
                    gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                    cover_pixbuf.get_width() + 2,
                    cover_pixbuf.get_height() + 2)
                cover_pixbuf.get_from_drawable(pixmap,
                    gtk.gdk.colormap_get_system(), 0, 0, 0, 0, -1, -1)
                cover_image = gtk.Image()
                cover_image.set_from_pixbuf(cover_pixbuf)
            except:
                cover_image = None
            if cover_image != None:
                hbox.pack_start(cover_image, False, False, 2)
            vbox = gtk.VBox(False, 2)
            vbox.set_border_width(6)
            ebox = gtk.EventBox()
            ebox.set_border_width(1)
            map = ebox.get_colormap()
            ebox.modify_bg(gtk.STATE_NORMAL, map.alloc_color('#eadfc6'))
            ebox.add(vbox)
            ebox2 = gtk.EventBox()
            ebox2.modify_bg(gtk.STATE_NORMAL, map.alloc_color('#888888'))
            ebox2.add(ebox)
            hbox.pack_start(ebox2, True, True, 2)
            if self.archive_type != '':
                label = \
                    gtk.Label(' ' + _('Page') + ' ' +
                    str(self.file_number + 2))
            else:
                filename = \
                    ' ' + self.to_unicode(os.path.basename(
                    self.file[self.file_number + 1]))
                if len(filename) > 35:
                    filename = filename[:32] + '...'
                label = gtk.Label(filename)
            label.set_alignment(0, 0)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            vbox.pack_start(gtk.Alignment(0, 0, 0, 0), True, False, 0)
            label = \
                gtk.Label(' ' + str(self.image2_width) + 'x' +
                str(self.image2_height) + ' px')
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(' ' + str(self.image2_scaled_width) + 'x' +
                str(self.image2_scaled_height) + ' px (' +
                str('%.1f' % (100.0 * self.image2_scaled_width /
                self.image2_width)) + ' %)')
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = gtk.Label(' ' + gtk.gdk.pixbuf_get_file_info(self.file
                [self.file_number + 1])[0]['mime_types'][0][6:].upper())
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(' ' + str('%.1f' %
                (os.path.getsize(self.file[self.file_number + 1]) /
                1024.0)) + ' kiB')
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            vbox = gtk.VBox(False, 6)
            main_box.pack_start(vbox, True, True, 2)
            filename = \
                ' ' + self.to_unicode(os.path.dirname(
                self.file[self.file_number + 1]))
            if len(filename) > 45:
                filename = filename[:42] + '...'
            label = gtk.Label(_('Location') + ':  ' + filename)
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            label = \
                gtk.Label(_('Accessed') + ':  ' +
                    time.strftime('%Y-%m-%d   [%H:%M:%S]',
                    time.localtime(os.stat(self.file[self.file_number + 1])
                    [stat.ST_ATIME])))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Modified') + ':  ' +
                    time.strftime('%Y-%m-%d   [%H:%M:%S]',
                    time.localtime(os.stat(self.file[self.file_number + 1])
                    [stat.ST_MTIME])))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Permissions') + ':  ' +
                str(oct(stat.S_IMODE(os.stat(
                self.file[self.file_number + 1])[stat.ST_MODE]))))
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            label = \
                gtk.Label(_('Owner') + ':  ' +
                    pwd.getpwuid(os.stat(self.file[self.file_number + 1])
                    [stat.ST_UID])[0])
            label.set_alignment(0, 0.5)
            attrlist = pango.AttrList()
            attrlist.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrlist)
            vbox.pack_start(label, False, False, 2)
            
            top_hbox.pack_start(gtk.VSeparator(), False, False, 5)
            expander = gtk.Expander()
            top_hbox.pack_start(expander, False, False, 0)
            hist_box = gtk.VBox(False, 2)
            hist_image, mean, median, stddev, pixels, sum, extrema, mode = \
                self.draw_histogram(self.stored_pixbuf2, self.file_number + 1)
            
            label = gtk.Label(_('Mode') + ':  ' + mode)
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            hist_box.pack_start(label, False, False, 2)
            label = gtk.Label(_('Pixel count') + ':  ' + str(pixels))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                label.get_text().index(':') + 1))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            hist_box.pack_start(label, False, False, 2)

            hist_box.pack_start(gtk.HSeparator(), False, False, 6)
            hbox = gtk.HBox(False, 30)
            hist_box.pack_start(hbox)

            label_box = gtk.VBox(False, 2)
            label = gtk.Label(_('Pixel sum'))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('R' + ':  ' + str(int(sum[0])))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('G' + ':  ' + str(int(sum[1])))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('B' + ':  ' + str(int(sum[2])))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            hbox.pack_start(label_box, False, False, 2)
            
            label_box = gtk.VBox(False, 2)
            label = gtk.Label(_('Extrema'))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('R' + ':  ' + str(extrema[0][0]) + '  -  ' +
                str(extrema[0][1]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('G' + ':  ' + str(extrema[1][0]) + '  -  ' +
                str(extrema[1][1]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = \
                gtk.Label('B' + ':  ' + str(extrema[2][0]) + '  -  ' +
                str(extrema[2][1]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            hbox.pack_start(label_box, False, False, 2)

            hist_image.set_alignment(0, 0.5)
            hist_box.pack_start(hist_image, False, False, 10)
            hbox = gtk.HBox(False, 20)
            hist_box.pack_start(hbox, False, False, 2)

            label_box = gtk.VBox(False, 2)
            label = gtk.Label(_('Mean'))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('R:  ' + '%3.1f' % mean[0])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('G:  ' + '%3.1f' % mean[1])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('B:  ' + '%3.1f' % mean[2])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            hbox.pack_start(label_box, False, False, 0)

            label_box = gtk.VBox(False, 2)
            label = gtk.Label(_('Median'))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('R:  ' + str(median[0]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('G:  ' + str(median[1]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('B:  ' + str(median[2]))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            hbox.pack_start(label_box, False, False, 0)

            label_box = gtk.VBox(False, 2)
            label = gtk.Label(_('Standard deviation'))
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0,
                len(label.get_text())))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('R:  ' + '%3.1f' % stddev[0])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('G:  ' + '%3.1f' % stddev[1])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            label = gtk.Label('B:  ' + '%3.1f' % stddev[2])
            attrs = pango.AttrList()
            attrs.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 2))
            label.set_attributes(attrs)
            label.set_alignment(0, 0.5)
            label_box.pack_start(label, False, False, 2)
            hbox.pack_start(label_box, False, False, 0)
            
            expander.add(hist_box)

            self.properties_notebook.insert_page(top_hbox,
                gtk.Label(_('Image 2')))
        
        self.properties_dialog.action_area.get_children()[0].grab_focus()
        self.properties_dialog.show_all()
    
    def close(self, event, data=None):
        
        ''' Hides the properties dialog. '''
        
        if self.exit:
            return False
        
        self.properties_dialog.hide()
        return True
 
