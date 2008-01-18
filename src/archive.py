# ============================================================================
# archive.py - Archive handling (extract/create) for Comix.
# ============================================================================

import sys
import os
import zipfile
import tarfile
import threading
import time

# ------------------------------------------------------------------------
# Determine if rar/unrar exists.
# ------------------------------------------------------------------------
_rar_exec = None
for path in os.getenv('PATH', '').split(':') + [os.path.curdir]:
    if os.path.isfile(os.path.join(path, 'unrar')):
        _rar_exec = os.path.join(path, 'unrar')
        break
    elif os.path.isfile(os.path.join(path, 'rar')):
        _rar_exec = os.path.join(path, 'rar')
        break
if _rar_exec == None:
    print '! Could not find the `rar` or `unrar` executables.'
    print '! RAR files (.cbr) will not be readable.\n'


class Extractor:
    
    def __init__(self):
        self._setupped = False
    
    def setup(self, src, dst):
        
        """
        Setup the extractor with archive <src> and destination dir <dst>.
        A threading condition related to the is_ready() method is returned.
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
            self._files = os.popen('%s vb "%s"' % (_rar_exec, src)).readlines()
            self._files = [name.rstrip('\n') for name in self._files]
        
        self._setupped = True
        return self._condition
    
    def get_files(self):
        
        """
        Get a list of names of all the files the extractor is currently
        set for extracting. After a call to setup() this is always all
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
        """

        self._files = files

    def is_ready(self, num):

        """
        Returns True if the file indexed by <num> in the extractors file
        list (as set by set_files()) is fully extracted.
        """

        return self._extracted.get(num, False)

    def get_mime_type(self):
        
        """ Returns the mime type name of the extractors archive. """

        return self._type

    def stop(self):
        
        """
        Tells the extractor to stop extracting and kill the extracting
        thread. Blocks until the extracting thread has exited.
        """

        self._stop = True
        if self._setupped:
            self._extract_thread.join()
            self.setupped = False

    def extract(self):
        
        """
        Starts extracting the files in the file list one by one using a
        new thread. Every time a new file is extracted a notify() will be
        signalled the condition returned by setup().
        """

        self._extract_thread = threading.Thread(target=self._thread_extract)
        self._extract_thread.setDaemon(False)
        self._extract_thread.start()

    def _thread_extract(self):
        for name in self._files:
            self._extract_file(name, self._dst)

    def _extract_file(self, name, dst):
        if self._stop:
            sys.exit(0)
        try:
            if self._type == 'zip':
                if (name.endswith('/') or 
                  self._zfile.getinfo(name).file_size <= 0):
                    return
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
                self._tfile.extract(name, dst)
            elif self._type == 'rar':
                if _rar_exec == None:
                    print '! archive.py: Could not find RAR file extractor.\n'
                    return
                os.popen('%s x -n"%s" -p- -o- -- "%s" "%s"' % (_rar_exec, name,
                    self._src, dst))
        except:
            # Better to ignore any failed extractions (e.g. from corrupt
            # archive) than to crash here and leave the main thread in a
            # possible infinite block. Missing/damaged files *should* be
            # handled gracefully by the main program anyway.
            pass
        
        self._condition.acquire()
        self._extracted[self._files.index(name)] = True
        self._condition.notify()
        self._condition.release()


def archive_mime_type(path):
    
    """ Returns the archive type of <path> or None for non-archives. """
    
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
    
    """ Returns a text representation of an archive type. """

    return {'zip':   _('ZIP archive'),
            'tar':   _('Tar archive'),
            'gzip':  _('Gzip compressed tar archive'),
            'bzip2': _('Bzip2 compressed tar archive'),
            'rar':   _('RAR archive')}[archive_type]

