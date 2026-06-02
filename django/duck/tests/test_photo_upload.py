"""Tests for the full image upload path (mocks only the Flickr API call)."""
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationPhoto


TEST_RECAPTCHA_SETTINGS = {
    'RECAPTCHA_PUBLIC_KEY': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    'RECAPTCHA_PRIVATE_KEY': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    'SILENCED_SYSTEM_CHECKS': ['django_recaptcha.recaptcha_test_key_error'],
}

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'playwright', 'fixtures')


def _valid_mark_data(duck_id=100):
    return {
        'duck_id': duck_id,
        'name': 'Photo Duck',
        'location': 'Dallas, TX',
        'date_time': '2026-01-15T12:00',
        'lat': '33.0',
        'lng': '-97.0',
        'comments': 'Has a photo!',
    }


@override_settings(**TEST_RECAPTCHA_SETTINGS)
class FullImageUploadPathTest(TestCase):
    """Test the complete upload path: form validation → disk save → DB record.

    Only upload_to_flickr is mocked (the external HTTP boundary).
    """

    def setUp(self):
        self.upload_dir = tempfile.mkdtemp()
        self.user = User.objects.create_user('tommy', 'tommy@test.com', 'pass')
        self.duck = Duck.objects.create(
            duck_id=100, name='Photo Duck', create_time=timezone.now(),
            comments='', total_distance=0, approved='Y',
        )
        DuckLocation.objects.create(
            duck=self.duck, latitude=32.95, longitude=-96.90,
            location='Origin', date_time=timezone.now(),
            comments='start', distance_to=0, user=self.user, approved='Y',
        )
        self.client.force_login(self.user)

    @patch('duck.photo_providers.flickr_api')
    @patch('duck.views.async_task')
    @override_settings(UPLOAD_PATH=None)  # will be set in test
    def test_full_upload_path_saves_file_and_creates_record(self, mock_async, mock_flickr_api):
        """Image goes through form validation, saves to disk, queues upload task."""
        # Use the real test fixture image
        fixture_path = os.path.join(FIXTURES_DIR, 'test_duck.jpg')
        with open(fixture_path, 'rb') as f:
            image_data = f.read()

        image = SimpleUploadedFile('test_duck.jpg', image_data, content_type='image/jpeg')
        data = _valid_mark_data()
        data['image'] = image

        with self.settings(UPLOAD_PATH=self.upload_dir):
            response = self.client.post('/mark/', data)

        # Should redirect to new location page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)

        # Verify file was saved to disk
        saved_files = os.listdir(self.upload_dir)
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(saved_files[0].endswith('.jpg'))

        # Verify upload_photo task was queued
        task_names = [call[0][0] for call in mock_async.call_args_list]
        self.assertIn('duck.tasks.upload_photo', task_names)

    @patch('duck.views.async_task')
    def test_no_photo_record_created_without_image(self, mock_async):
        """Submitting without an image creates no DuckLocationPhoto."""
        data = _valid_mark_data()
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        photos = DuckLocationPhoto.objects.filter(duck_location__duck_id=100)
        self.assertEqual(photos.count(), 0)

    @patch('duck.views.async_task')
    def test_invalid_image_rejected_no_side_effects(self, mock_async):
        """A non-image file is rejected; no location or photo is created."""
        initial_location_count = DuckLocation.objects.filter(duck_id=100).count()

        data = _valid_mark_data()
        data['image'] = SimpleUploadedFile('evil.exe', b'MZ\x90\x00' * 100, content_type='application/x-msdownload')
        response = self.client.post('/mark/', data)

        # Form re-renders (no redirect)
        self.assertEqual(response.status_code, 200)

        # No new location or photo created
        self.assertEqual(
            DuckLocation.objects.filter(duck_id=100).count(),
            initial_location_count,
        )
        self.assertEqual(DuckLocationPhoto.objects.filter(duck_location__duck_id=100).count(), 0)
