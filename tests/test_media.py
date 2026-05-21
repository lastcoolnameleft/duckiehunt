import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.duck.media import handle_uploaded_file, save_uploaded_file, upload_to_flickr

class MediaTests(TestCase):

    def setUp(self):
        # Create a temporary directory for file uploads
        self.upload_path = os.path.join(settings.BASE_DIR, 'temp_uploads')
        os.makedirs(self.upload_path, exist_ok=True)
        settings.UPLOAD_PATH = self.upload_path

    def tearDown(self):
        # Remove the temporary directory and its contents
        for root, dirs, files in os.walk(self.upload_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.upload_path)

    def test_save_uploaded_file(self):
        # Create a simple uploaded file
        uploaded_file = SimpleUploadedFile("test_file.txt", b"file_content")

        # Save the uploaded file
        file_path = save_uploaded_file(uploaded_file, self.upload_path)

        # Check if the file was saved correctly
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            self.assertEqual(f.read(), b"file_content")

    def test_handle_uploaded_file(self):
        # Mock the upload_to_flickr function
        def mock_upload_to_flickr(photo_file, title, comments, is_public, tags):
            return {
                'id': '12345',
                'title': title,
                'description': comments,
                'tags': tags,
                'sizes': {'size': [{'label': 'Original', 'source': 'http://example.com/original.jpg'}]}
            }

        # Replace the real upload_to_flickr with the mock function
        original_upload_to_flickr = upload_to_flickr
        upload_to_flickr = mock_upload_to_flickr

        try:
            # Create a simple uploaded file
            uploaded_file = SimpleUploadedFile("test_file.txt", b"file_content")

            # Handle the uploaded file
            photo_info = handle_uploaded_file(uploaded_file, 1, "Duck Name", "Test comments")

            # Check if the photo info is correct
            self.assertEqual(photo_info['id'], '12345')
            self.assertEqual(photo_info['title'], 'Duck #1 (Duck Name)')
            self.assertEqual(photo_info['description'], 'Test comments')
            self.assertEqual(photo_info['tags'], 'duckiehunt')
            self.assertEqual(photo_info['sizes']['size'][0]['label'], 'Original')
            self.assertEqual(photo_info['sizes']['size'][0]['source'], 'http://example.com/original.jpg')
        finally:
            # Restore the original upload_to_flickr function
            upload_to_flickr = original_upload_to_flickr