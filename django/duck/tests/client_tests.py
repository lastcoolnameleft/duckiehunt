from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, TestCase, Client

from duck.models import Duck, DuckLocation, DuckLocationPhoto
from duck.views import detail, mark, index
from duck.forms import DuckForm

# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_details(self):
        request = self.factory.get('/')
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_mark_full(self):
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