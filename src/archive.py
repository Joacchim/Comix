# ============================================================================
# archive.py - Archive handling (extract/create) for Comix.
# ============================================================================

import sys
import os
import zipfile
import tarfile

# ------------------------------------------------------------------------
# Determine if rar/unrar exists.
# ------------------------------------------------------------------------
_rar_exec = None
for path in os.getenv('PATH').split(':') + [os.path.curdir]:
    if os.path.isfile(os.path.join(path, 'unrar')):
        _rar_exec = os.path.join(path, 'unrar')
        break
    elif os.path.isfile(os.path.join(path, 'rar')):
        _rar_exec = os.path.join(path, 'rar')
        break
if _rar_exec == None:
    print '! Could not find the `rar` or `unrar` executables.'
    print '! RAR files (.cbr) will not be readable.\n'

def extract_archive(src_path, dst_path):
    
    """ Extracts <src_path> to <dst_path>. Returns the archive type. """
    
    archive_type = archive_mime_type(src_path)
    try:    
        # ----------------------------------------------------------------
        # Zip archive.
        # ----------------------------------------------------------------
        if archive_type == 'zip':
            zipf = zipfile.ZipFile(src_path)
            zipfiles = zipf.namelist()
            for i, f in enumerate(zipfiles):
                # Caught the directory descriptor. Skip it.
                if f.endswith('/'):
                    continue
                # Other source encodings? I *believe* this is the standard.
                dst = unicode(f, 'cp437')
                found_encoding = False
                for enc in (sys.getfilesystemencoding(), 'utf8', 'latin-1'):
                    try:
                        dst = dst.encode(enc)
                    except:
                        pass
                    else:
                        found_encoding = True
                        break
                if not found_encoding:
                    dst = '%05d_unknown_encoding' % i
                if zipf.getinfo(f).file_size > 0:
                    full_path = os.path.join(dst_path, dst)
                    if not os.path.exists(os.path.dirname(full_path)):
                        os.makedirs(os.path.dirname(full_path))
                    new = open(full_path, 'w')
                    new.write(zipf.read(f))
                    new.close()
            zipf.close()
        
        # ----------------------------------------------------------------
        # Tar archive.
        # ----------------------------------------------------------------
        elif archive_type in ['tar', 'gzip', 'bzip2']:
            tar = tarfile.open(src_path, 'r')
            tarfiles = tar.getmembers()
            for f in tarfiles:
                tar.extract(f, dst_path)
            tar.close()
        
        # ----------------------------------------------------------------
        # RAR archive.
        # ----------------------------------------------------------------
        elif archive_type == 'rar':
            if _rar_exec != None:
                os.popen('%s x "%s" "%s"' % (_rar_exec, src_path, dst_path))
            else:
                print '! archive.py: Could not find RAR file extractor.\n'
                # FIXME: Pop-up or statusbar should be better for user
                return None
    except:
        print '! archive.py: Error extracting', src_path, 'to', dst_path, '\n'
    return archive_type

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

    return {'zip':   _('Zip archive'),
            'tar':   _('Tar archive'),
            'gzip':  _('Gzip compressed tar archive'),
            'bzip2': _('Bzip2 compressed tar archive'),
            'rar':   _('RAR archive')}[archive_type]

