from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationLink, DuckLocationPhoto


class DuckModelTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.user = User.objects.create_user(
            username='ducktester',
            email='ducktester@example.com',
            password='password123',
        )

    def test_duck_creation_with_all_fields(self):
        duck = Duck.objects.create(
            duck_id=1,
            create_time=self.now,
            name='Mallory',
            comments='Ready to travel',
            total_distance=123.45,
            approved='N',
        )

        self.assertEqual(duck.duck_id, 1)
        self.assertEqual(duck.create_time, self.now)
        self.assertEqual(duck.name, 'Mallory')
        self.assertEqual(duck.comments, 'Ready to travel')
        self.assertEqual(duck.total_distance, 123.45)
        self.assertEqual(duck.approved, 'N')

    def test_duck_natural_key_returns_expected_dict(self):
        duck = Duck.objects.create(
            duck_id=2,
            create_time=self.now,
            name='Puddle Jumper',
            comments='Natural key test',
            total_distance=42.0,
        )

        self.assertEqual(
            duck.natural_key(),
            {'duck_id': 2, 'name': 'Puddle Jumper', 'total_distance': 42.0},
        )

    def test_duck_default_values(self):
        duck = Duck.objects.create(
            duck_id=3,
            create_time=self.now,
            name='',
            comments='',
        )

        self.assertEqual(duck.total_distance, 0)
        self.assertEqual(duck.approved, 'Y')

    def test_duck_location_creation_with_foreign_key(self):
        duck = Duck.objects.create(
            duck_id=4,
            create_time=self.now,
            name='Scout',
            comments='Location test',
        )

        location = DuckLocation.objects.create(
            duck=duck,
            user=self.user,
            link='https://example.com/location/1',
            latitude=59.91,
            longitude=10.75,
            comments='Seen near the harbor',
            flickr_photo_id=987654321,
            duck_history_id=12,
            date_time=self.now,
            location='Oslo Harbor',
            approved='Y',
            distance_to=3.14,
        )

        self.assertEqual(location.duck, duck)
        self.assertEqual(location.user, self.user)
        self.assertEqual(location.latitude, 59.91)
        self.assertEqual(location.longitude, 10.75)
        self.assertEqual(location.location, 'Oslo Harbor')

    def test_duck_location_is_deleted_when_duck_is_deleted(self):
        duck = Duck.objects.create(
            duck_id=5,
            create_time=self.now,
            name='Cascade',
            comments='Cascade delete test',
        )
        DuckLocation.objects.create(duck=duck, user=self.user, date_time=self.now)

        duck.delete()

        self.assertEqual(DuckLocation.objects.count(), 0)

    def test_duck_location_link_creation_with_foreign_key(self):
        duck = Duck.objects.create(
            duck_id=6,
            create_time=self.now,
            name='Linked',
            comments='Link test',
        )
        location = DuckLocation.objects.create(duck=duck, user=self.user, date_time=self.now)

        location_link = DuckLocationLink.objects.create(
            duck_location=location,
            link='https://example.com/more-info',
        )

        self.assertEqual(location_link.duck_location, location)
        self.assertEqual(location_link.link, 'https://example.com/more-info')

    def test_duck_location_photo_creation_with_foreign_key(self):
        duck = Duck.objects.create(
            duck_id=7,
            create_time=self.now,
            name='Snapshot',
            comments='Photo test',
        )
        location = DuckLocation.objects.create(duck=duck, user=self.user, date_time=self.now)

        photo = DuckLocationPhoto.objects.create(
            duck_location=location,
            flickr_photo_id=123456789,
            flickr_thumbnail_url='https://example.com/thumb.jpg',
        )

        self.assertEqual(photo.duck_location, location)
        self.assertEqual(photo.flickr_photo_id, 123456789)
        self.assertEqual(photo.flickr_thumbnail_url, 'https://example.com/thumb.jpg')

    def test_duck_can_have_multiple_locations_filtered_by_duck_id(self):
        duck = Duck.objects.create(
            duck_id=8,
            create_time=self.now,
            name='Traveler',
            comments='Multiple locations test',
        )
        other_duck = Duck.objects.create(
            duck_id=9,
            create_time=self.now,
            name='Other Duck',
            comments='Other duck',
        )
        DuckLocation.objects.create(duck=duck, user=self.user, location='First stop', date_time=self.now)
        DuckLocation.objects.create(duck=duck, user=self.user, location='Second stop', date_time=self.now)
        DuckLocation.objects.create(duck=other_duck, user=self.user, location='Elsewhere', date_time=self.now)

        locations = DuckLocation.objects.filter(duck_id=duck.duck_id).order_by('duck_location_id')

        self.assertEqual(locations.count(), 2)
        self.assertEqual(locations[0].location, 'First stop')
        self.assertEqual(locations[1].location, 'Second stop')

    def test_duck_location_can_have_multiple_photos(self):
        duck = Duck.objects.create(
            duck_id=10,
            create_time=self.now,
            name='Photogenic',
            comments='Multiple photos test',
        )
        location = DuckLocation.objects.create(duck=duck, user=self.user, date_time=self.now)
        DuckLocationPhoto.objects.create(
            duck_location=location,
            flickr_photo_id=111,
            flickr_thumbnail_url='https://example.com/photo-1.jpg',
        )
        DuckLocationPhoto.objects.create(
            duck_location=location,
            flickr_photo_id=222,
            flickr_thumbnail_url='https://example.com/photo-2.jpg',
        )

        photos = DuckLocationPhoto.objects.filter(duck_location=location).order_by('duck_location_photo_id')

        self.assertEqual(photos.count(), 2)
        self.assertEqual(photos[0].flickr_photo_id, 111)
        self.assertEqual(photos[1].flickr_photo_id, 222)
