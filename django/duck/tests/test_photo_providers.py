"""Tests for the photo provider abstraction (issue #101)."""
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings

from duck.photo_providers import (
    PhotoProvider,
    FlickrProvider,
    get_photo_provider,
)


class FakeProvider(PhotoProvider):
    """Test provider that stores uploads in memory."""

    uploads = []

    def upload(self, image_file, title, description, tags=None):
        self.uploads.append({'title': title, 'description': description})
        return {'id': 'fake-123', 'thumbnail_url': 'http://fake.com/thumb.jpg'}

    def get_url(self, photo_id):
        return f'http://fake.com/{photo_id}'

    def delete(self, photo_id):
        pass


class GetPhotoProviderTest(TestCase):
    """Test provider resolution via settings."""

    def test_default_returns_flickr_provider(self):
        provider = get_photo_provider()
        self.assertIsInstance(provider, FlickrProvider)

    @override_settings(PHOTO_PROVIDER='duck.tests.test_photo_providers.FakeProvider')
    def test_custom_provider_via_dotted_path(self):
        provider = get_photo_provider()
        self.assertIsInstance(provider, FakeProvider)

    @override_settings(PHOTO_PROVIDER='flickr')
    def test_explicit_flickr_string(self):
        provider = get_photo_provider()
        self.assertIsInstance(provider, FlickrProvider)


class FlickrProviderUploadTest(TestCase):
    """Test FlickrProvider.upload with mocked flickr_api."""

    @patch('duck.photo_providers.flickr_api')
    def test_upload_returns_id_and_thumbnail(self, mock_flickr):
        mock_photo = MagicMock()
        mock_photo.getInfo.return_value = {'id': 12345}
        mock_photo.getSizes.return_value = {
            'Small 320': {'source': 'http://flickr.com/small.jpg'},
            'Medium': {'source': 'http://flickr.com/medium.jpg'},
        }
        mock_flickr.upload.return_value = mock_photo

        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile('duck.jpg', b'fake image data')

        provider = FlickrProvider()
        result = provider.upload(image, 'Test Duck', 'A comment', tags='test')

        self.assertEqual(result['id'], 12345)
        self.assertEqual(result['thumbnail_url'], 'http://flickr.com/small.jpg')
        mock_flickr.upload.assert_called_once()

    @patch('duck.photo_providers.flickr_api')
    def test_upload_failure_propagates(self, mock_flickr):
        mock_flickr.upload.side_effect = Exception('Flickr API down')

        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile('duck.jpg', b'fake image data')

        provider = FlickrProvider()
        with self.assertRaises(Exception) as ctx:
            provider.upload(image, 'Test', 'desc')
        self.assertIn('Flickr API down', str(ctx.exception))


class MarkerHandleUploadedFileTest(TestCase):
    """Test that marker.handle_uploaded_file uses the provider."""

    @override_settings(PHOTO_PROVIDER='duck.tests.test_photo_providers.FakeProvider')
    def test_uses_configured_provider(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from duck import marker

        image = SimpleUploadedFile('duck.jpg', b'fake image data')
        result = marker.handle_uploaded_file(image, 42, 'Quackers', 'Found it')

        self.assertEqual(result['id'], 'fake-123')
        self.assertEqual(result['sizes']['Small 320']['source'], 'http://fake.com/thumb.jpg')
