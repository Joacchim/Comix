# ============================================================================
# process.py - Process spawning module.
#
# The subprocess and popen2 modules in Python are broken (see issue 1336).
# The problem (i.e. complete crash) they can cause happen fairly often (once
# is too often) in Comix when calling "rar" or "unrar" to extract specific
# files from archives. We roll our own very simple process spawning module
# here instead (and surely introduce a whole new array of exciting bugs!)
# ============================================================================

import os
import sys
import gc

class Process:
    
    def __init__(self, args):
        
        """
        Setup a Process where <args> is a sequence of arguments that defines
        the process. The first element of <args> shuld be the full path to 
        the executable file to be run.
        """

        self._args = args
        self._pid = None
    
    def spawn(self):
        
        """
        Spawn the process defined by the args in __init__. Return a file-like
        object linked to the spawned process' stdout.
        """

        gc.disable() # Avoid Python issue 1336!
        read_pipe, write_pipe = os.pipe()
        self._pid = os.fork()
        if self._pid == 0:
            try:
                os.close(read_pipe)
                os.dup2(write_pipe, 1)
                os.execv(self._args[0], self._args)
            except:
                sys.stderr.write('Could not execute %s\n' % str(self._args[0]))
                sys.exit(1)
        gc.enable()
        os.close(write_pipe)
        return os.fdopen(read_pipe)

    def wait(self):
        
        """ Wait for the process to terminate. """
        
        if self._pid:
            os.waitpid(self._pid, 0)
        else:
            raise Exception, 'Process not spawned'

