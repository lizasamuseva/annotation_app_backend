import os
import tempfile

from django.core.cache import cache
from django.core.files.storage import FileSystemStorage

from annotation.helpers.utils.custom_exceptions import SessionExpired
from api import settings


class FileManager:
    """
    Handles file storage operations used throughout the application's execution.
    """

    @staticmethod
    def process_temporally_file_saving_within_request(uploaded_file):
        """
        Temporarily stores the uploaded file for use within the scope of a single request.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.rml')
        try:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            temp_file.close()
            raise e

    @staticmethod
    def process_persistent_file_saving_across_requests(uploaded_file):
        """
        Stores the uploaded file in MEDIA root folder to access file across multiple requests.
        """

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        return fs.path(filename)

    @staticmethod
    def create_and_save_file_in_media(content, filename, subdir="uploads"):
        """
        Creates a new file (e.g. annotated version of the ePPG file) and stores it in MEDIA folder.
        """

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, subdir))

        with fs.open(filename, 'w') as file:
            file.write(content)

        return fs.path(filename)

    @staticmethod
    def save_entity_to_the_cache(request, cache_key_description, entity_to_save):
        """
        Caches annotation-related data and links to the user session for later retrieval.
        """
        # Save cache key if it is first initialization
        if not request.session.session_key:
            request.session.save()

        # Set the Cache key name
        generated_cache_key = f"{cache_key_description}:{request.session.session_key}"
        # Set entity in the cache
        cache.set(generated_cache_key, entity_to_save, timeout=3600)
        # Link Session nand Cache key
        request.session[cache_key_description] = generated_cache_key

    @staticmethod
    def get_entity_from_cache(request, cache_key_description):
        """
        Returns the entity connected to the session-cache key.

        Raises:
            SessionExpired: if the session key is expired.
        """
        cache_key = request.session.get(cache_key_description)
        if cache_key:
            entity = cache.get(cache_key)
            return entity

        raise SessionExpired

    @staticmethod
    def cleanup_file(file_path):
        """
        Deletes the specified file from the MEDIA folder.
        """
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
