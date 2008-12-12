"""Portability functions for Comix."""

import os
import sys

def get_home_directory():
    """On UNIX-like systems, this method will return the path of the home
    directory, e.g. /home/username. On Windows, it will return a Comix
    sub-directory of <Documents and Settings/Username>.
    """
    if sys.platform == 'win32':
        return os.path.join(os.path.expanduser('~'), 'Comix')
    else:
        return os.path.expanduser('~')

def get_comix_directory():
    """Comix' home directory. On UNIX, this would be /home/username/.comix,
    on Windows the same directory as get_home_directory(). 
 
    Reasoning behind this is that things are better kept together in one
    directory on Windows.
    """
    if sys.platform == 'win32':
        return get_home_directory()
    else:
        return os.path.join(os.path.expanduser('~'), '.comix')
