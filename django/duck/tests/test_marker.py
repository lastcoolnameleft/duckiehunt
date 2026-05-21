"""Tests for duck.marker business logic"""
import os
import tempfile
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone

from duck.models import Duck, DuckLocation
from duck import marker


class CreateNewDuckTest(TestCase):
    def setUp(self):
        # marker.add_initial_duck_location requires User with id=1
        self.user = User.objects.create_user(
            username='tommy', email='tommy@test.com', password='pass'
        )

    def test_creates_duck_with_correct_fields(self):
        duck = marker.create_new_duck(42, 'Quackers')
        self.assertEqual(duck.duck_id, 42)
        self.assertEqual(duck.name, 'Quackers')
        self.assertEqual(duck.approved, 'Y')
        self.assertEqual(duck.total_distance, 0)
        self.assertIsNotNone(duck.create_time)

    def test_creates_initial_location(self):
        duck = marker.create_new_duck(42, 'Quackers')
        locations = DuckLocation.objects.filter(duck=duck)
        self.assertEqual(locations.count(), 1)
        loc = locations.first()
        self.assertAlmostEqual(loc.latitude, 32.95159763382337)
        self.assertAlmostEqual(loc.longitude, -96.90789423886032)
        self.assertEqual(loc.distance_to, 0)
        self.assertEqual(loc.user, self.user)

    def test_duck_persists_in_db(self):
        marker.create_new_duck(42, 'Quackers')
        duck = Duck.objects.get(pk=42)
        self.assertEqual(duck.name, 'Quackers')


class AddDuckLocationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tommy', email='tommy@test.com', password='pass'
        )
        self.duck = Duck.objects.create(
            duck_id=1, name='Traveler', create_time=timezone.now(),
            total_distance=0, approved='Y', comments='',
        )
        # Initial location in Dallas
        DuckLocation.objects.create(
            duck=self.duck, user=self.user,
            latitude=32.95, longitude=-96.90,
            location='Dallas, TX',
            date_time='2020-01-01 00:00:00',
            distance_to=0, approved='Y',
        )

    def test_calculates_distance(self):
        # New York is roughly 1,370 miles from Dallas
        loc = marker.add_duck_location(
            duck_id=1,
            latitude=40.7128, longitude=-74.0060,
            location='New York, NY',
            date_time='2020-06-01 12:00:00',
            comments='Moved to NYC',
            user=self.user,
        )
        self.assertGreater(loc.distance_to, 1300)
        self.assertLess(loc.distance_to, 1500)

    def test_saves_correct_fields(self):
        loc = marker.add_duck_location(
            duck_id=1,
            latitude=40.7128, longitude=-74.0060,
            location='New York, NY',
            date_time='2020-06-01 12:00:00',
            comments='Test comment',
            user=self.user,
        )
        self.assertEqual(loc.duck_id, 1)
        self.assertAlmostEqual(loc.latitude, 40.7128)
        self.assertAlmostEqual(loc.longitude, -74.0060)
        self.assertEqual(loc.location, 'New York, NY')
        self.assertEqual(loc.comments, 'Test comment')
        self.assertEqual(loc.approved, 'Y')
        self.assertEqual(loc.user, self.user)

    def test_distance_zero_for_same_location(self):
        loc = marker.add_duck_location(
            duck_id=1,
            latitude=32.95, longitude=-96.90,
            location='Dallas again',
            date_time='2020-02-01 00:00:00',
            comments='Still here',
            user=self.user,
        )
        self.assertAlmostEqual(loc.distance_to, 0, places=1)


class EmailDuckLocationTest(TestCase):
    def test_sends_email_with_correct_content(self):
        marker.email_duck_location(5, '/location/100')
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Duck #5', email.subject)
        self.assertIn('/location/100', email.body)
        self.assertEqual(email.content_subtype, 'html')

    def test_email_recipients(self):
        marker.email_duck_location(1, '/location/1')
        email = mail.outbox[0]
        self.assertEqual(email.to, ['test@example.com'])


class SaveUploadedFileTest(TestCase):
    def test_saves_file_to_disk(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        upload_dir = tempfile.mkdtemp()
        try:
            uploaded = SimpleUploadedFile('duckie.jpg', b'fake image data')
            file_path = marker.save_uploaded_file(uploaded, upload_dir)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'rb') as f:
                self.assertEqual(f.read(), b'fake image data')
        finally:
            # Cleanup
            for f in os.listdir(upload_dir):
                os.remove(os.path.join(upload_dir, f))
            os.rmdir(upload_dir)


class HandleUploadedFileTest(TestCase):
    @patch('duck.marker.upload_to_flickr')
    def test_calls_upload_with_correct_args(self, mock_upload):
        from django.core.files.uploadedfile import SimpleUploadedFile

        mock_upload.return_value = {
            'id': '12345',
            'sizes': {'Small 320': {'source': 'http://example.com/thumb.jpg'}},
        }

        uploaded = SimpleUploadedFile('duckie.jpg', b'image data')
        result = marker.handle_uploaded_file(uploaded, 7, 'Lucky Duck', 'Found it!')

        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        self.assertIn('Duck #7 (Lucky Duck)', call_args[1].get('title', call_args[0][1] if len(call_args[0]) > 1 else ''))
        self.assertEqual(result['id'], '12345')
