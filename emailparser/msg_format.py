from .base import Email, Attachment
import email
import email.utils
from email.header import decode_header, make_header
from datetime import datetime
from base64 import urlsafe_b64decode
import logging
from binascii import unhexlify

log = logging.getLogger(__name__)


def part_decode(part):
    try:
        data = part.get_payload(decode=True)
    except Exception as e:
        # -- added for email : e12b13efd577c5d3f446ecfbffeef8cee8907425d163735c51f6fa90a7b33934
        data = part.get_payload(decode=False).split('\r\n')
        if not data[-1].endswith('AA'):
            del(data[-1])
        data = ''.join(data)
        data = urlsafe_b64decode(data)
    return data


class Msg(Email):

    def __init__(self, contents):
        super().__init__(contents)
        try:
            msg = email.message_from_string(contents.decode('utf-8', 'replace'))
        except Exception as e:
            log.exception('Unable to decode and parse msg contents')
        # parse
        self.sender = email.utils.parseaddr(msg['From'])[1]
        self.receiver = [addr[1].lower() for addr in email.utils.getaddresses(msg.get_all('to', []) + msg.get_all('cc', []))]
        self.subject = msg['Subject']
        self.timestamp = email.utils.parsedate(msg['Date'])
        if self.timestamp is not None:
            self.timestamp = datetime(
                year=self.timestamp[0],
                month=self.timestamp[1],
                day=self.timestamp[2],
                hour=self.timestamp[3],
                minute=self.timestamp[4],
                second=self.timestamp[5]
            )
        self.body = b''
        # body and attachments
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_maintype() == 'text':
                    self.body += part.get_payload(decode=True)
                else:
                    self.attachments.append(MsgAttachment(part))
        else:
            self.body += msg.get_payload(decode=True)
        # -- hack to make sure all attachments are accounted for and not snucked into epilogue
        if len(self.attachments) ==0 and msg.get_boundary() is not None:
            for part in msg.as_string().split('--' + msg.get_boundary()):
                if 'content-transfer-encoding' in part.lower() and 'base64' in part.lower():
                    attachment = email.message_from_string(part.strip())
                    if attachment.get_filename() is not None:
                        msg.attach(attachment)
        #-- end hack


class MsgAttachment(Attachment):

    def __init__(self, attachment_data):
        super().__init__(part_decode(attachment_data))
        self.name = self.sha256
        if attachment_data.get_filename():
            try:
                self.name = str(make_header(decode_header(attachment_data.get_filename())))
            except UnicodeEncodeError:
                log.exception('[UnicodeEncodeError] Parsing Attachment Name')
            else:
                self.file_name = self.name
