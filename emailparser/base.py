import hashlib
import patoolib
import tempfile
import os
import magic
import mimetypes
import logging
from zipfile import ZipFile

log = logging.getLogger(__name__)


class Email:
    def __init__(self, contents):
        self.md5 = hashlib.md5(contents).hexdigest()
        self.sha256 = hashlib.sha256(contents).hexdigest()
        self.sha1 = hashlib.sha1(contents).hexdigest()
        self.size = len(contents)
        self.type = magic.from_buffer(contents)
        self.mime = magic.from_buffer(contents, mime=True)
        self.subject = None
        self.sender = None
        self.receiver = None
        self.body = None
        self.timestamp = None
        self.attachments = []


class Attachment:
    def __init__(self, contents):
        self.md5 = hashlib.md5(contents).hexdigest()
        self.sha256 = hashlib.sha256(contents).hexdigest()
        self.sha1 = hashlib.sha1(contents).hexdigest()
        self.size = len(contents)
        self.type = magic.from_buffer(contents)
        self.mime = magic.from_buffer(contents, mime=True)
        self.extension = mimetypes.guess_extension(self.mime, strict=True)
        self.content = contents
        self.name = None
        self.file_name = None

    @staticmethod
    def zip_encrypted(filepath):
        try:
            zf = ZipFile(filepath)
            zf.testzip()
        except RuntimeError as e:
            if 'encrypted' in str(e):
                return True
            else:
                return False
        else:
            return False

    def unpack(self, out_dir):
        with tempfile.NamedTemporaryFile(suffix=self.file_name, delete=False) as temp:
            log.debug('Unpacking Attachment: {0}'.format(temp.name))
            temp.write(self.content)
            temp.flush()
            # -- check for encrypted zip files
            if '.zip' in temp.name and self.zip_encrypted(temp.name):
                log.warning('Attached zip file is encrypted: {0}'.format(temp.name))
                raise
            try:
                patoolib.extract_archive(temp.name, outdir=out_dir, verbosity=-1, interactive=False)
            except Exception as e:
                log.warning('Unable to unzip attachment: {0}'.format(e))
                raise
            else:
                out_files = []
                for dp, dn, fn in os.walk(out_dir):
                    for f in fn:
                        out_files.append(os.path.join(dp, f))
                log.debug('Successfully unpacked attachment: {0}'.format(temp.name))
                return out_files
