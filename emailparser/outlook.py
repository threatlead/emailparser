"""
Based on data from : http://www.fileformat.info/format/outlookmsg/
"""
import json
import olefile
from .base import Email, Attachment
from email.parser import Parser as EmailParser
import email.utils


class OutLookMsg(Email):

    def __init__(self, contents):
        super().__init__(contents)
        ole_msg = olefile.OleFileIO(contents)
        # msg_dir contains each msg stream
        tagger = json.load(open("emailparser/id.json", "r"))
        out = {'attachments': {}, 'body': u"", }
        streams = OutLookMsg._streams(ole_msg)
        for stream in streams:
            if '__attach_' in stream and '__substg1' in stream:
                attachment_number = str(int(stream.split('#')[1].split('/')[0]))
                lookup_code = OutLookMsg._lookup_code(stream, tagger)
                if attachment_number not in out['attachments']:
                    out['attachments'][attachment_number] = {}
                if 'Binary' in lookup_code:
                    out['attachments'][attachment_number][lookup_code] = ole_msg.openstream(stream).read()
                else:
                    out['attachments'][attachment_number][lookup_code] = OutLookMsg._convert(ole_msg.openstream(stream).read())
            elif '__substg1' in stream:
                lookup_code = OutLookMsg._lookup_code(stream, tagger)
                if ole_msg.openstream(stream):
                    content = OutLookMsg._convert(ole_msg.openstream(stream).read())
                    if content:
                        if lookup_code == 'unknown':
                            out['body'] += content
                        else:
                            if lookup_code not in out:
                                out[lookup_code] = ''
                            out[lookup_code] += content
            else:
                continue
        # map to email object
        if 'PidTagHtml' in out:
            self.body = out['PidTagHtml']
        elif 'PidTagBody' in out:
            self.body = out['PidTagBody']
        if 'PidTagSubject' in out:
            self.subject = out['PidTagSubject']
        # extract data from headers
        if 'PidTagTransportMessageHeaders' in out:
            headers = EmailParser().parsestr(out['PidTagTransportMessageHeaders'])
            # date/timestamp
            if 'date' in headers:
                self.timestamp = email.utils.parsedate(headers['date'])
            # sender
            if 'from' in headers and headers['from'] is not None:
                self.sender = email.utils.parseaddr(headers['from'])[1]
            # receiver
            if 'to' in headers and headers['to'] is not None:
                self.receiver = email.utils.parseaddr(headers['to'])[1]
        # backup if headers are missing
        if not self.sender and 'PidTagSenderEmailAddress' in out:
            self.sender = email.utils.parseaddr(out['PidTagSenderEmailAddress'])[1]
        if not self.receiver and "PidTagDisplayTo" in out:
            self.receiver = email.utils.parseaddr(out["PidTagDisplayTo"])[1]
        # attachments
        for k, a in out['attachments'].items():
            self.attachments.append(OutlookAttachment(a))


    @classmethod
    def _streams(cls, ole_msg):
        streams = []
        for entry in ole_msg.listdir():
            streams.append('/'.join(entry))
        return streams

    @classmethod
    def _lookup_code(cls, stream_name, tagger):
        lookup_code = stream_name.split('__substg')[1].split('_')[1]
        if lookup_code in tagger:
            return tagger[lookup_code]
        else:
            return 'unknown'

    @classmethod
    def is_outlook_msg(cls, data):
        if b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1' in data[:10]:
            return True
        else:
            return False

    @classmethod
    def _convert(cls, string):
        if string:
            try:
                return string.decode('utf-8').replace("\x00", "")
            except:
                return None
        else:
            return None


class OutlookAttachment(Attachment):

    def __init__(self, attachment_data):
        if 'PidTagAttachDataBinary' not in attachment_data:
            return None
        super().__init__(attachment_data.get('PidTagAttachDataBinary'))
        self.name = attachment_data.get('PidTagAttachFilename', None)
        self.file_name = attachment_data.get('PidTagAttachLongFilename', None)
        self.mime = attachment_data.get('PidTagAttachMimeTag', None)
        self.extension = attachment_data.get('PidTagAttachExtension', None)
        self.content = attachment_data.get('PidTagAttachDataBinary')