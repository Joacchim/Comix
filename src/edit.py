"""edit.py - Archive editor."""

import gtk

_dialog = None


class _EditArchiveDialog(gtk.Dialog):

    def __init__(self):
        gtk.Dialog.__init__(self, _('Edit archive'), None, 0,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_OK))
        self.set_has_separator(False)
        #self.set_resizable(False)
        self.connect('response', self._response)
        self.set_default_response(gtk.RESPONSE_OK)
        
        self.show_all()

    def _response(self, dialog, response):
        if response == gtk.RESPONSE_OK:
            print 'ok'
        else:
            print 'close'


def open_dialog(*args):
    global _dialog
    if _dialog is None:
        _dialog = _EditArchiveDialog()
    else:
        _dialog.present()


def _close_dialog(*args):
    global _dialog
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None
