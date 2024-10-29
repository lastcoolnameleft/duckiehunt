""" Helper functions for uploading image to Flickr """
import flickr_api, os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

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
