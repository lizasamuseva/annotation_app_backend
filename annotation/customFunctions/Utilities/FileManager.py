import os
import tempfile
import uuid

from django.core.files.storage import FileSystemStorage
from django.core.cache import cache

from api import settings

class FileManager:
    """
    Handles file storage operations used throughout the application's execution.
    """

    @staticmethod
    def process_temporally_file_saving_WITHIN_REQUEST(uploaded_file):
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
    def process_persistence_file_saving_ACROSS_REQUESTS(uploaded_file):
        """
        Stores the uploaded file in MEDIA root folder to access file across multiple requests.
        """

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        return fs.path(filename)

    @staticmethod
    def create_and_save_file_in_MEDIA(content, filename, subdir="uploads"):
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

        # Create cache key
        cache_key = f"{cache_key_description}:{uuid.uuid4()}"

        # Connect the cache key with entity
        cache.set(cache_key, entity_to_save, timeout=3600)

        # Save the record within one session:
        # 1. To allow access across multiple requests.
        # 2. To ensure each user has isolated data.
        request.session[f'{cache_key_description}'] = cache_key

    @staticmethod
    def cleanup_file(file_path):
        """
        Deletes the specified file from the MEDIA folder.
        """
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass