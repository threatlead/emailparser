from .outlook import OutLookMsg
from .msg_format import Msg
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())


def parse(file_path):
    with open(file_path, 'rb') as sample:
        data = sample.read()
        # -- Replace BOM
        if data.startswith(b'\xef\xbb\xbf'):
            data = data[3:]
        if OutLookMsg.is_outlook_msg(data):
            return OutLookMsg(data)
        else:
            return Msg(data)
