# -*- coding: utf-8 -*-
"""about.py - About dialog."""

from os.path import join, dirname, isfile
import sys

import gtk

import constants

_dialog = None


class _AboutDialog(gtk.Dialog):

    def __init__(self, window):
        gtk.Dialog.__init__(self, _('About'), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_has_separator(False)
        self.set_resizable(False)
        self.connect('response', _close_dialog)
        self.set_default_response(gtk.RESPONSE_CLOSE)

        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook, False, False, 0)
        self.set_border_width(4)
        notebook.set_border_width(6)

        # ----------------------------------------------------------------
        # About tab.
        # ----------------------------------------------------------------
        box = gtk.VBox(False, 0)
        box.set_border_width(5)
        icon_path = join(dirname(dirname(sys.argv[0])), 'images/comix.svg')
        if not isfile(icon_path):
            for prefix in [dirname(dirname(sys.argv[0])), '/usr', '/usr/local',
              '/usr/X11R6']:
                icon_path = join(prefix,
                    'share/icons/hicolor/scalable/apps/comix.svg')
                if isfile(icon_path):
                    break
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 150, 150)
            icon = gtk.Image()
            icon.set_from_pixbuf(pixbuf)
            box.pack_start(icon, False, False, 10)
        except Exception:
            print '! Could not find the icon file "comix.svg"\n'
        label = gtk.Label()
        label.set_markup(
        '<big><big><big><big><b><span foreground="#333333">Com</span>' +
        '<span foreground="#79941b">ix</span> <span foreground="#333333">' +
        constants.VERSION +
        '</span></b></big></big></big></big>\n\n' +
        _('Comix is an image viewer specifically designed to handle comic books.') +
        '\n' +
        _('It reads ZIP, RAR and tar archives, as well as plain image files.') +
        '\n\n' +
        _('Comix is licensed under the GNU General Public License.') +
        '\n\n' +
        '<small>Copyright © 2005-2008 Pontus Ekberg\n\n' +
        'herrekberg@users.sourceforge.net\n' +
        'http://comix.sourceforge.net</small>\n')
        box.pack_start(label, True, True, 0)
        label.set_justify(gtk.JUSTIFY_CENTER)
        label.set_selectable(True)
        notebook.insert_page(box, gtk.Label(_('About')))

        # ----------------------------------------------------------------
        # Credits tab.
        # ----------------------------------------------------------------
        box = gtk.VBox(False, 5)
        box.set_border_width(5)
        for nice_person, description in (
            ('Pontus Ekberg', _('Developer')),
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
            ('김민기', _('Korean translation')),
            ('Maryam Sanaat', _('Persian translation')),
            ('Andhika Padmawan', _('Indonesian translation')),
            ('Jan Nekvasil', _('Czech translation')),
            ('Victor Castillejo', _('Icon design'))
            ):
            label = gtk.Label()
            label.set_markup('<b>%s:</b>   %s' % (nice_person, description))
            box.pack_start(label, False, False, 0)
            label.set_alignment(0, 0.5)
        notebook.insert_page(box, gtk.Label(_('Credits')))
        self.show_all()


def open_dialog(action, window):
    """Create and display the (singleton) about dialog."""
    global _dialog
    if _dialog is None:
        _dialog = _AboutDialog(window)
    else:
        _dialog.present()


def _close_dialog(*args):
    """Destroy the about dialog."""
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None
