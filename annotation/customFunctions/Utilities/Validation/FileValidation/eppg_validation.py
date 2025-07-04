from annotation.customFunctions.Utilities.Validation.FileValidation.base_file_validation import BaseFileValidation
from annotation.customFunctions.Utilities.custom_exceptions import EppgFileInvalid


class EPPGValidation(BaseFileValidation):
    """
    Implements functions related to ePPG validation.
    """

    def __init__(self, request):
        super().__init__("EPPG")
        self.request = request

    @staticmethod
    def has_header(uploaded_file):
        """
        Validates whether the uploaded file has a header.
        Header should contain:
        1) The datetime in serial number format
        2) The names of the columns

        Raises:
            EppgFileInvalid: if file doesn't contain a valid header or valid records.
        """

        # Reset the file's pointer
        uploaded_file.seek(0)
        lines = []
        for _ in range(3):
            line = uploaded_file.readline()
            if not line:
                break
            lines.append(line.decode('utf-8').strip())

        if len(lines) < 3:
            raise EppgFileInvalid("ePPG file is too short.")

        # Check the first two lines for a header
        for line in lines[:1]:
            if not line.startswith("0"):
                try:
                    # Check whether the line contains the date/time in a number form
                    float(line.split("=")[1])
                except (IndexError, ValueError):
                    raise EppgFileInvalid("Valid header not found in the first two lines.")
            else:
                raise EppgFileInvalid("ePPG file doesn't contain required header.")

        # Check the third line for a valid record
        if not lines[2].startswith("0"):
            raise EppgFileInvalid("Your ePPG file doesn't contain valid records.")
        # Reset pointer of the file to start
        uploaded_file.seek(0)

    def validate(self):
        """
        Runs all validations for the ePPG file.
        """
        uploaded_file = self.base_file_validation(self.request)
        self.has_header(uploaded_file)
        return uploaded_file
