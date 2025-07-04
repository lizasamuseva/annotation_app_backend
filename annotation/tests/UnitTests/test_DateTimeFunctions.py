import unittest
from datetime import datetime, timedelta

from annotation.customFunctions.Utilities.custom_exceptions import EppgFileInvalid
from annotation.customFunctions.Utilities.datetime_functions import DateTimeFunctions


class DateTimeTests(unittest.TestCase):
    def test_convert_serial_number_with_microseconds_DOWNROUND(self):
        """
        Operates with function convert_serial_number_to_date
        Checks whether the microseconds are rounded to the lower second
        Example:
        the date after conversion to datetime with microseconds part "2024-10-02 19:22:22.003600"
        the date after rounding of microseconds part should be: "2024-10-02 19:22:22.003600"
        """
        actual_result = DateTimeFunctions.convert_serial_number_to_date(40759.3542130)
        expected_result = datetime.strptime("2011-08-04T08:30:04", "%Y-%m-%dT%H:%M:%S")
        self.assertEqual(expected_result, actual_result)

    def test_convert_serial_number_with_microseconds_UPROUND(self):
        """
        Operates with function convert_serial_number_to_date
        Checks whether the microseconds are rounded to the upper second
        Example:
        the date after conversion to datetime with microseconds part "2024-10-02 19:22:22.995840"
        the date after rounding of microseconds part should be: "2024-10-02 19:22:23.995840"
        """
        actual_result = DateTimeFunctions.convert_serial_number_to_date(45567.8072106)
        expected_result = datetime.strptime("2024-10-02T19:22:23", "%Y-%m-%dT%H:%M:%S")
        self.assertEqual(expected_result, actual_result)

    """
    Next four tests check function compare_datetime_from_rml_and_ePPG on the results: neutral, positive, negative, and neutral values.
    """

    def test_compare_datetime_from_rml_and_ePPG_Equality(self):
        rml_datetime = datetime.strptime("2024-10-02T19:22:23", "%Y-%m-%dT%H:%M:%S")
        ePPG_datetime = DateTimeFunctions.convert_serial_number_to_date(45567.8072106)

        actual_result = DateTimeFunctions.compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime)
        expected_result = timedelta(0).total_seconds()

        self.assertEqual(expected_result, actual_result)

    def test_compare_datetime_from_rml_Later_and_ePPG_Earlier(self):
        rml_datetime = datetime.strptime("2024-10-02T19:22:24", "%Y-%m-%dT%H:%M:%S")
        ePPG_datetime = DateTimeFunctions.convert_serial_number_to_date(45567.8072106)

        actual_result = DateTimeFunctions.compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime)
        expected_result = timedelta(seconds=1).total_seconds()

        self.assertEqual(expected_result, actual_result)

    def test_compare_datetime_from_rml_Earlier_and_ePPG_Later(self):
        rml_datetime = datetime.strptime("2024-10-02T19:22:23", "%Y-%m-%dT%H:%M:%S")
        ePPG_datetime = DateTimeFunctions.convert_serial_number_to_date(45567.8072222)

        actual_result = DateTimeFunctions.compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime)
        expected_result = -timedelta(seconds=1).total_seconds()

        self.assertEqual(expected_result, actual_result)

    def test_compare_datetime_from_rml_and_ePPG_Exception(self):
        rml_datetime = datetime.strptime("2024-10-02T19:22:23", "%Y-%m-%dT%H:%M:%S")
        ePPG_datetime = DateTimeFunctions.convert_serial_number_to_date(45567.1405440)

        with self.assertRaises(EppgFileInvalid) as context:
            DateTimeFunctions.compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime)

        self.assertEqual(str(context.exception),
                         "Review your files, they have the difference more than 8 hours.")


if __name__ == '__main__':
    unittest.main()
