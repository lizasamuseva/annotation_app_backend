from enum import Enum

class RequestContentType(Enum):
    FILE = 'multipart/form-data'
    JSON = 'application/json'

class MIMETypes(Enum):
    RML = 'application/octet-stream'
    EPPG = 'text/plain'

class FilesExtensions(Enum):
    RML = ".rml"
    EPPG = ".txt"

