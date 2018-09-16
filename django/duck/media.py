""" Helper functions for uploading image to Flickr """
import flickr_api
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def handle_uploaded_file(uploaded_file, duck_id, duck_name, comments):
    """ Upload duck location image to flickr """
    title = 'Duck #' + str(duck_id) + ' (' + duck_name + ')'
    tags = "duckiehunt"

    file_path = write_upload_to_file(uploaded_file, settings.UPLOAD_PATH)
    photo_info = upload_to_flickr(file_path, title, comments, settings.FLICKR_PHOTO_IS_PUBLIC, tags)
    return photo_info

def write_upload_to_file(photo_file, upload_path):
    """ Save bufferred file in memory to disk """
    fss = FileSystemStorage()
    filename = fss.save(upload_path + photo_file.name, photo_file)
    uploaded_file_url = fss.url(filename)
    return uploaded_file_url

def upload_to_flickr(photo_file, title, comments, is_public, tags):
    """ Upload file to flickr """
    photo = flickr_api.upload(photo_file=photo_file, title=title, is_public=is_public,
                              tags=tags, description=comments)
    photo_info = photo.getInfo()
    photo_info['sizes'] = photo.getSizes()
    return photo_info
