# ============================================================================
# ui.py - UI definitions for Comix.
# ============================================================================

import gtk

import about
import bookmark
import filechooser
import filehandler
import properties

def bogus(*args):
    print 'Weeee...'

class MainUI(gtk.UIManager):

    def __init__(self, window):
        gtk.UIManager.__init__(self)
        self._window = window

        # ----------------------------------------------------------------
        # Create actions for the menus.
        # ----------------------------------------------------------------
        actiongroup = gtk.ActionGroup('comix-main')
        actiongroup.add_actions([
            ('next_page', gtk.STOCK_GO_FORWARD, _('_Next page'),
                'Page_Down', None, window.next_page),
            ('previous_page', gtk.STOCK_GO_BACK, _('_Previous page'),
                'Page_Up', None, window.previous_page),
            ('first_page', gtk.STOCK_GOTO_FIRST, _('_First page'),
                'Home', None, window.first_page),
            ('last_page',gtk.STOCK_GOTO_LAST, _('_Last page'),
                'End', None, window.last_page),
            ('zoom_in', gtk.STOCK_ZOOM_IN, _('_Zoom in'),
                'KP_Add', None, window.manual_zoom_in),
            ('zoom_out', gtk.STOCK_ZOOM_OUT, _('Zoom _out'),
                'KP_Subtract', None, window.manual_zoom_out),
            ('zoom_original', gtk.STOCK_ZOOM_100, _('_Normal size'),
                'n', None, window.manual_zoom_original),
            ('preferences', gtk.STOCK_PREFERENCES, _('Pr_eferences'),
                None, None, bogus),
            ('about', gtk.STOCK_ABOUT, _('_About'),
                None, None, about.dialog_open),
            ('edit_thumbnails', 'comix-thumbnails', _('_Manage thumbnails...'),
                None, None, bogus),
            ('comments', gtk.STOCK_INFO, _('View _comments'),
                'c', None, bogus),
            ('clear_recent', gtk.STOCK_CLEAR, _('Clear recent files'),
                None, None, bogus),
            ('library', 'comix-library', _('Open _library...'),
                '<Control>l', None, bogus),
            ('add_to_library', 'comix-library-add', _('_Add to library'),
                None, None, bogus),
            ('convert', gtk.STOCK_CONVERT, _('Con_vert...'),
                None, None, bogus),
            ('extract', gtk.STOCK_SAVE_AS, _('E_xtract image...'),
                None, None, bogus),
            ('close', gtk.STOCK_CLOSE, _('_Close'),
                '<Control>w', None, window.file_handler.close_file),
            ('quit', gtk.STOCK_QUIT, _('_Quit'),
                '<Control>q', None, window.terminate_program),
            ('colour_adjust', 'comix-colour-adjust', _('_Adjust colour...'),
                'j', None, bogus),
            ('slideshow', 'comix-slideshow', _('Slideshow'),
                '<Control>S', None, bogus),
            ('delete', gtk.STOCK_DELETE, _('Delete image...'),
                None, None, bogus),
            ('rotate_90_jpeg', 'comix-rotate-90-jpeg',
                _('CW lossless JPEG rotation...'), '<Alt>r', None, bogus),
            ('rotate_270_jpeg', 'comix-rotate-270-jpeg',
                _('CCW lossless JPEG rotation...'), '<Alt><Shift>r', None,
                bogus),
            ('flip_horiz_jpeg', 'comix-flip-horizontal-jpeg',
                _('Horizontal lossless JPEG flip...'), None, None, bogus),
            ('flip_vert_jpeg', 'comix-flip-vertical-jpeg',
                _('Vertical lossless JPEG flip...'), None, None, bogus),
            ('desaturate_jpeg', 'comix-desaturate',
                _('Convert JPEG to greyscale...'), None, None, bogus),
            ('rotate_90', 'comix-rotate-90', _('_Rotate 90 degrees CW'),
                'r', None, window.rotate_90),
            ('rotate_180','comix-rotate-180', _('Rotate 180 de_grees'),
                None, None, window.rotate_180),
            ('rotate_270', 'comix-rotate-270', _('Rotat_e 90 degrees CCW'),
                '<Shift>r', None, window.rotate_270),
            ('flip_horiz', 'comix-flip-horizontal', _('Fli_p horizontally'),
                None, None, window.flip_horizontally),
            ('flip_vert', 'comix-flip-vertical', _('Flip _vertically'),
                None, None, window.flip_vertically),
            ('menu_zoom', 'comix-zoom', _('Manual _Zoom')),
            ('menu_recent', 'comix-recent-files', _('_Recent files')),
            ('menu_bookmarks', None, _('_Bookmarks')),
            ('menu_toolbars', 'comix-toolbars', _('_Toolbars')),
            ('menu_edit', None, _('_Edit')),
            ('menu_file_operations', 'comix-file-operations',
                _('File o_perations')),
            ('menu_file', None, _('_File')),
            ('menu_view', None, _('_View')),
            ('menu_go', None, _('_Go')),
            ('menu_help', None, _('_Help')),
            ('menu_transform', 'comix-transform', _('_Transform')),
            ('expander', None, None, None, None, None)])

        actiongroup.add_toggle_actions([
            ('fullscreen', None, _('_Fullscreen'),
                'f', None, window.change_fullscreen),
            ('double_page', 'comix-double-page', _('_Double page mode'),
                'd', None, window.change_double_page),
            ('toolbar', None, _('_Toolbar'),
                None, None, window.change_toolbar_visibility),
            ('menubar', None, _('_Menubar'),
                None, None, window.change_menubar_visibility),
            ('statusbar', None, _('St_atusbar'),
                None, None, window.change_statusbar_visibility),
            ('scrollbar', None, _('S_crollbars'),
                None, None, window.change_scrollbar_visibility),
            ('thumbnails', None, _('Th_umbnails'),
                'F9', None, window.change_thumbnails_visibility),
            ('hide all', None, _('H_ide all'),
                'i', None, window.change_hide_all),
            ('manga_mode', 'comix-manga', _('_Manga mode'),
                'm', None, window.change_manga_mode),
            ('keep_rotation', None, _('_Keep transformation'),
                'k', None, window.change_keep_rotation),
            ('lens', 'comix-lens', _('Magnifying _lens'),
                'z', None, bogus)])

        actiongroup.add_radio_actions([
            ('fit_manual_mode', 'comix-fitnone', _('Manual zoom mode'),
                'a', None, 0),
            ('fit_screen_mode', 'comix-fitscreen', _('Fit-to-_screen mode'),
                's', None, 1),
            ('fit_width_mode', 'comix-fitwidth', _('Fit _width mode'),
                'w', None, 2),
            ('fit_height_mode', 'comix-fitheight', _('Fit _height mode'),
                'h', None, 3)],
            0, window.change_zoom_mode)
        
        # Some actions added separately since they need the main window as
        # a parameter.
        actiongroup.add_actions([
            ('open', gtk.STOCK_OPEN, _('_Open...'),
                '<Control>o', None, filechooser.dialog_open),
            ('properties', gtk.STOCK_PROPERTIES, _('Proper_ties'),
                '<Alt>Return', None, properties.dialog_open)], window)

        ui_description = """
        <ui>
            <toolbar name="Tool">
                <toolitem action="first_page" />
                <toolitem action="previous_page" />
                <toolitem action="next_page" />
                <toolitem action="last_page" />
                <toolitem action="expander" />
                <toolitem action="fit_screen_mode" />
                <toolitem action="fit_width_mode" />
                <toolitem action="fit_height_mode" />
                <toolitem action="fit_manual_mode" />
                <separator />
                <toolitem action="double_page" />
                <toolitem action="manga_mode" />
                <separator />
                <toolitem action="lens" />
            </toolbar>

            <menubar name="Menu">
                <menu action="menu_file">
                    <menuitem action="open" />
                    <menuitem action="library" />
                    <separator />
                    <menuitem action="add_to_library" />
                    <menuitem action="convert" />
                    <menuitem action="extract" />
                    <menu action="menu_file_operations">
                        <menuitem action="rotate_90_jpeg" />
                        <menuitem action="rotate_270_jpeg" />
                        <menuitem action="flip_horiz_jpeg" />
                        <menuitem action="flip_vert_jpeg" />
                        <menuitem action="desaturate_jpeg" />
                        <separator />
                        <menuitem action="delete" />
                    </menu>
                    <separator />
                    <menu action="menu_recent">
                        <separator />
                        <menuitem action="clear_recent" />
                    </menu>
                    <separator />
                    <menuitem action="properties" />
                    <menuitem action="comments" />
                    <separator />
                    <menuitem action="close" />
                    <menuitem action="quit" />
                </menu>
                <menu action="menu_edit">
                    <menuitem action="edit_thumbnails" />
                    <menuitem action="preferences" />
                </menu>
                <menu action="menu_view">
                    <menuitem action="fullscreen" />
                    <menuitem action="double_page" />
                    <menuitem action="manga_mode" />
                    <separator />
                    <menuitem action="fit_screen_mode" />
                    <menuitem action="fit_width_mode" />
                    <menuitem action="fit_height_mode" />
                    <menuitem action="fit_manual_mode" />
                    <separator />
                    <menuitem action="slideshow" />
                    <separator />
                    <menuitem action="colour_adjust" />
                    <separator />
                    <menuitem action="lens" />
                    <separator />
                    <menu action="menu_transform">
                        <menuitem action="rotate_90" />
                        <menuitem action="rotate_270" />
                        <menuitem action="rotate_180" />
                        <menuitem action="flip_horiz" />
                        <menuitem action="flip_vert" />
                        <separator />
                        <menuitem action="keep_rotation" />
                    </menu>
                    <menu action="menu_zoom">
                        <menuitem action="zoom_in" />
                        <menuitem action="zoom_out" />
                        <menuitem action="zoom_original" />
                    </menu>
                    <separator />
                    <menu action="menu_toolbars">
                        <menuitem action="menubar" />
                        <menuitem action="toolbar" />
                        <menuitem action="statusbar" />
                        <menuitem action="scrollbar" />
                        <menuitem action="thumbnails" />
                        <separator />
                        <menuitem action="hide all" />
                    </menu>
                </menu>
                <menu action="menu_go">
                    <menuitem action="first_page" />
                    <menuitem action="previous_page" />
                    <menuitem action="next_page" />
                    <menuitem action="last_page" />
                </menu>
                <menu action="menu_bookmarks">
                </menu>
                <menu action="menu_help">
                    <menuitem action="about" />
                </menu>
            </menubar>

            <popup name="Popup">
                <menuitem action="next_page" />
                <menuitem action="previous_page" />
                <separator />
                <menuitem action="fullscreen" />
                <menuitem action="double_page" />
                <menuitem action="manga_mode" />
                <separator />
                <menuitem action="fit_screen_mode" />
                <menuitem action="fit_width_mode" />
                <menuitem action="fit_height_mode" />
                <menuitem action="fit_manual_mode" />
                <separator />
                <menu action="menu_transform">
                    <menuitem action="rotate_90" />
                    <menuitem action="rotate_270" />
                    <menuitem action="rotate_180" />
                    <menuitem action="flip_horiz" />
                    <menuitem action="flip_vert" />
                    <separator />
                    <menuitem action="keep_rotation" />
                </menu>
                <separator />
                <menuitem action="properties" />
                <separator />
                <menuitem action="open" />
            </popup>
        </ui>
        """

        self.add_ui_from_string(ui_description)
        self.insert_action_group(actiongroup, 0)
        
        self.bookmarks = bookmark.BookmarksMenu(self, window)
        self.get_widget('/Menu/menu_bookmarks').set_submenu(self.bookmarks)
        self.get_widget('/Menu/menu_bookmarks').show()
        
        window.add_accel_group(self.get_accel_group())

        # FIXME: Is there no built-in way to do this?
        self.get_widget('/Tool/expander').set_expand(True)
        self.get_widget('/Tool/expander').set_sensitive(False)

    def set_sensitivities(self):
        general = ('/Menu/menu_file/properties',
                   '/Menu/menu_file/close',
                   '/Menu/menu_file/menu_file_operations/rotate_90_jpeg',
                   '/Menu/menu_file/menu_file_operations/rotate_270_jpeg',
                   '/Menu/menu_file/menu_file_operations/flip_horiz_jpeg',
                   '/Menu/menu_file/menu_file_operations/flip_vert_jpeg',
                   '/Menu/menu_file/menu_file_operations/desaturate_jpeg',
                   '/Menu/menu_file/menu_file_operations/delete',
                   '/Menu/menu_view/slideshow',
                   '/Menu/menu_view/menu_transform/rotate_90',
                   '/Menu/menu_view/menu_transform/rotate_180',
                   '/Menu/menu_view/menu_transform/rotate_270',
                   '/Menu/menu_view/menu_transform/flip_horiz',
                   '/Menu/menu_view/menu_transform/flip_vert',
                   '/Menu/menu_go/next_page',
                   '/Menu/menu_go/previous_page',
                   '/Menu/menu_go/first_page',
                   '/Menu/menu_go/last_page',
                   '/Tool/next_page',
                   '/Tool/previous_page',
                   '/Tool/first_page',
                   '/Tool/last_page',
                   '/Popup/next_page',
                   '/Popup/previous_page',
                   '/Popup/properties')
        archive = ('/Menu/menu_file/add_to_library',
                   '/Menu/menu_file/convert',
                   '/Menu/menu_file/extract',
                   '/Menu/menu_file/comments')

        if self._window.file_handler.file_loaded:
            for path in general:
                self.get_widget(path).set_sensitive(True)
            if self._window.file_handler.archive_type:
                for path in archive:
                    self.get_widget(path).set_sensitive(True)
        else:
            for path in general + archive:
                self.get_widget(path).set_sensitive(False)

