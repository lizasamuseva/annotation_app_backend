import os
import tempfile
import uuid

from django.core.files.storage import FileSystemStorage
from django.core.cache import cache

from api import settings

class FileManager:
    @staticmethod
    def process_temporally_file_saving_WITHIN_REQUEST(uploaded_file):
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
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        return fs.path(filename)

    @staticmethod
    def create_and_save_file_in_MEDIA(content, filename, subdir="uploads"):
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, subdir))

        with fs.open(filename, 'w') as file:
            file.write(content)

        return fs.path(filename)

    @staticmethod
    def save_entity_to_the_cache(request, cache_key_description, entity_to_save):
        # Create cache key
        cache_key = f"{cache_key_description}:{uuid.uuid4()}"

        # Connect the key cache with entity
        cache.set(cache_key, entity_to_save, timeout=3600)

        # Save the record within one session. Why?
        # 1. to access the dictionary across multiple requests
        # 2. each user should have unique records
        request.session[f'{cache_key_description}'] = cache_key

    @staticmethod
    def cleanup_file(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass