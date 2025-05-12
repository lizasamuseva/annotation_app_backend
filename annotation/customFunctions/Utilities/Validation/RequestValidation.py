from rest_framework.exceptions import ValidationError

from annotation.customFunctions.Utilities.Constants.SupportedRequestsTypes import RequestContentType


class RequestValidation:
    @staticmethod
    def content_type(request, mode: RequestContentType):
        expected = mode.value
        if not request.content_type.startswith(expected):
            raise ValidationError(f'Request must be {expected}.')

    @staticmethod
    def has_file_key(request, key):
        if key not in request.FILES:
            raise ValidationError(f'No file uploaded with key {key}.')
