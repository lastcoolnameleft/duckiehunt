from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, TestCase

from .views import detail, mark, index


# Create your tests here.
class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
#        self.user = User.objects.create_user(
#            username='jacob', email='tommy@duckiehunt.com', password='top_secret')

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get('/')

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
#        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)
