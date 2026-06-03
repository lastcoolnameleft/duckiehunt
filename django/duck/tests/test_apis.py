"""Tests for duck.apis JSON endpoints."""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationPhoto


class DuckAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'test@example.com', 'pass')
        self.duck_time = timezone.now().replace(microsecond=0)
        self.location_time = timezone.now().replace(microsecond=0)

        self.duck = Duck.objects.create(
            duck_id=1,
            name='API Duck',
            comments='',
            create_time=self.duck_time,
            total_distance=50.5,
            approved='Y',
        )
        self.other_duck = Duck.objects.create(
            duck_id=2,
            name='Second Duck',
            comments='',
            create_time=self.duck_time,
            total_distance=12.25,
            approved='N',
        )
        self.empty_duck = Duck.objects.create(
            duck_id=3,
            name='Empty Duck',
            comments='',
            create_time=self.duck_time,
            total_distance=0,
            approved='Y',
        )

        self.location = DuckLocation.objects.create(
            duck=self.duck,
            user=self.user,
            latitude=32.95,
            longitude=-96.9,
            comments='First spot',
            date_time=self.location_time,
        )
        self.other_location = DuckLocation.objects.create(
            duck=self.other_duck,
            user=self.user,
            latitude=40.71,
            longitude=-74.0,
            comments='Second spot',
            date_time=self.location_time,
        )

    def test_get_duck_detail_returns_existing_duck_json(self):
        response = self.client.get(f'/api/duck/{self.duck.duck_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'duck_id': self.duck.duck_id,
                'name': self.duck.name,
                'total_distance': self.duck.total_distance,
                'create_time': self.duck_time.isoformat().replace('+00:00', 'Z'),
                'approved': self.duck.approved,
            },
        )

    def test_get_duck_detail_returns_404_for_missing_duck(self):
        response = self.client.get('/api/duck/9999')

        self.assertEqual(response.status_code, 404)

    def test_get_ducks_returns_all_ducks(self):
        response = self.client.get('/api/ducks')

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    'duck_id': self.duck.duck_id,
                    'name': self.duck.name,
                    'total_distance': self.duck.total_distance,
                },
                {
                    'duck_id': self.other_duck.duck_id,
                    'name': self.other_duck.name,
                    'total_distance': self.other_duck.total_distance,
                },
                {
                    'duck_id': self.empty_duck.duck_id,
                    'name': self.empty_duck.name,
                    'total_distance': self.empty_duck.total_distance,
                },
            ],
        )

    def test_get_ducks_returns_empty_list_when_no_ducks_exist(self):
        DuckLocation.objects.all().delete()
        Duck.objects.all().delete()

        response = self.client.get('/api/ducks')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_locations_returns_all_locations(self):
        response = self.client.get('/api/locations')

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    'duck_id': self.duck.duck_id,
                    'duck__name': self.duck.name,
                    'latitude': self.location.latitude,
                    'longitude': self.location.longitude,
                    'comments': self.location.comments,
                },
                {
                    'duck_id': self.other_duck.duck_id,
                    'duck__name': self.other_duck.name,
                    'latitude': self.other_location.latitude,
                    'longitude': self.other_location.longitude,
                    'comments': self.other_location.comments,
                },
            ],
        )

    def test_get_duck_locations_filters_by_duck(self):
        response = self.client.get(f'/api/duck/{self.duck.duck_id}/locations')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    'duck_id': self.duck.duck_id,
                    'duck__name': self.duck.name,
                    'latitude': self.location.latitude,
                    'longitude': self.location.longitude,
                    'comments': self.location.comments,
                }
            ],
        )

    def test_get_duck_locations_returns_empty_for_duck_with_no_locations(self):
        response = self.client.get(f'/api/duck/{self.empty_duck.duck_id}/locations')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_location_returns_correct_location_data(self):
        response = self.client.get(f'/api/location/{self.location.duck_location_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'duck_id': self.duck.duck_id,
                'latitude': self.location.latitude,
                'longitude': self.location.longitude,
                'date_time': self.location_time.isoformat().replace('+00:00', 'Z'),
                'comments': self.location.comments,
            },
        )

    def test_get_location_returns_404_for_missing_location(self):
        response = self.client.get('/api/location/9999')

        self.assertEqual(response.status_code, 404)

    def test_get_version_returns_git_sha(self):
        with patch.dict('os.environ', {'GIT_SHA': 'abc123'}):
            response = self.client.get('/api/version')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'git_sha': 'abc123'})

    def test_get_version_returns_unknown_when_env_not_set(self):
        with patch.dict('os.environ', {}, clear=True):
            response = self.client.get('/api/version')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'git_sha': 'unknown'})

    def test_share_api_route_removed(self):
        response = self.client.post(f'/api/share/{self.location.duck_location_id}/')
        self.assertEqual(response.status_code, 404)


class DuckPhotosAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'test@example.com', 'pass')
        self.duck_time = timezone.now()
        self.duck = Duck.objects.create(
            duck_id=1, name='Photo Duck', comments='',
            create_time=self.duck_time, total_distance=0, approved='Y',
        )
        self.location = DuckLocation.objects.create(
            duck=self.duck, user=self.user,
            latitude=32.0, longitude=-96.0,
            date_time=self.duck_time,
        )
        self.photo = DuckLocationPhoto.objects.create(
            duck_location=self.location,
            flickr_photo_id=12345,
            flickr_thumbnail_url='https://example.com/thumb.jpg',
        )

    def test_get_duck_photos_returns_photos(self):
        response = self.client.get(f'/api/duck/{self.duck.duck_id}/')
        self.assertEqual(response.status_code, 200)

    def test_get_duck_photos_empty_for_duck_without_photos(self):
        other_duck = Duck.objects.create(
            duck_id=2, name='No Photos', comments='',
            create_time=self.duck_time, total_distance=0, approved='Y',
        )
        response = self.client.get(f'/api/duck/{other_duck.duck_id}/locations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
