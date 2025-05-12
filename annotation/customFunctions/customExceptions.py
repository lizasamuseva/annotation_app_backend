from pyexpat import ExpatError


class EppgFileInvalid(Exception):
    def __init__(self, message):
        super().__init__(message)

class MissingRMLKeyError(KeyError):
    def __init__(self, key):
        super().__init__(f'RML file is unprocessable, because required key is missing: {key}')

class InvalidRMLStructure(ExpatError):
    def __init__(self):
        super().__init__('RML file is invalid')
