from rest_framework.exceptions import ValidationError
from annotation.helpers.utils.constants.supported_requests_types import RequestContentType


class RequestValidation:
    """
    Validates the request.
    """

    @staticmethod
    def content_type(request, mode: RequestContentType):
        """
        Validate that the request's content type matches the expected type.

        Args:
            request: Django request object.
            mode (RequestContentType): Expected content type enum.

        Raises:
            ValidationError: If content type does not match the expected type.
        """

        expected = mode.value
        if not request.content_type.startswith(expected):
            raise ValidationError(f'Request must be {expected}.')

    @staticmethod
    def has_file_key(request, key):
        """
        Check if a file is included in the request under the specified key.

        Args:
            request: Django or DRF request object.
            key (str): Key under which file should be uploaded.

        Raises:
            ValidationError: If the file is not found under the given key.
        """

        if key not in request.FILES:
            raise ValidationError(f'No file uploaded with key {key}.')
