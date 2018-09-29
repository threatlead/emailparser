from .context import emailparser
import os
import unittest
import tempfile


class ConnectTestSuite(unittest.TestCase):

    def test_msg_with_attachment(self):
        folder = os.path.abspath('samples')
        msgfile = os.path.join(folder, 'msg_file_with_word_attachment.eml')
        email = emailparser.parse(msgfile)
        self.assertEqual(len(email.attachments), 1, 'Unable to extract attachments')
        self.assertEqual(email.attachments[0].name, 'invoice_4723253.doc', 'Attachment name doesnt matches')
        self.assertEqual(email.attachments[0].md5, 'ae863a25146f83142e0b6a27129c2c26', 'Attachment hash doesnt matches')

    def test_msg_with_zip_attachment(self):
        folder = os.path.abspath('samples')
        msgfile = os.path.join(folder, 'msg_file_with_zip_attachment.eml')
        email = emailparser.parse(msgfile)
        self.assertEqual(len(email.attachments), 1, 'Unable to extract attachments')
        self.assertEqual(email.attachments[0].name, 'wire_xls_46B.zip', 'Attachment name doesnt matches')
        self.assertEqual(email.attachments[0].md5, '59c1b8a8a6307bd0433d2fbd5f54d8f9', 'Attachment hash doesnt matches')
        # -- unzip check
        outdir = os.path.join(tempfile.gettempdir(), 'emailparser_test')
        known_file = os.path.join(outdir, 'urgent 94026.js')
        files_list = email.attachments[0].unpack(out_dir=outdir)
        self.assertIn(known_file, files_list, 'Missing file from unzipped attachment')
        for f in files_list:
            os.remove(f)
        os.rmdir(outdir)

    def test_msg(self):
        folder = os.path.abspath('samples')
        msgfile = os.path.join(folder, 'outlook_file.msg')
        email = emailparser.parse(msgfile)
        self.assertEqual(email.md5, '5818cdbf9114ea000c30805d83d1dfba', 'Wrong MSG file selected for testing')
        self.assertEqual(email.receiver, 'brinfo@eagle-crest.com', 'Msg file email address did not matched')
        self.assertEqual(len(email.attachments), 1, 'Unable to extract attachments')
        self.assertEqual(email.attachments[0].name, '010v29~1.dot', 'Attachment name doesnt match')

    def test_msg_with_bom(self):
        folder = os.path.abspath('samples')
        msgfile = os.path.join(folder, 'msg_file_with_bom.eml')
        email = emailparser.parse(msgfile)
        self.assertEqual(len(email.attachments), 2, 'Unable to extract attachments')
        self.assertEqual(email.attachments[0].name, 'logo (2).png', 'Attachment name doesnt matches')
        self.assertEqual(email.attachments[0].md5, '6cf84d6037cf4e5646da179cea6ecfdb', 'Attachment hash doesnt matches')


if __name__ == '__main__':
    unittest.main()
