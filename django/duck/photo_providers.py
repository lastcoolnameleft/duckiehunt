"""Photo provider abstraction for uploading and managing duck photos.

Configure the active provider via PHOTO_PROVIDER in Django settings.
Supported values: 'flickr' (default), or a dotted path to a custom class.
"""
import abc
import os

import flickr_api
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PhotoProvider(abc.ABC):
    """Interface for photo storage providers."""

    @abc.abstractmethod
    def upload(self, image_file, title, description, tags=None):
        """Upload an image and return a dict with 'id' and 'thumbnail_url'.

        Args:
            image_file: Django UploadedFile or file-like object.
            title: Photo title string.
            description: Photo description/comments.
            tags: Optional tags string.

        Returns:
            dict with keys:
                'id': provider-specific photo identifier (str or int)
                'thumbnail_url': URL to a small thumbnail
        """
        ...

    def upload_from_path(self, file_path, title, description, tags=None):
        """Upload a photo from a local file path (for async tasks).

        Default implementation opens the file and calls upload().
        Providers may override for efficiency.
        """
        from django.core.files import File
        with open(file_path, 'rb') as f:
            django_file = File(f, name=os.path.basename(file_path))
            return self.upload(django_file, title, description, tags)

    @abc.abstractmethod
    def get_url(self, photo_id):
        """Get the display URL for a photo by its provider ID."""
        ...

    @abc.abstractmethod
    def delete(self, photo_id):
        """Delete a photo by its provider ID."""
        ...


class FlickrProvider(PhotoProvider):
    """Photo provider backed by Flickr API."""

    def upload(self, image_file, title, description, tags=None):
        upload_path = getattr(settings, 'UPLOAD_PATH', '/tmp')
        file_path = _save_to_disk(image_file, upload_path)
        return self.upload_from_path(file_path, title, description, tags)

    def upload_from_path(self, file_path, title, description, tags=None):
        is_public = getattr(settings, 'FLICKR_PHOTO_IS_PUBLIC', '0')
        photo = flickr_api.upload(
            photo_file=file_path,
            title=title,
            is_public=is_public,
            tags=tags or 'duckiehunt',
            description=description,
        )
        photo_info = photo.getInfo()
        sizes = photo.getSizes()

        return {
            'id': photo_info['id'],
            'thumbnail_url': sizes.get('Small 320', {}).get('source', ''),
        }

    def get_url(self, photo_id):
        photo = flickr_api.Photo(id=photo_id)
        sizes = photo.getSizes()
        return sizes.get('Medium', {}).get('source', '')

    def delete(self, photo_id):
        photo = flickr_api.Photo(id=photo_id)
        photo.delete()


def _save_to_disk(uploaded_file, upload_path):
    """Save an uploaded file to local disk, return the path."""
    fss = FileSystemStorage(location=upload_path)
    filename = fss.save(uploaded_file.name, uploaded_file)
    return fss.path(filename)


def get_photo_provider():
    """Return the configured photo provider instance.

    Uses settings.PHOTO_PROVIDER (default: 'flickr').
    Can be 'flickr' or a dotted path to a PhotoProvider subclass.
    """
    provider_setting = getattr(settings, 'PHOTO_PROVIDER', 'flickr')

    if provider_setting == 'flickr':
        return FlickrProvider()

    # Support dotted path to custom provider class
    from django.utils.module_loading import import_string
    provider_class = import_string(provider_setting)
    return provider_class()
