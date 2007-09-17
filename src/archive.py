# ========================================================================
# archive.py - Archive handling for Comix.
# ========================================================================

import sys
import os
import zipfile
import tarfile

# =======================================================
# Determine if rar/unrar exists.
# =======================================================
rar_exec = None
for path in os.getenv('PATH').split(':') + [os.path.curdir]:
    if os.path.isfile(os.path.join(path, 'unrar')):
        rar_exec = os.path.join(path, 'unrar')
        break
    elif os.path.isfile(os.path.join(path, 'rar')):
        self.rar = os.path.join(path, 'rar')
        break
if not rar_exec:
    print 'Could not find the `rar` or `unrar` executables.'
    print 'RAR (.cbr) files will not be readable.'
    print

def extract_archive(src_path, dst_path):
    
    ''' Extracts <src_path> to <dst_path>. Returns the archive type. '''
    
    archive_type = archive_mime_type(src_path)
    try:    
        # =======================================================
        # Zip archive.
        # =======================================================
        if archive_type == 'zip':
            zipf = zipfile.ZipFile(src_path)
            zipfiles = zipf.namelist()
            for i, x in enumerate(zipfiles):
                # Caught the directory descriptor. Skip it.
                if x.endswith('/'):
                    continue
                # FIXME: Other possible encodings?
                dst = unicode(x, 'cp437')
                found_encoding = False
                for enc in (sys.getfilesystemencoding(),
                    sys.getdefaultencoding(), 'utf8', 'latin-1'):
                    try:
                        dst = dst.encode(enc)
                    except:
                        pass
                    else:
                        found_encoding = True
                        break
                if not found_encoding:
                    dst = str(i) + '_unknown_encoding'
                if zipf.getinfo(x).file_size > 0:
                    full_path = os.path.join(dst_path, dst)
                    if not os.path.exists(os.path.dirname(full_path)):
                        os.makedirs(os.path.dirname(full_path))
                    new = open(full_path, 'w')
                    new.write(zipf.read(x))
                    new.close()
            zipf.close()
        
        # =======================================================
        # Tar archive.
        # =======================================================
        elif archive_type in ['tar', 'gzip', 'bzip2']:
            tar = tarfile.open(src_path, 'r')
            tarfiles = tar.getmembers()
            for x in tarfiles:
                tar.extract(x, dst_path)
            tar.close()
        
        # =======================================================
        # RAR archive.
        # =======================================================
        elif archive_type == 'rar':
            global rar_exec
            if rar_exec:
                os.popen(rar_exec + ' x "' + src_path + '" "' + dst_path + '"')
            else:
                print 'archive.py: Could not find RAR file extractor'
                return None
    except:
        print 'archive.py: Error extracting', src_path, 'to', dst_path
    return archive_type

def archive_mime_type(path):
    
    ''' Returns the archive type of <path> or None for non-archives. '''
    
    try:
        if os.path.isfile(path):
            if zipfile.is_zipfile(path):
                return 'zip'
            fd = open(path, 'rb')
            magic = fd.read(4)
            fd.close()
            if tarfile.is_tarfile(path) and os.path.getsize(path) > 0:
                if magic[:3] == 'BZh':
                    return 'bzip2'
                if magic[:2] == '\037\213':
                    return 'gzip'
                return 'tar'
            if magic == 'Rar!':
                return 'rar'
    except:
        print 'archive.py: Error while reading', path
    return None

