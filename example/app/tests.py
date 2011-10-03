import os
import templfile
from string import printable
from django.test import TestCase
from django.test.client import Client

class UploadTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.raw_file_content = printable
        self.raw_file = templfile.NamedTemporaryFile(delete=False)
        self.image_file = open('data/favicon.ico')

        self.raw_file.write(self.raw_file_content)
        self.raw_file.close()
    
    def tearDown(self):
        os.remove(self.raw_file.path)

    def test_basic(self):
        response = self.client.get('/upload/')
        self.assertTemplateUsed(response, 'file_formpreview/form.html')

    def test_preview(self):
        data = {'raw_file': self.raw_file_content.read()
                'image_file': self.image_file.read()}

        response = self.client.post('/upload/')
        self.assertTemplateUsed(response, 'file_formpreview/preview.html')
        

