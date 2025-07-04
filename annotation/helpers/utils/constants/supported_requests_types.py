from enum import Enum


class RequestContentType(Enum):
    """
    Supported HTTP request content types.
    """

    FILE = 'multipart/form-data'
    JSON = 'application/json'


class MIMETypes(Enum):
    """
    Expected MIME types for specific file uploads.
    """

    RML = 'application/octet-stream'
    EPPG = 'text/plain'


class FilesExtensions(Enum):
    """
    Allowed file extensions for supported file types.
    """

    RML = ".rml"
    EPPG = ".txt"
