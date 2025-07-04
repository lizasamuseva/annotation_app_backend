from pyexpat import ExpatError

"""
Defines custom exceptions related to RML and ePPG file parsing and validation.
"""


class EPPGFileInvalid(Exception):
    """
    Raised when the uploaded ePPG file is invalid due to one of the following:
    1. Missing required header
    2. No records present
    3. Time mismatch of more than 8 hours with the RML file
    """

    def __init__(self, message):
        super().__init__(message)


class MissingRMLKeyError(KeyError):
    """Raised when a required key is missing in the parsed RML dictionary."""

    def __init__(self, key):
        super().__init__(f"RML file is unprocessable, because required key is missing: {key}")


class InvalidRMLStructure(ExpatError):
    """Raised when the structure of the RML file is invalid or cannot be parsed."""

    def __init__(self):
        super().__init__("RML file is invalid")


class SessionExpired(Exception):
    """Raised when the entity can't be found within session."""

    def __init__(self):
        super().__init__("Please start again, because last changes were too long.")
