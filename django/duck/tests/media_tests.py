""" Media Tests """
from django.test import TestCase
import flickr_api
from duck import media
try:
    from duckiehunt.local_settings import *
except ImportError:
    pass

# Create your tests here.
class MediaTest(TestCase):

    def test_upload(self):
        photo_id = media.upload_to_flickr('/tmp/thelab_social_genericprofile.jpg',
                                          'test image', 'test comment', '0', 'tag1, tag2')

        print(photo_id)
        self.assertTrue(photo_id)
