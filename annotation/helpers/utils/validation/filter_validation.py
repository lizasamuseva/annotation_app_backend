from rest_framework.exceptions import ValidationError

from annotation.helpers.utils.constants.constants import CACHE_KEY_ALL_POSSIBLE_FILTERS
from annotation.helpers.utils.file_manager import FileManager


class FilterValidation:
    """
    validation of the client's filters request.
    """

    @staticmethod
    def has_correct_format(filters_data, key_to_filters_in_json):
        """
            Check if the requested filters are in the correct dictionary format.

            Raises:
                ValidationError: If the key is missing, not a dictionary, or is empty.
        """
        required_filters = filters_data.get(key_to_filters_in_json)
        if not isinstance(required_filters, dict):
            raise ValidationError(f"Invalid or missing '{key_to_filters_in_json}' key. Expected a dictionary.")
        if not required_filters:
            raise ValidationError(f"Invalid filters: filters are empty.")
        return required_filters

    @staticmethod
    def are_filters_allowed(request, required_filters):
        """
            Verifies that the client requested valid filters.
            Raises:
                ValidationError: if filter or its category is unrecognizable.
        """
        all_filters = FileManager.get_entity_from_cache(request, CACHE_KEY_ALL_POSSIBLE_FILTERS)

        if not all_filters:
            raise ValidationError("Filter cache is empty or expired.")

        for key, required_values in required_filters.items():
            if key not in all_filters:
                raise ValidationError(f"Unrecognizable filter category: {key}")
            if not set(required_values).issubset(set(all_filters[key])):
                invalid_values = set(required_values) - set(all_filters[key])
                raise ValidationError(
                    f"Invalid filters in category '{key}': {list(invalid_values)} not in {all_filters[key]}")
