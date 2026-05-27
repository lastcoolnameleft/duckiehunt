"""Tests for duck utilities and create duck feature."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from duck.utils import is_prime, is_valid_duck_number, next_available_duck_id
from duck.models import Duck


class IsPrimeTest(TestCase):
    def test_primes(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in primes:
            self.assertTrue(is_prime(p), f'{p} should be prime')

    def test_non_primes(self):
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16]
        for n in non_primes:
            self.assertFalse(is_prime(n), f'{n} should not be prime')


class IsValidDuckNumberTest(TestCase):
    def test_valid_numbers(self):
        self.assertTrue(is_valid_duck_number(4))
        self.assertTrue(is_valid_duck_number(6))
        self.assertTrue(is_valid_duck_number(100))

    def test_invalid_primes(self):
        self.assertFalse(is_valid_duck_number(3))
        self.assertFalse(is_valid_duck_number(7))
        self.assertFalse(is_valid_duck_number(13))

    def test_invalid_low_numbers(self):
        self.assertFalse(is_valid_duck_number(0))
        self.assertFalse(is_valid_duck_number(1))

    def test_special_duck_2_is_valid(self):
        self.assertTrue(is_valid_duck_number(2))


class NextAvailableDuckIdTest(TestCase):
    def test_returns_first_non_prime_when_empty(self):
        self.assertEqual(next_available_duck_id(), 4)

    def test_skips_existing(self):
        from django.utils import timezone
        Duck.objects.create(duck_id=4, name='Test', create_time=timezone.now(), comments='')
        self.assertEqual(next_available_duck_id(), 6)

    def test_skips_primes_and_existing(self):
        from django.utils import timezone
        for did in [4, 6, 8, 9, 10]:
            Duck.objects.create(duck_id=did, name='Test', create_time=timezone.now(), comments='')
        result = next_available_duck_id()
        self.assertFalse(is_prime(result))
        self.assertFalse(Duck.objects.filter(duck_id=result).exists())


class CreateDuckViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_requires_login(self):
        response = self.client.get('/duck/new')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_get_shows_form(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/duck/new')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get a Duck Number')

    def test_create_with_custom_number(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/duck/new', {'duck_id': '4', 'name': 'My Duck'})
        self.assertEqual(response.status_code, 302)
        duck = Duck.objects.get(duck_id=4)
        self.assertEqual(duck.name, 'My Duck')
        self.assertEqual(duck.created_by, self.user)

    def test_create_auto_assign(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/duck/new', {'duck_id': '', 'name': 'Auto Duck'})
        self.assertEqual(response.status_code, 302)
        duck = Duck.objects.get(name='Auto Duck')
        self.assertFalse(is_prime(duck.duck_id))
        self.assertEqual(duck.created_by, self.user)

    def test_rejects_prime_number(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/duck/new', {'duck_id': '7', 'name': 'Prime Duck'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot be prime')
        self.assertFalse(Duck.objects.filter(duck_id=7).exists())

    def test_rejects_duplicate(self):
        from django.utils import timezone
        Duck.objects.create(duck_id=4, name='Existing', create_time=timezone.now(), comments='')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/duck/new', {'duck_id': '4', 'name': 'Dup Duck'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already taken')
