# -*- coding: utf-8 -*-
# ============================================================================
# about.py - About dialog for Comix.
# ============================================================================

import os
import sys

import gtk

import constants

dialog = None

class AboutDialog(gtk.Dialog):

    def __init__(self, window):
        gtk.Dialog.__init__(self, _('About'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_has_separator(False)
        self.set_resizable(False)
        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook, False, False, 0)

        self.connect('response', dialog_close)
        self.connect('delete_event', dialog_close)
        
        # ----------------------------------------------------------------
        # About tab.
        # ----------------------------------------------------------------
        box = gtk.VBox(False, 0)
        box.set_border_width(5)
                
        if os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(
            sys.argv[0])), 'images/logo/comix.svg')):
            icon_path = \
                os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),
                'images/logo/comix.svg')
        else:
            for prefix in [os.path.dirname(os.path.dirname(sys.argv[0])),
                '/usr', '/usr/local', '/usr/X11R6']:
                icon_path = \
                    os.path.join(prefix,
                    'share/icons/hicolor/scalable/apps/comix.svg')
                if os.path.isfile(icon_path):
                    break
        try:
            icon_pixbuf = \
                gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 150, 150)
            icon_image = gtk.Image()
            icon_image.set_from_pixbuf(icon_pixbuf)
            box.pack_start(icon_image, False, False, 10)
        except:
            print '! Could not find the file "comix.svg"\n'
        
        label = gtk.Label()
        label.set_markup(
        '<big><big><big><big><b><span foreground="#333333">Com</span>' +
        '<span foreground="#79941b">ix</span> <span foreground="#333333">' +
        constants.version +
        '</span></b></big></big></big></big>\n' +
        "\n" +
        _("Comix is an image viewer specifically designed to handle comic books.") +
        "\n" +
        _("It reads ZIP, RAR and tar archives (also gzip or bzip2 compressed)") +
        "\n" +
        _("as well as plain image files.") + "\n" +
        "\n" +
        _("Comix is licensed under the GNU General Public License.") + "\n" +
        "\n" +
        "<small>Copyright © 2005-2007 Pontus Ekberg\n\n" +
        "herrekberg@users.sourceforge.net</small>\n" +
        "<small>http://comix.sourceforge.net</small>\n")
        box.pack_start(label, True, True, 0)
        label.set_justify(gtk.JUSTIFY_CENTER)
        
        notebook.insert_page(box, gtk.Label(_("About")))
        
        # ----------------------------------------------------------------
        # Credits tab.
        # ----------------------------------------------------------------
        box = gtk.VBox(False, 5)
        box.set_border_width(5)

        for nice_person, description in (
            ('Pontus Ekberg', _('Developer and Swedish translation')),
            ('Emfox Zhou &amp; Xie Yanbo',
            _('Simplified Chinese translation')),
            ('Manuel Quiñones', _('Spanish translation')),
            ('Marcelo Góes', _('Brazilian Portuguese translation')),
            ('Christoph Wolk',
            _('German translation and Nautilus thumbnailer')),
            ('Raimondo Giammanco &amp; GhePeU', _('Italian translation')),
            ('Arthur Nieuwland', _('Dutch translation')),
            ('Achraf Cherti', _('French translation')),
            ('Kamil Leduchowski', _('Polish translation')),
            ('Paul Chatzidimitriou', _('Greek translation')),
            ('Carles Escrig', _('Catalan translation')),
            ('Hsin-Lin Cheng', _('Traditional Chinese translation')),
            ('Mamoru Tasaka', _('Japanese translation')),
            ('Ernő Drabik', _('Hungarian translation')),
            ('Artyom Smirnov', _('Russian translation')),
            ('Adrian C.', _('Croatian translation')),
            ('Jan Nekvasil', _('Czech translation'))
            ):
            label = gtk.Label()
            label.set_markup('<b>' + nice_person + ':</b>   ' +
                description)
            box.pack_start(label, False, False, 0)
            label.set_alignment(0, 0)

        notebook.insert_page(box, gtk.Label(_("Credits")))
        self.action_area.get_children()[0].grab_focus()
        self.vbox.show_all()
        

def dialog_open(*args):
    global dialog
    if dialog == None:
        dialog = AboutDialog(None)
        dialog.show()

def dialog_close(*args):
    global dialog
    if dialog != None:
        dialog.destroy()
        dialog = None

