"""Tests for background tasks (duck/tasks.py).

Tests run with DJANGO_Q_SYNC=True so async_task() executes inline,
verifying the full queue → process → result cycle.
"""
import os
import tempfile
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationPhoto
from duck.tasks import upload_photo, share_to_social, send_email_notification


def _create_test_duck_and_location(user):
    """Create a duck with one location for testing."""
    duck = Duck.objects.create(
        duck_id=500, name='Task Test Duck', create_time=timezone.now(),
        comments='', total_distance=0, approved='Y',
    )
    location = DuckLocation.objects.create(
        duck=duck, user=user,
        latitude=32.95, longitude=-96.90,
        location='Dallas, TX', date_time=timezone.now(),
        distance_to=0, approved='Y', comments='Test sighting',
    )
    return duck, location


class UploadPhotoTaskTest(TestCase):
    """Tests for the upload_photo background task."""

    def setUp(self):
        self.user = User.objects.create_user('taskuser', 'task@test.com', 'pass')
        self.duck, self.location = _create_test_duck_and_location(self.user)
        # Create a photo record with local_path (as views.py now does)
        self.photo = DuckLocationPhoto.objects.create(
            duck_location=self.location,
            local_path='test_duck.jpg',
        )
        # Create a temp file to simulate saved image
        self.tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        self.tmp.write(b'\xff\xd8\xff\xe0' + b'\x00' * 100)  # minimal JPEG header
        self.tmp.close()

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    @patch('duck.photo_providers.get_photo_provider')
    def test_upload_photo_updates_record(self, mock_get_provider):
        """Successful upload updates the existing DuckLocationPhoto with provider URLs."""
        mock_provider = MagicMock()
        mock_provider.upload_from_path.return_value = {
            'id': '12345',
            'thumbnail_url': 'https://example.com/thumb.jpg',
        }
        mock_get_provider.return_value = mock_provider

        upload_photo(
            self.photo.duck_location_photo_id,
            self.tmp.name,
            self.duck.duck_id,
            self.duck.name,
            'Test comments',
        )

        # Verify DuckLocationPhoto was updated (not a new one created)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.flickr_photo_id, 12345)
        self.assertEqual(self.photo.flickr_thumbnail_url, 'https://example.com/thumb.jpg')
        self.assertEqual(DuckLocationPhoto.objects.count(), 1)

        # Verify provider was called with correct args
        mock_provider.upload_from_path.assert_called_once_with(
            self.tmp.name, 'Duck #500 (Task Test Duck)', 'Test comments', tags='duckiehunt'
        )

    @patch('duck.photo_providers.get_photo_provider')
    def test_upload_photo_handles_provider_error(self, mock_get_provider):
        """Provider exception is caught — record keeps local_path, no Flickr URL."""
        mock_provider = MagicMock()
        mock_provider.upload_from_path.side_effect = Exception("Flickr is down")
        mock_get_provider.return_value = mock_provider

        # Should not raise
        upload_photo(
            self.photo.duck_location_photo_id,
            self.tmp.name,
            self.duck.duck_id,
            self.duck.name,
            'Test',
        )

        self.photo.refresh_from_db()
        self.assertIsNone(self.photo.flickr_photo_id)
        self.assertEqual(self.photo.local_path, 'test_duck.jpg')

    def test_upload_photo_missing_record(self):
        """Task with non-existent photo ID logs error, doesn't crash."""
        upload_photo(99999, self.tmp.name, 500, 'Test', 'comments')

    @override_settings(Q_CLUSTER={'name': 'test', 'sync': True, 'orm': 'default'})
    @patch('duck.photo_providers.get_photo_provider')
    def test_upload_photo_via_async_task(self, mock_get_provider):
        """Task queued via async_task executes and updates the photo record."""
        from django_q.tasks import async_task

        mock_provider = MagicMock()
        mock_provider.upload_from_path.return_value = {
            'id': '67890',
            'thumbnail_url': 'https://example.com/queued.jpg',
        }
        mock_get_provider.return_value = mock_provider

        async_task(
            'duck.tasks.upload_photo',
            self.photo.duck_location_photo_id,
            self.tmp.name,
            self.duck.duck_id,
            self.duck.name,
            'Queued test',
        )

        self.photo.refresh_from_db()
        self.assertEqual(self.photo.flickr_photo_id, 67890)


