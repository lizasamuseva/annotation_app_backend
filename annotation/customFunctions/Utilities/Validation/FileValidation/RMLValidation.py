from annotation.customFunctions.Utilities.Validation.FileValidation.BaseFileValidation import BaseFileValidation


class RMLValidation(BaseFileValidation):
    def __init__(self, request):
        super().__init__("RML")
        self.request = request

    def validate(self):
        uploaded_file = self.base_file_validation(self.request)
        return uploaded_file