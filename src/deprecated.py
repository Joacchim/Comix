"""deprecated.py - Clean up deprecated Comix files."""

import os
import shutil

import gtk

import constants


class _CleanerDialog(gtk.MessageDialog):

    def __init__(self, window, paths):
        gtk.MessageDialog.__init__(self, window, 0, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _('There are deprecated files left on your computer.'))

        self._paths = paths
        self.connect('response', self._response)

        self.format_secondary_text(
            _('Some old files (that were used for storing preferences, the library, bookmarks etc. for older versions of Comix) were found on your computer. If you do not plan on using the older versions of Comix again, you should remove these files in order to save some disk space. Do you want these files to be removed for you now?'))
    
    def _response(self, dialog, response):
        if response == gtk.RESPONSE_YES:
            for path in self._paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception:
                    print '! Could not remove', path
        self.destroy()


def check_for_deprecated_files(window):
    """Check for a number of deprecated files created by older versions of
    Comix. If any are found, we ask the user through a dilaog if they
    should be removed.
    """
    deprecated = (
        os.path.join(constants.HOME_DIR, '.comixrc'),
        os.path.join(constants.COMIX_DIR, 'archive_thumbnails'),
        os.path.join(constants.COMIX_DIR, 'bookmarks'),
        os.path.join(constants.COMIX_DIR, 'bookmarks_data'),
        os.path.join(constants.COMIX_DIR, 'comixrc'),
        os.path.join(constants.COMIX_DIR, 'library'),
        os.path.join(constants.COMIX_DIR, 'menu_thumbnails'),
        os.path.join(constants.COMIX_DIR, 'preferences_data'),
        os.path.join(constants.COMIX_DIR, 'recent_files'),
        os.path.join(constants.COMIX_DIR, 'recent_files_data'))
    found = []
    for path in deprecated:
        if os.path.exists(path):
            found.append(path)
    if found:
        dialog = _CleanerDialog(window, found)
        dialog.show_all()
