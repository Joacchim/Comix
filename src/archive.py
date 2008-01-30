# ============================================================================
# archive.py - Archive handling (extract/create) for Comix.
# ============================================================================

import sys
import os
import subprocess
import zipfile
import tarfile
import threading

import time

# ------------------------------------------------------------------------
# Determine if rar/unrar exists, and bind the executable path to _rar_exec
# ------------------------------------------------------------------------
_rar_exec = None
for path in os.getenv('PATH', '').split(':') + [os.path.curdir]:
    if os.path.isfile(os.path.join(path, 'unrar')):
        _rar_exec = os.path.join(path, 'unrar')
        break
    elif os.path.isfile(os.path.join(path, 'rar')):
        _rar_exec = os.path.join(path, 'rar')
        break
if not _rar_exec:
    print '! Could not find the `rar` or `unrar` executables.'
    print '! RAR files (.cbr) will not be readable.\n'


class Extractor:
    
    """
    Extractor is a threaded class for extracting different archive formats.

    The Extractor can be loaded with paths to archives (currently ZIP, tar,
    or RAR archives) and a path to a destination directory. Once an archive
    has been set it is possible to filter out the files to be extracted and
    set the order in which they should be extracted. The extraction can
    then be started in a new thread in which files are extracted one by one,
    and a signal is sent on a condition after each extraction, so that it is
    possible for other threads to wait on specific files to be ready.

    Note: Support for gzip/bzip2 compressed tar archives is limited, see
    set_files() for more info.
    """
    
    def __init__(self):
        self._setupped = False
    
    def setup(self, src, dst):
        
        """
        Setup the extractor with archive <src> and destination dir <dst>.
        Return a threading Condition related to the is_ready() method.
        """

        self._src = src
        self._dst = dst
        self._type = archive_mime_type(src)
        self._files = []
        self._extracted = {}
        self._stop = False
        self._extract_thread = None
        self._condition = threading.Condition()
        
        if self._type == 'zip':
            self._zfile = zipfile.ZipFile(src, 'r')
            self._files = self._zfile.namelist()
        elif self._type in ['tar', 'gzip', 'bzip2']:
            self._tfile = tarfile.open(src, 'r')
            self._files = self._tfile.getnames()
        elif self._type == 'rar':
            if not _rar_exec:
                # FIXME: Set statusbar or popup dialog.
                pass
            proc = subprocess.Popen([_rar_exec, 'vb', src],
                stdout=subprocess.PIPE)
            self._files = proc.stdout.readlines()
            self._files = [name.rstrip('\n') for name in self._files]
        
        self._setupped = True
        return self._condition
    
    def get_files(self):
        
        """
        Return a list of names of all the files the extractor is currently
        set for extracting. After a call to setup() this is by default all
        files found in the archive. The paths in the list are relative to
        the archive root and are not absolute for the files once extracted.
        """

        return self._files[:]

    def set_files(self, files):
        
        """
        Set the files that the extractor should extract from the archive in
        the order of extraction. Normally one would get the list of all files
        in the archive using get_files(), then filter and/or permute this
        list before sending it back using set_files().
        
        Note: Random access on gzip or bzip2 compressed tar archives is
        no good idea. These formats are supported *only* for backwards
        compability. They are fine formats for some purposes, but should
        not be used for scanned comic books. So, we cheat and ignore the
        ordering applied with this method on such archives.
        """

        if self._type == 'gzip' or self._type == 'bzip2':
            self._files = filter(files.count, self._files)
        else:
            self._files = files

    def is_ready(self, name):

        """
        Return True if the file <name> in the extractors file list
        (as set by set_files()) is fully extracted.
        """
        
        return self._extracted.get(name, False)

    def get_mime_type(self):
        
        """ Return the mime type name of the extractor's current archive. """

        return self._type

    def stop(self):
        
        """
        Signal the extractor to stop extracting and kill the extracting
        thread. Blocks until the extracting thread has terminated.
        """

        self._stop = True
        if self._setupped:
            self._extract_thread.join()
            self.setupped = False

    def extract(self):
        
        """
        Start extracting the files in the file list one by one using a
        new thread. Every time a new file is extracted a notify() will be
        signalled the Condition that was returned by setup().
        """

        self._extract_thread = threading.Thread(target=self._thread_extract)
        self._extract_thread.setDaemon(False)
        self._extract_thread.start()

    def _thread_extract(self):
        
        """ Extract the files in the file list one by one. """
        

        for name in self._files:
            self._extract_file(name, self._dst)

    def _extract_file(self, name, dst):
        
        """
        Extract the file named <name> to directory <dst>, mark the file
        as "ready", then signal a notify() on the Condition returned by
        setup().
        """
        
        if self._stop:
            sys.exit(0)
        try:
            if self._type == 'zip':
                dst_name = unicode(name, 'cp437')
                for enc in (sys.getfilesystemencoding(), 'utf8', 'latin-1'):
                    try:
                        dst_name = dst_name.encode(enc)
                        break
                    except UnicodeError:
                        continue
                dst_path = os.path.join(dst, dst_name)
                if not os.path.exists(os.path.dirname(dst_path)):
                    os.makedirs(os.path.dirname(dst_path))
                new = open(dst_path, 'w')
                new.write(self._zfile.read(name))
                new.close()
            elif self._type in ['tar', 'gzip', 'bzip2']:
                if os.path.normpath(os.path.join(dst, name)).startswith(dst):
                    self._tfile.extract(name, dst)
                else:
                    print '! archive.py: Non-local tar member:', name, '\n'
            elif self._type == 'rar':
                if _rar_exec:
                    subprocess.call([_rar_exec, 'x', '-n' + name, '-p-', '-o-',
                        '-inul', '--', self._src, dst])
                else:
                    print '! archive.py: Could not find RAR file extractor.\n'
        except:
            # Better to ignore any failed extractions (e.g. from corrupt
            # archive) than to crash here and leave the main thread in a
            # possible infinite block. Damaged files *should* be
            # handled gracefully by the main program anyway.
            pass
        
        self._condition.acquire()
        self._extracted[name] = True
        self._condition.notify()
        self._condition.release()


def archive_mime_type(path):
    
    """ Return the archive type of <path> or None for non-archives. """
    
    try:
        if os.path.isfile(path):
            if zipfile.is_zipfile(path):
                return 'zip'
            fd = open(path, 'rb')
            magic = fd.read(4)
            fd.close()
            if tarfile.is_tarfile(path) and os.path.getsize(path) > 0:
                if magic.startswith('BZh'):
                    return 'bzip2'
                if magic.startswith('\037\213'):
                    return 'gzip'
                return 'tar'
            if magic == 'Rar!':
                return 'rar'
    except:
        print '! archive.py: Error while reading', path, '\n'
    return None

def get_name(archive_type):
    
    """ Return a text representation of an archive type. """

    return {'zip':   _('ZIP archive'),
            'tar':   _('Tar archive'),
            'gzip':  _('Gzip compressed tar archive'),
            'bzip2': _('Bzip2 compressed tar archive'),
            'rar':   _('RAR archive')}[archive_type]

