from abc import ABC, abstractmethod
from rest_framework.exceptions import ValidationError
from annotation.helpers.Utilities.constants.supported_requests_types import RequestContentType, MIMETypes, \
    FilesExtensions
from annotation.helpers.Utilities.constants.constants import KEY_IN_REQUEST_RML, KEY_IN_REQUEST_EPPG
from annotation.helpers.Utilities.validation.request_validation import RequestValidation


class BaseFileValidation(ABC):
    """
    An abstract base class that defines the interface for all file validations.
    """

    def __init__(self, file_type):
        self.uploaded_file = None
        self.requestType = RequestContentType.FILE
        match file_type:
            case "RML":
                self.key_name = KEY_IN_REQUEST_RML
                self.mimeType = MIMETypes.RML
                self.fileExtension = FilesExtensions.RML
            case "EPPG":
                self.key_name = KEY_IN_REQUEST_EPPG
                self.mimeType = MIMETypes.EPPG
                self.fileExtension = FilesExtensions.EPPG
            case _:
                raise ValueError(f"Unsupported file type: {file_type}")

    def MIME_type(self):
        """
            Validates that the uploaded file has the correct MIME type.

            Raises:
                ValidationError: If the MIME type does not match the expected value.
        """
        if self.uploaded_file.content_type != self.mimeType.value:
            raise ValidationError(f'Expected file content type {self.mimeType.value}.')

    def extension(self):
        """
            Validates that the uploaded file has the correct extension.

            Raises:
                ValidationError: If the extension does not match the expected value.
        """
        if not self.uploaded_file.name.endswith(self.fileExtension.value):
            raise ValidationError(f'Only {self.fileExtension.value} files allowed.')

    def not_empty(self):
        """
            Validates that the uploaded file is not empty.

            Raises:
                ValidationError: If the file is empty.
        """
        if self.uploaded_file.size == 0:
            raise ValidationError('File is empty.')

    def base_file_validation(self, request):
        """
        Collects all base validation methods into one scope.
        """
        RequestValidation.content_type(request, self.requestType)
        RequestValidation.has_file_key(request, self.key_name)
        self.uploaded_file = request.FILES[self.key_name]
        self.MIME_type()
        self.extension()
        self.not_empty()
        return self.uploaded_file

    @abstractmethod
    def validate(self):
        """
        Should be implemented by subclasses.
        """
        pass
