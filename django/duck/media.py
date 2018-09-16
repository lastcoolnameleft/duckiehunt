""" Helper functions for uploading image to Flickr """
import flickr_api
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def handle_uploaded_file(uploaded_file, duck_id, duck_name, comments):
    """ Upload duck location image to flickr """
    api_key = settings.FLICKR_API_KEY
    api_secret = settings.FLICKR_API_SECRET
    flickr_auth_file = settings.FLICKR_AUTH_FILE #'/tmp/authfile'
    title = 'Duck #' + str(duck_id) + ' (' + duck_name + ')'
    is_public = "0"
    tags = "duckiehunt"

    file_path = write_upload_to_file(uploaded_file, settings.UPLOAD_PATH)
    photo_info = upload_to_flickr(api_key, api_secret, flickr_auth_file, file_path,
                                  title, comments, is_public, tags)
    return photo_info

def write_upload_to_file(photo_file, upload_path):
    """ Save bufferred file in memory to disk """
    fss = FileSystemStorage()
    filename = fss.save(upload_path + photo_file.name, photo_file)
    uploaded_file_url = fss.url(filename)
    return uploaded_file_url

def upload_to_flickr(api_key, api_secret, flickr_auth_file, photo_file,
                     title, comments, is_public, tags):
    """ Upload file to flickr """
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
    flickr_api.set_auth_handler(flickr_auth_file)
    photo = flickr_api.upload(photo_file=photo_file, title=title, is_public=is_public,
                              tags=tags, description=comments)
    photo_info = photo.getInfo()
    photo_info['sizes'] = photo.getSizes()
    print(photo_info)
    return photo_info
