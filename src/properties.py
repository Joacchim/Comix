# ========================================================================
# properties.py - Properties dialog for Comix.
# ========================================================================

import gtk

import main
import filehandler

dialog = None

class Propertiesdialog(gtk.Dialog):

    def __init__(self, window):
        
        ''' Creates the properties dialog. '''
        
        gtk.Dialog.__init__(self, _("Properties"), window, 0,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        
        self.set_resizable(False)
        self.set_has_separator(False)
        self.notebook = gtk.Notebook()
        self.vbox.pack_start(self.notebook, False, False, 0)
        
        label = gtk.Label("h0h0")
        self.vbox.pack_start(label, False, False, 0)
        
        self.connect('response', dialog_close)
        self.connect('delete_event', dialog_close)
        self.vbox.show_all()

def dialog_open(*args):
    global dialog
    if dialog == None:
        dialog = Propertiesdialog(None)
        dialog.show()

def dialog_close(*args):
    global dialog
    if dialog != None:
        dialog.destroy()
        dialog = None 