class ShareToSocialTaskTest(TestCase):
    """Tests for the share_to_social background task."""

    def setUp(self):
        self.user = User.objects.create_user('socialuser', 'social@test.com', 'pass')
        self.duck, self.location = _create_test_duck_and_location(self.user)

    @patch('duck.social.share_to_all')
    def test_share_to_social_calls_providers(self, mock_share_all):
        """Approved sighting is shared to all configured providers."""
        mock_share_all.return_value = {
            'facebook': {'success': True, 'post_id': 'fb_123'},
        }

        share_to_social(self.location.duck_location_id)

        mock_share_all.assert_called_once_with(self.location, photo_url=None)

    @patch('duck.social.share_to_all')
    def test_share_to_social_includes_photo_url(self, mock_share_all):
        """If a photo exists, its URL is passed to providers."""
        DuckLocationPhoto.objects.create(
            duck_location=self.location,
            flickr_photo_id=111,
            flickr_thumbnail_url='https://flickr.com/photo.jpg',
        )
        mock_share_all.return_value = {'facebook': {'success': True, 'post_id': 'x'}}

        share_to_social(self.location.duck_location_id)

        mock_share_all.assert_called_once_with(
            self.location, photo_url='https://flickr.com/photo.jpg'
        )

    @patch('duck.social.share_to_all')
    def test_share_to_social_skips_unapproved(self, mock_share_all):
        """Unapproved sightings are not shared."""
        self.location.approved = 'N'
        self.location.save()

        share_to_social(self.location.duck_location_id)

        mock_share_all.assert_not_called()

    @patch('duck.social.share_to_all')
    def test_share_to_social_missing_location(self, mock_share_all):
        """Non-existent location ID doesn't crash."""
        share_to_social(99999)
        mock_share_all.assert_not_called()

    @override_settings(Q_CLUSTER={'name': 'test', 'sync': True, 'orm': 'default'})
    @patch('duck.social.share_to_all')
    def test_share_via_async_task(self, mock_share_all):
        """Task queued via async_task executes correctly."""
        from django_q.tasks import async_task

        mock_share_all.return_value = {'facebook': {'success': True, 'post_id': 'q_123'}}

        async_task('duck.tasks.share_to_social', self.location.duck_location_id)

        mock_share_all.assert_called_once()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_FROM='test@duckiehunt.com',
    EMAIL_TO=['admin@duckiehunt.com'],
    BASE_URL='https://duckiehunt.com',
)
class SendEmailNotificationTaskTest(TestCase):
    """Tests for the send_email_notification background task."""

    def test_send_email_success(self):
        """Email is sent with correct subject and body."""
        send_email_notification(42, '/location/100')

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Duckiehunt Update: Duck #42')
        self.assertIn('Duck #42 has moved!', email.body)
        self.assertIn('https://duckiehunt.com/location/100', email.body)
        self.assertEqual(email.from_email, 'test@duckiehunt.com')
        self.assertEqual(email.to, ['admin@duckiehunt.com'])

    @override_settings(EMAIL_BACKEND='duck.tests.test_tasks.FailingEmailBackend')
    def test_send_email_handles_error(self):
        """Email failure is caught — doesn't crash the task."""
        # Should not raise
        send_email_notification(42, '/location/100')


class FailingEmailBackend:
    """Email backend that always raises for testing error handling."""
    def __init__(self, *args, **kwargs):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def send_messages(self, messages):
        raise Exception("SMTP down")

    @override_settings(Q_CLUSTER={'name': 'test', 'sync': True, 'orm': 'default'})
    def test_email_via_async_task(self):
        """Task queued via async_task sends the email."""
        from django_q.tasks import async_task

        async_task('duck.tasks.send_email_notification', 7, '/location/55')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Duck #7', mail.outbox[0].subject)
