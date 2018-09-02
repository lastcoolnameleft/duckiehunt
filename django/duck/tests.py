from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, TestCase, Client

from .models import Duck, DuckLocation, DuckLocationPhoto
from .views import detail, mark, index
from .forms import DuckForm

# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()

    def test_details(self):
        request = self.factory.get('/')
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_mark(self):
        data = {'duck_id': '999', 'name': 'test duck 999', 'location': 'northkapp',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08'}
        response = self.c.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/duck/999')
        duck = Duck.objects.get(pk=999)
        self.assertEqual(duck.name, 'test duck 999')
        duck_location = DuckLocation.objects.filter(duck_id=999)
        self.assertEqual(len(duck_location), 1)
        self.assertEqual(duck_location[0].location, 'northkapp')
        self.assertEqual(duck_location[0].latitude, 71.169493)
        self.assertEqual(duck_location[0].longitude, 25.7831639)

