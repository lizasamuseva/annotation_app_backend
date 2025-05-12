import logging

from annotation.customFunctions.Utilities.Validation.FileValidation.BaseFileValidation import BaseFileValidation
from annotation.customFunctions.customExceptions import EppgFileInvalid

logger = logging.getLogger(__name__)


class EPPGValidation(BaseFileValidation):
    def __init__(self, request):
        super().__init__("EPPG")
        self.request = request

    def has_header(self, uploaded_file):
        uploaded_file.seek(0)
        lines = []
        for _ in range(3):
            line = uploaded_file.readline()
            if not line:
                break
            lines.append(line.decode('utf-8').strip())

        if len(lines) < 3:
            raise EppgFileInvalid("EPPG file is too short.")
        logger.error(f"Lines: %s",
                     lines)

        # Check the first two lines for a header
        for line in lines[:1]:
            if not line.startswith("0"):
                try:
                    float(line.split("=")[1])
                except (IndexError, ValueError):
                    raise EppgFileInvalid("Valid header not found in the first two lines.")
            else:
                raise EppgFileInvalid("EPPG file doesn't contain required header.")

        # Check the third line for a valid record
        if not lines[2].startswith("0"):
            raise EppgFileInvalid("Your EPPG file doesn't contain valid records.")
        # Reset pointer of the file to start
        uploaded_file.seek(0)


    def validate(self):
        uploaded_file = self.base_file_validation(self.request)
        self.has_header(uploaded_file)
        return uploaded_file