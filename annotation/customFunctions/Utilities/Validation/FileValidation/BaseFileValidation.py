from abc import ABC, abstractmethod

from rest_framework.exceptions import ValidationError

from annotation.customFunctions.Utilities.Constants.SupportedRequestsTypes import RequestContentType, MIMETypes, \
    FilesExtensions
from annotation.customFunctions.Utilities.Constants.constants import KEY_IN_REQUEST_RML, KEY_IN_REQUEST_EPPG
from annotation.customFunctions.Utilities.Validation.RequestValidation import RequestValidation


class BaseFileValidation(ABC):
    def __init__(self, fileType):
        self.uploaded_file = None
        self.requestType = RequestContentType.FILE
        match fileType:
            case "RML":
                self.key_name = KEY_IN_REQUEST_RML
                self.mimeType = MIMETypes.RML
                self.fileExtension = FilesExtensions.RML
            case "EPPG":
                self.key_name = KEY_IN_REQUEST_EPPG
                self.mimeType = MIMETypes.EPPG
                self.fileExtension = FilesExtensions.EPPG
            case _:
                raise ValueError(f"Unsupported file type: {fileType}")

    def MIME_type(self):
        if self.uploaded_file.content_type != self.mimeType.value:
            raise ValidationError(f'Expected file content type {self.mimeType.value}.')

    def extension(self):
        if not self.uploaded_file.name.endswith(self.fileExtension.value):
            raise ValidationError(f'Only {self.fileExtension.value} files allowed.')

    def not_empty(self):
        if self.uploaded_file.size == 0:
            raise ValidationError('File is empty.')

    def base_file_validation(self, request):
        RequestValidation.content_type(request, self.requestType)
        RequestValidation.has_file_key(request, self.key_name)
        self.uploaded_file = request.FILES[self.key_name]
        self.MIME_type()
        self.extension()
        self.not_empty()
        return self.uploaded_file

    @abstractmethod
    def validate(self):
        pass