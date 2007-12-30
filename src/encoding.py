# ============================================================================
# encoding.py - Encoding handler for Comix.
# ============================================================================

import sys

def to_unicode(string):
    
    """ 
    Converts <string> to unicode. First tries the default filesystem
    encoding, and then falls back on some common encodings. If none
    of the convertions are successful "???" is returned. 
    """

    if isinstance(string, unicode):
        return string
    for encoding in (sys.getfilesystemencoding(), 'utf-8', 'latin-1'):
        try:
            ustring = unicode(string, encoding)
            return ustring
        except (UnicodeError, LookupError):
            pass
    return '???'

