# ========================================================================
# ui.py - UI definitions for Comix.
# ========================================================================

import gtk

import main
import about
import properties
import filechooser

def bogus(*args):
    print 'Weeee...'

class MainUI(gtk.UIManager):

    def __init__(self):
        gtk.UIManager.__init__(self)

        # =======================================================
        # Create actions for the menus.
        # =======================================================
        actiongroup = gtk.ActionGroup('')
        actiongroup.add_actions([
            ('next', gtk.STOCK_GO_FORWARD, _('_Next page'), 'Page_Down',
                None, main.next_page),
            ('previous', gtk.STOCK_GO_BACK, _('_Previous page'), 'Page_Up',
                None, main.previous_page),
            ('first', gtk.STOCK_GOTO_FIRST, _('_First page'), 'Home',
                None, main.first_page),
            ('last',gtk.STOCK_GOTO_LAST, _('_Last page'), 'End',
                None, main.last_page),
            ('go', gtk.STOCK_JUMP_TO, _('_Go to page...'), 'g',
                None, bogus),
            ('zoom', 'comix-zoom', _('Manual _Zoom')),
            ('zin', gtk.STOCK_ZOOM_IN, _('_Zoom in'), 'KP_Add',
                None, main.manual_zoom_in),
            ('zout', gtk.STOCK_ZOOM_OUT, _('Zoom _out'), 'KP_Subtract',
                None, main.manual_zoom_out),
            ('zoriginal', gtk.STOCK_ZOOM_100, _('_Normal size'), 'n',
                None, main.manual_zoom_original),
            ('zwidth', gtk.STOCK_ZOOM_FIT, _('Fit _width'), '<Control>w',
                None, bogus),
            ('zheight', gtk.STOCK_ZOOM_FIT, _('Fit _height'), '<Control>h',
                None, bogus),
            ('zfit', gtk.STOCK_ZOOM_FIT, _('_Best fit'), 'b',
                None, bogus),
            ('add_bookmark', gtk.STOCK_ADD, _('_Add bookmark'), '<Control>d',
                None, bogus),
            ('clear_bookmarks', gtk.STOCK_CLEAR, _('Clear bookmarks'), '',
                None, bogus),
            ('bookmark_manager', 'comix-edit-bookmarks',
                _('_Edit bookmarks...'), '<Control>b', None,
                bogus),
            ('preferences', gtk.STOCK_PREFERENCES, _('Pr_eferences'), '',
                None, bogus),
            ('about', gtk.STOCK_ABOUT, _('_About'), '',
                None, about.dialog_open),
            ('thumbnail_dialog', 'comix-thumbnails',
                _('_Manage thumbnails...'),
                '', None, bogus),
            ('properties', gtk.STOCK_PROPERTIES, _('Proper_ties'), '<Alt>Return',
                None, properties.dialog_open),
            ('comments', gtk.STOCK_INFO, _('View _comments'), 'c',
                None, bogus),
            ('open', gtk.STOCK_OPEN, _('_Open...'), '<Control>o',
                None, filechooser.dialog_open),
            ('recent', 'comix-recent-files', _('_Recent files')),
            ('clear_recent', gtk.STOCK_CLEAR, _('Clear recent files'), '',
                None, bogus),
            ('library', 'comix-library', _('Open _library...'), '<Control>l',
                None, bogus),
            ('add_to_library', 'comix-library-add', _('_Add to library'), '',
                None, bogus),
            ('convert', gtk.STOCK_CONVERT, _('Con_vert...'), '',
                None, bogus),
            ('extract', gtk.STOCK_SAVE_AS, _('E_xtract image...'), '',
                None, bogus),
            ('close', gtk.STOCK_CLOSE, _('_Close'), '<Control>w',
                None, bogus),
            ('quit', gtk.STOCK_QUIT, _('_Quit'), '<Control>q',
                None, main.terminate_program),
            ('colour_adjust', 'comix-colour-adjust', _('_Adjust colour...'),
                'j', None, bogus),
            ('slideshow', 'comix-slideshow', _('Slideshow'), '<Control>S', 
                None, bogus),
            ('delete', gtk.STOCK_DELETE, _('Delete image...'), None,
                None, bogus),
            ('file_rot_90', 'comix-rotate-90-jpeg',
                _('CW lossless JPEG rotation...'), '<Alt>r',
                None, bogus),
            ('file_rot_270', 'comix-rotate-270-jpeg',
                _('CCW lossless JPEG rotation...'),
                '<Alt><Shift>r', None, bogus),
            ('file_flip_horiz', 'comix-flip-horizontal-jpeg',
                _('Horizontal lossless JPEG flip...'),
                None, None, bogus),
            ('file_flip_vert', 'comix-flip-vertical-jpeg',
                _('Vertical lossless JPEG flip...'),
                None, None, bogus),
            ('file_desaturate', 'comix-desaturate',
                _('Convert JPEG to greyscale...'),
                None, None, bogus),
            ('menu_bookmarks', None, _('_Bookmarks')),
            ('menu_toolbars', 'comix-toolbars', _('_Toolbars')),
            ('menu_bookmarks_popup', 'comix-bookmarks', _('_Bookmarks')),
            ('menu_edit', None, _('_Edit')),
            ('menu_file_operations', 'comix-file-operations',
                _('File o_perations')),
            ('menu_file', None, _('_File')),
            ('menu_view', None, _('_View')),
            ('menu_go', None, _('_Go')),
            ('menu_help', None, _('_Help')),
            ('transform', 'comix-transform', _('_Transform')),
            ('rotate_90', 'comix-rotate-90', _('_Rotate 90 degrees CW'), 'r',
                None, main.rotate90),
            ('rotate_180','comix-rotate-180', _('Rotate 180 de_grees'), None,
                None, main.rotate180),
            ('rotate_270', 'comix-rotate-270', _('Rotat_e 90 degrees CCW'),
                '<Shift>r', None, main.rotate270),
            ('flip_horiz', 'comix-flip-horizontal', _('Fli_p horizontally'),
                None, None, bogus),
            ('flip_vert', 'comix-flip-vertical', _('Flip _vertically'), None,
                None, bogus),
            ('expander', None, None, None, None, None)])

        actiongroup.add_toggle_actions([
            ('fullscreen', None, _('_Fullscreen'), 'f',
                None, main.change_fullscreen),
            ('double', 'comix-double-page', _('_Double page mode'), 'd',
                None, main.change_double_page),
            ('toolbar', None, _('_Toolbar'), None,
                None, main.change_toolbar_visibility),
            ('menubar', None, _('_Menubar'), None,
                None, main.change_menubar_visibility),
            ('statusbar', None, _('St_atusbar'), None,
                None, main.change_statusbar_visibility),
            ('scrollbar', None, _('S_crollbars'), None,
                None, main.change_scrollbar_visibility),
            ('thumbnails', None, _('Th_umbnails'), 'F9',
                None, main.change_thumbnails_visibility),
            ('hide all', None, _('H_ide all'), 'i',
                None, main.change_hide_all),
            ('manga_mode', 'comix-manga', _('_Manga mode'), 'm',
                None, main.change_manga_mode),
            ('keep_rotation', None, _('_Keep transformation'), 'k',
                None, main.change_keep_rotation),
            ('lens', 'comix-lens', _('Magnifying _lens'), 'z',
                None, bogus)])

        actiongroup.add_radio_actions([
            ('fit_manual_mode', 'comix-fitnone',
                _('Manual zoom mode'), 'a', None, 0),
            ('fit_screen_mode', 'comix-fitscreen',
                _('Fit-to-_screen mode'), 's', None, 1),
            ('fit_width_mode', 'comix-fitwidth',
                _('Fit _width mode'), 'w', None, 2),
            ('fit_height_mode', 'comix-fitheight',
                _('Fit _height mode'), 'h', None, 3)],
            0, main.change_zoom_mode)

        ui_description = """
        <ui>
            <toolbar name="Tool">
                <toolitem action="first" />
                <toolitem action="previous" />
                <toolitem action="next" />
                <toolitem action="last" />
                <separator />
                <toolitem action="go" />
                <toolitem action="expander" />
                <toolitem action="fit_screen_mode" />
                <toolitem action="fit_width_mode" />
                <toolitem action="fit_height_mode" />
                <toolitem action="fit_manual_mode" />
                <separator />
                <toolitem action="double" />
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
                        <menuitem action="file_rot_90" />
                        <menuitem action="file_rot_270" />
                        <menuitem action="file_flip_horiz" />
                        <menuitem action="file_flip_vert" />
                        <menuitem action="file_desaturate" />
                        <separator />
                        <menuitem action="delete" />
                    </menu>
                    <separator />
                    <menu action="recent">
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
                    <menuitem action="thumbnail_dialog" />
                    <menuitem action="preferences" />
                </menu>
                <menu action="menu_view">
                    <menuitem action="fullscreen" />
                    <menuitem action="double" />
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
                    <menu action="transform">
                        <menuitem action="rotate_90" />
                        <menuitem action="rotate_270" />
                        <menuitem action="rotate_180" />
                        <menuitem action="flip_horiz" />
                        <menuitem action="flip_vert" />
                        <separator />
                        <menuitem action="keep_rotation" />
                    </menu>
                    <menu action="zoom">
                        <menuitem action="zin" />
                        <menuitem action="zout" />
                        <menuitem action="zoriginal" />
                        <menuitem action="zwidth" />
                        <menuitem action="zheight" />
                        <menuitem action="zfit" />
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
                    <menuitem action="first" />
                    <menuitem action="previous" />
                    <menuitem action="next" />
                    <menuitem action="last" />
                    <separator />
                    <menuitem action="go" />
                </menu>
                <menu action="menu_bookmarks">
                    <menuitem action="add_bookmark" />
                    <menuitem action="bookmark_manager" />
                    <separator />
                    <separator />
                    <menuitem action="clear_bookmarks" />
                </menu>
                <menu action="menu_help">
                    <menuitem action="about" />
                </menu>
            </menubar>

            <popup name="Pop">
                <menuitem action="next" />
                <menuitem action="previous" />
                <separator />
                <menuitem action="fullscreen" />
                <menuitem action="double" />
                <menuitem action="manga_mode" />
                <separator />
                <menuitem action="fit_screen_mode" />
                <menuitem action="fit_width_mode" />
                <menuitem action="fit_height_mode" />
                <menuitem action="fit_manual_mode" />
                <separator />
                <menu action="transform">
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
        
        # FIXME: Is there no built-in way to do this?
        self.get_widget('/Tool/expander').set_expand(True)
        self.get_widget('/Tool/expander').set_sensitive(False)

