import os
import tempfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from string import printable
from unittest import TestCase

from django.test.client import Client

class UploadTest(TestCase):

    def setUp(self):
        self.client = Client()

        content = ''.join(printable)
        self.raw_fd = StringIO()
        self.raw_fd.write(content)
        
        img = open('app/tests/data/favicon.ico')
        self.img_fd = StringIO()
        self.img_fd.write(img.read())

    def tearDowm(self):
        os.remove(self.raw_fd.path)

    def test_upload(self):

        data = {'raw_file': self.raw_fd, 'image_file': self.img_fd}
        response = self.client.post('/upload/', data)

        self.assertTemplateUsed('file_formpreview/preview.html')
