# ============================================================================
# encoding.py - Encoding handler.
# ============================================================================

import sys

def to_unicode(string):
    
    """ 
    Convert <string> to unicode. First trie the default filesystem
    encoding, and then fall back on some common encodings. If none
    of the convertions are successful, "???" is returned. 
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

