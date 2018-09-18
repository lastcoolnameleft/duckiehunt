""" Client Tests """
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model

from duck.models import Duck, DuckLocation
from duck.views import index

# Create your tests here.
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
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/mark/')
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)

    def test_mark_full(self):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'name': 'test duck ' + duck_id, 'location': 'northkapp',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/duck/' + duck_id)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'test duck ' + duck_id)
        duck_location = DuckLocation.objects.filter(duck_id=duck_id)
        self.assertEqual(len(duck_location), 1)
        self.assertEqual(duck_location[0].location, 'northkapp')
        self.assertEqual(duck_location[0].latitude, 71.169493)
        self.assertEqual(duck_location[0].longitude, 25.7831639)
        self.assertEqual(duck_location[0].comments, 'this is a comment')


    def test_mark_no_name(self):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'location': 'northkapp', 'name': '',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/duck/' + duck_id)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'Unnamed')
        duck_location = DuckLocation.objects.filter(duck_id=duck_id)
        self.assertEqual(len(duck_location), 1)

    # NOT READY YET.
    def test_mark_no_name_rename(self):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'location': 'northkapp', 'name': '',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/duck/' + duck_id)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'Unnamed')
        duck_location = DuckLocation.objects.filter(duck_id=duck_id)
        self.assertEqual(len(duck_location), 1)

     