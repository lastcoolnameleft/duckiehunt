"""Tests for file upload validation and anonymous write policy (issue #93)"""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from duck.models import Duck, DuckLocation


TEST_RECAPTCHA_SETTINGS = {
    'RECAPTCHA_PUBLIC_KEY': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    'RECAPTCHA_PRIVATE_KEY': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    'SILENCED_SYSTEM_CHECKS': ['django_recaptcha.recaptcha_test_key_error'],
}


def _create_test_duck(user):
    """Create a duck with initial location for testing."""
    duck = Duck.objects.create(
        duck_id=100, name='Test Duck', create_time=timezone.now(),
        comments='', total_distance=0, approved='Y',
    )
    DuckLocation.objects.create(
        duck=duck, latitude=32.95, longitude=-96.90,
        location='Origin', date_time=timezone.now(),
        comments='start', distance_to=0, user=user, approved='Y',
    )
    return duck


def _valid_mark_data(duck_id=100):
    return {
        'duck_id': duck_id,
        'name': 'Test Duck',
        'location': 'Dallas, TX',
        'date_time': '2026-01-15T12:00',
        'lat': '33.0',
        'lng': '-97.0',
        'comments': 'Found it!',
    }


@override_settings(**TEST_RECAPTCHA_SETTINGS)
class AnonymousWritePolicyTest(TestCase):
    """Anonymous submissions should be marked as unapproved."""

    def setUp(self):
        self.user = User.objects.create_user('tommy', 'tommy@test.com', 'pass')
        _create_test_duck(self.user)

    @patch('duck.marker.email_duck_location')
    @patch('django_recaptcha.fields.ReCaptchaField.validate', return_value=None)
    def test_anonymous_submission_approved_by_default(self, mock_captcha, mock_email):
        """Anonymous users' sightings are approved by default."""
        data = _valid_mark_data()
        data['g-recaptcha-response'] = 'PASSED'
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        location = DuckLocation.objects.filter(duck_id=100).order_by('-duck_location_id').first()
        self.assertEqual(location.approved, 'Y')
        self.assertIsNone(location.user)
        mock_email.assert_called_once()

    @patch.dict('os.environ', {'REQUIRE_ANONYMOUS_REVIEW': 'true'})
    @patch('duck.marker.email_duck_location')
    @patch('django_recaptcha.fields.ReCaptchaField.validate', return_value=None)
    def test_anonymous_submission_unapproved_when_env_set(self, mock_captcha, mock_email):
        """Anonymous sightings are unapproved when REQUIRE_ANONYMOUS_REVIEW=true."""
        data = _valid_mark_data()
        data['g-recaptcha-response'] = 'PASSED'
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        location = DuckLocation.objects.filter(duck_id=100).order_by('-duck_location_id').first()
        self.assertEqual(location.approved, 'N')
        self.assertIsNone(location.user)
        mock_email.assert_not_called()

    @patch('duck.marker.email_duck_location')
    def test_authenticated_submission_marked_approved(self, mock_email):
        """Authenticated users' sightings are saved with approved='Y'."""
        self.client.force_login(self.user)
        response = self.client.post('/mark/', _valid_mark_data())
        self.assertEqual(response.status_code, 302)

        location = DuckLocation.objects.filter(duck_id=100).order_by('-duck_location_id').first()
        self.assertEqual(location.approved, 'Y')
        self.assertEqual(location.user, self.user)
        mock_email.assert_called_once()


@override_settings(**TEST_RECAPTCHA_SETTINGS)
class FileUploadValidationTest(TestCase):
    """File uploads should go through form validation."""

    def setUp(self):
        self.user = User.objects.create_user('tommy', 'tommy@test.com', 'pass')
        _create_test_duck(self.user)
        self.client.force_login(self.user)

    def test_invalid_file_type_rejected(self):
        """Uploading a non-image file is rejected by form validation."""
        data = _valid_mark_data()
        data['image'] = SimpleUploadedFile('evil.txt', b'not an image', content_type='text/plain')
        response = self.client.post('/mark/', data)
        # Form re-renders (200) instead of redirecting (302)
        self.assertEqual(response.status_code, 200)

    @patch('duck.marker.handle_uploaded_file')
    def test_valid_image_accepted(self, mock_upload):
        """Uploading a valid image file proceeds through form."""
        mock_upload.return_value = {
            'id': 12345,
            'sizes': {'Small 320': {'source': 'http://example.com/thumb.jpg'}},
        }
        # Create a minimal valid 1x1 PNG
        import struct
        import zlib
        raw_data = b'\x00\x00\x00\x00'  # 1 pixel RGBA
        compressed = zlib.compress(raw_data)
        png = b'\x89PNG\r\n\x1a\n'
        # IHDR
        ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        png += struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        # IDAT
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        # IEND
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

        data = _valid_mark_data()
        data['image'] = SimpleUploadedFile('duck.png', png, content_type='image/png')
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        mock_upload.assert_called_once()
