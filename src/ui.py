# ============================================================================
# ui.py - UI definitions for main window.
# 
# Logically this isn't really a separate module from main.py, but it is
# given it's own file for the sake of readability.
# ============================================================================

import gtk

import about
import bookmark
import comment
import enhance
import filechooser
import filehandler
import preferences
import properties
import recent

def bogus(*args):
    print 'Feature not implemented yet.'

class MainUI(gtk.UIManager):
    
    def __init__(self, window):
        gtk.UIManager.__init__(self)
        self._window = window

        # ----------------------------------------------------------------
        # Create actions for the menus.
        # ----------------------------------------------------------------
        self._actiongroup = gtk.ActionGroup('comix-main')
        self._actiongroup.add_actions([
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
                '<Control>0', None, window.manual_zoom_original), 
            ('about', gtk.STOCK_ABOUT, _('_About'),
                None, None, about.open_dialog),
            ('edit_thumbnails', 'comix-thumbnails', _('_Manage thumbnails...'),
                None, None, bogus),
            ('library', 'comix-library', _('_Library...'),
                '<Control>l', None, bogus),
            ('add_to_library', 'comix-library-add', _('_Add to library'),
                None, None, bogus),
            ('edit_archive', gtk.STOCK_EDIT, _('_Edit archive...'),
                None, None, bogus),
            ('close', gtk.STOCK_CLOSE, _('_Close'),
                '<Control>w', None, window.file_handler.close_file),
            ('quit', gtk.STOCK_QUIT, _('_Quit'),
                '<Control>q', None, window.terminate_program),
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
            ('menu_recent', None, _('Open _recent')),
            ('menu_bookmarks', None, _('_Bookmarks')),
            ('menu_toolbars', None, _('_Toolbars')),
            ('menu_edit', None, _('_Edit')),
            ('menu_file', None, _('_File')),
            ('menu_view', None, _('_View')),
            ('menu_go', None, _('_Go')),
            ('menu_help', None, _('_Help')),
            ('menu_transform', 'comix-transform', _('_Transform')),
            ('expander', None, None, None, None, None)])

        self._actiongroup.add_toggle_actions([
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
            ('slideshow', gtk.STOCK_MEDIA_PLAY, _('Run _slideshow'),
                '<Control>S', None, window.slideshow.toggle),
            ('lens', 'comix-lens', _('Magnifying _glass'),
                'g', None, window.glass.toggle)])

        self._actiongroup.add_radio_actions([
            ('fit_manual_mode', 'comix-fitmanual', _('M_anual zoom mode'),
                'a', None, 0),
            ('fit_screen_mode', 'comix-fitscreen', _('Fit-to-_screen mode'),
                's', None, 1),
            ('fit_width_mode', 'comix-fitwidth', _('Fit _width mode'),
                'w', None, 2),
            ('fit_height_mode', 'comix-fitheight', _('Fit _height mode'),
                'h', None, 3)],
            0, window.change_zoom_mode)
        
        # Some actions added separately since they need extra arguments.
        self._actiongroup.add_actions([
            ('properties', gtk.STOCK_PROPERTIES, _('Proper_ties'),
                '<Alt>Return', None, properties.open_dialog),
            ('enhance_image', 'comix-enhance-image', _('_Enhance image...'),
                'e', None, enhance.open_dialog),
            ('preferences', gtk.STOCK_PREFERENCES, _('Pr_eferences'),
                None, None, preferences.open_dialog)], window)

        self._actiongroup.add_actions([
            ('open', gtk.STOCK_OPEN, _('_Open...'),
                '<Control>o', None, filechooser.open_dialog),
            ('comments', 'comix-comments', _('View _comments'),
                'c', None, comment.open_dialog)], window.file_handler)

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
                    <menuitem action="edit_archive" />
                    <separator />
                    <menuitem action="properties" />
                    <menuitem action="comments" />
                    <separator />
                    <menu action="menu_recent">
                    </menu>
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
                    <menuitem action="enhance_image" />
                    <separator />
                    <menuitem action="lens" />
                    <separator />
                    <menu action="menu_transform">
                        <menuitem action="rotate_90" />
                        <menuitem action="rotate_270" />
                        <menuitem action="rotate_180" />
                        <separator />
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
                    <menuitem action="next_page" />
                    <menuitem action="previous_page" />
                    <menuitem action="first_page" />
                    <menuitem action="last_page" />
                    <separator />
                    <menuitem action="slideshow" />
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
                    <separator />
                    <menuitem action="flip_horiz" />
                    <menuitem action="flip_vert" />
                    <separator />
                    <menuitem action="keep_rotation" />
                </menu>
                <menu action="menu_toolbars">
                    <menuitem action="menubar" />
                    <menuitem action="toolbar" />
                    <menuitem action="statusbar" />
                    <menuitem action="scrollbar" />
                    <menuitem action="thumbnails" />
                    <separator />
                    <menuitem action="hide all" />
                </menu>
            </popup>
        </ui>
        """

        self.add_ui_from_string(ui_description)
        self.insert_action_group(self._actiongroup, 0)
        
        self.bookmarks = bookmark.BookmarksMenu(self, window)
        self.get_widget('/Menu/menu_bookmarks').set_submenu(self.bookmarks)
        self.get_widget('/Menu/menu_bookmarks').show()
        
        self.recent = recent.RecentFilesMenu(self, window)
        self.get_widget('/Menu/menu_file/menu_recent').set_submenu(self.recent)
        self.get_widget('/Menu/menu_file/menu_recent').show()
        
        window.add_accel_group(self.get_accel_group())

        # FIXME: Is there no built-in way to do this?
        self.get_widget('/Tool/expander').set_expand(True)
        self.get_widget('/Tool/expander').set_sensitive(False)

    def set_sensitivities(self):

        """ Sets the main UI's widget's sensitivities appropriately. """

        general = ('properties',
                   'edit_archive',
                   'close',
                   'slideshow',
                   'rotate_90',
                   'rotate_180',
                   'rotate_270',
                   'flip_horiz',
                   'flip_vert',
                   'next_page',
                   'previous_page',
                   'first_page',
                   'last_page')
        archive = ('add_to_library',)
        comment = ('comments',)
        general_sensitive = False
        archive_sensitive = False
        comment_sensitive = False

        if self._window.file_handler.file_loaded:
            general_sensitive = True
            if self._window.file_handler.archive_type:
                archive_sensitive = True
                if self._window.file_handler.get_number_of_comments():
                    comment_sensitive = True 
        for name in general:
            self._actiongroup.get_action(name).set_sensitive(general_sensitive)
        for name in archive:
            self._actiongroup.get_action(name).set_sensitive(archive_sensitive)
        for name in comment:
            self._actiongroup.get_action(name).set_sensitive(comment_sensitive)
        self.bookmarks.set_sensitive(general_sensitive)

