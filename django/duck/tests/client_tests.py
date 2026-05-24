""" Client Tests """
from unittest.mock import patch

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model

from duck.models import Duck, DuckLocation
from duck.views import index


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_details(self):
        request = self.factory.get('/')
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_secure_page(self):
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recaptcha')
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)

    @patch('duck.marker.email_duck_location')
    def test_mark_full(self, mock_email):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'name': 'test duck ' + duck_id, 'location': 'northkapp',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment', 'g-recaptcha-response': 'PASSED'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'test duck ' + duck_id)
        # Initial location + new location = 2
        duck_location = DuckLocation.objects.filter(duck_id=duck_id).order_by('duck_location_id')
        self.assertEqual(len(duck_location), 2)
        new_loc = duck_location[1]
        self.assertEqual(new_loc.location, 'northkapp')
        self.assertEqual(new_loc.latitude, 71.169493)
        self.assertEqual(new_loc.longitude, 25.7831639)
        self.assertEqual(new_loc.comments, 'this is a comment')

    @patch('duck.marker.email_duck_location')
    def test_mark_no_name(self, mock_email):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'location': 'northkapp', 'name': '',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment', 'g-recaptcha-response': 'PASSED'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'Unnamed')
        duck_location = DuckLocation.objects.filter(duck_id=duck_id)
        self.assertEqual(len(duck_location), 2)  # initial + new

    @patch('duck.marker.email_duck_location')
    def test_mark_no_name_rename(self, mock_email):
        """An unnamed duck gets renamed when a new name is provided."""
        self.client.force_login(self.user)
        duck_id = '2'
        # First mark: creates duck as Unnamed
        data = {'duck_id': duck_id, 'location': 'northkapp', 'name': '',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'first', 'g-recaptcha-response': 'PASSED'}
        self.client.post('/mark/', data)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'Unnamed')

        # Second mark: renames the duck
        data2 = {'duck_id': duck_id, 'location': 'oslo', 'name': 'Renamed Duck',
                 'lat': '59.91', 'lng': '10.75', 'date_time': '10/01/2018 12:00:00',
                 'comments': 'second', 'g-recaptcha-response': 'PASSED'}
        response = self.client.post('/mark/', data2)
        self.assertEqual(response.status_code, 302)
        duck.refresh_from_db()
        self.assertEqual(duck.name, 'Renamed Duck')
