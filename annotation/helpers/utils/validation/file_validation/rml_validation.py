from annotation.helpers.utils.validation.file_validation.base_file_validation import BaseFileValidation


class RMLValidation(BaseFileValidation):
    """
    Class validation for PSG files.
    """

    def __init__(self, request):
        super().__init__("RML")
        self.request = request

    def validate(self):
        return self.base_file_validation(self.request)
