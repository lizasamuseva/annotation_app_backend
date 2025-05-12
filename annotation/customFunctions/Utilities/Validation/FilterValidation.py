import logging

from rest_framework.exceptions import ValidationError

from annotation.customFunctions.Utilities.Constants.constants import CACHE_KEY_ALL_POSSIBLE_FILTERS

from django.core.cache import cache

logger = logging.getLogger(__name__)


class FilterValidation:
    @staticmethod
    def has_correct_format(filters_data, key_to_filters_in_json):
        required_filters = filters_data.get(key_to_filters_in_json)
        if not isinstance(required_filters, dict):
            raise ValidationError(f"Invalid or missing '{key_to_filters_in_json}' key. Expected a dictionary.")
        if not required_filters:
            raise ValidationError(f"Invalid filters: filters are empty.")
        return required_filters

    @staticmethod
    def are_filters_allowed(request, required_filters):
        all_filters = cache.get(request.session[CACHE_KEY_ALL_POSSIBLE_FILTERS])

        if not all_filters:
            raise ValidationError("Filter cache is empty or expired.")

        for key, required_values in required_filters.items():
            logger.error(f"Key: %s", key)
            logger.error(f"all_filters: %s", all_filters)
            if key not in all_filters:
                raise ValidationError(f"Unrecognizable filter category: {key}")
            if not set(required_values).issubset(set(all_filters[key])):
                raise ValidationError(
                    f"Invalid filters in category '{key}': {required_values} not in {all_filters[key]}"
                )