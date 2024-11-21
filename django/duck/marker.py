""" Helper functions for uploading image to Flickr """
import flickr_api, os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .models import Duck, DuckLocation, DuckLocationPhoto
from haversine import haversine, Unit
from django.core.mail import EmailMessage
import datetime

def create_new_duck(duck_id, name):
    """ Create a new Duck """
    duck = Duck(duck_id=duck_id,
                name=name, 
                approved='Y',
                total_distance=0,
                create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                comments='')
    duck.save()

    add_initial_duck_location(duck) 
    return duck

def add_initial_duck_location(duck):
    """ Create new DuckLocation from it's origin """
    tommy = User.objects.get(id=1)
    duck_location_start = DuckLocation(duck=duck,
                    latitude='32.95159763382337',
                    longitude='-96.90789423886032',
                    location='Carrollton Plaza Arts Center, Carrollton, TX',
                    date_time='2008-08-16 20:00:00',
                    comments='Just got married!',
                    distance_to=0,
                    user=tommy,
                    approved='Y')
    duck_location_start.save()

def add_duck_location(duck_id, latitude, longitude, location, date_time, comments, user):
    # Calculate the distance since last location
    last_duck_location = DuckLocation.objects.filter(duck_id=duck_id).order_by('-date_time')[0]
    distance_travelled = haversine((last_duck_location.latitude, last_duck_location.longitude),
                                    (latitude, longitude), unit=Unit.MILES)
    duck_location = DuckLocation(duck_id=duck_id,
                                    latitude=latitude,
                                    longitude=longitude,
                                    location=location,
                                    date_time=date_time,
                                    comments=comments,
                                    distance_to=round(distance_travelled, 2),
                                    user=user,
                                    approved='Y')
    duck_location.save()
    return duck_location

def add_duck_location_photo(duck_id, duck_name, image, comments, duck_location):
    title = 'Duck #' + str(duck_id) + ' (' + duck_name + ')'
    tags = "duckiehunt"

    photo_info = handle_uploaded_file(image, duck_id, duck_name, comments)
    duck_location_photo = DuckLocationPhoto(duck_location=duck_location,
                                            flickr_photo_id=photo_info['id'],
                                            flickr_thumbnail_url=photo_info['sizes']['Small 320']['source'])
    duck_location_photo.save()

def email_duck_location(duck_id, duck_location_url):
    """ Send an email to the user with the location """
    msg = EmailMessage(
        'Duckiehunt Update: Duck #' + str(duck_id),
        'Duck #' + str(duck_id) + ' has moved!<br/>' + settings.BASE_URL + duck_location_url,
        settings.EMAIL_FROM, settings.EMAIL_TO
    )
    msg.content_subtype = "html"
    msg.send()

def handle_uploaded_file(uploaded_file, duck_id, duck_name, comments):
    """ Upload duck location image to flickr """
    title = 'Duck #' + str(duck_id) + ' (' + duck_name + ')'
    tags = "duckiehunt"

    file_path = save_uploaded_file(uploaded_file, settings.UPLOAD_PATH)
    photo_info = upload_to_flickr(file_path, title, comments, settings.FLICKR_PHOTO_IS_PUBLIC, tags)
    return photo_info

def save_uploaded_file(uploaded_file, upload_path):
    """
    Save a Django uploaded file to the local disk.

    Args:
        uploaded_file: The uploaded file object.
        upload_path: The path where the file should be saved.

    Returns:
        The file path where the uploaded file is saved.
    """
    fss = FileSystemStorage(location=upload_path)
    filename = fss.save(uploaded_file.name, uploaded_file)
    file_path = fss.path(filename)
    return file_path

def upload_to_flickr(photo_file, title, comments, is_public, tags):
    """ Upload file to flickr """
    # No idea why, but is_public DOESN'T WORK.
    photo = flickr_api.upload(photo_file=photo_file, title=title, is_public=is_public,
                              tags=tags, description=comments)
    photo_info = photo.getInfo()
    photo_info['sizes'] = photo.getSizes()
    return photo_info