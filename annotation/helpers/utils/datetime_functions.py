from datetime import datetime, timedelta

from annotation.helpers.Utilities.custom_exceptions import EppgFileInvalid


class DateTimeFunctions:
    """
       Utility class for handling date and time conversions/synchronization related to ePPG and PSG files time difference.
    """

    @staticmethod
    def convert_serial_number_to_date(serial_number_date):
        """
            Converts the date and time (in serial number) of the ePPG file into datetime format.
            Further information about serial numbers is described in the LabChart documentation
            https://www.adinstruments.com/support/knowledge-base/how-do-i-set-specific-start-time-and-date-imported-text-file
        """
        temp = datetime(1899, 12, 30)

        # Round to precision of 7 numbers after comma according to the Excel format
        rounded_serial_number = round(serial_number_date, 7)
        result = temp + timedelta(days=rounded_serial_number)

        # Round the microseconds (to seconds) according to the rounding rule
        if result.microsecond >= 1000000 / 2:
            result += timedelta(seconds=1)

        # Remove microseconds
        return result.replace(microsecond=0)

    @staticmethod
    def convert_datetime_from_rml(datetime_element):
        """
            Converts the recording start date/time from PSG file into datetime format
        """
        return datetime.strptime(datetime_element, "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime):
        """
            Compares the difference between PSG and ePPG start date/time recordings.
            Returns positive value, if PSG recording started earlier than ePPG recording
            Returns negative value, if ePPG started recording earlier
            EppgFileInvalid is raised, when the difference between file's times is more than 8 hours
        """
        maximum_possible_difference = timedelta(hours=8)
        difference_between_datetime = rml_datetime - ePPG_datetime
        if abs(difference_between_datetime) >= maximum_possible_difference:
            raise EppgFileInvalid("Review your files, they have the difference more than 8 hours.")
        return difference_between_datetime.total_seconds()

    @staticmethod
    def calculate_timedelta_plus_time_in_seconds(start, delta):
        """
            Adjusts the synchronisation time delta to the event time from ePPG/PSG.
            Outputs the synchronized time.

            Example:
                Input: start = 113, delta = 17.5
                Output: 130.500

            Time formats:
            1) Time should be float number with precision 3
            2) If the part after "." is 000, this part should be removed
        """
        new_time_with_offset = str(round(float(start) + float(delta), 3))

        if new_time_with_offset.split('.')[1] == "0":
            new_time_with_offset = new_time_with_offset.split(".")[0]
        return new_time_with_offset

    @staticmethod
    def convert_time_of_record_into_dict_form(time_of_record):
        """
            Converts a time record from ePPG into a dictionary form.

            Example:
                Input: "00:00:10.000"
                Output:
                {
                    "hours": "00",
                    "minutes": "00",
                    "seconds": "10",
                    "milliseconds": "000"
                }
        """
        time_of_record_splat_semicolon = time_of_record.split(":")
        time_of_record_splat_point = time_of_record_splat_semicolon[2].split(".")
        return dict({
            "hours": time_of_record_splat_semicolon[0],
            "minutes": time_of_record_splat_semicolon[1],
            "seconds": time_of_record_splat_point[0],
            "milliseconds": time_of_record_splat_point[1]
        })

    @staticmethod
    def convert_time_of_occasion_into_seconds(time):
        """
            This function converts the time of ePPG time record to seconds.
            This is useful for comparison of event's time between ePPG and PSG records.

            Example:
                Input: "00:00:10.000"
                Output: "10"
        """
        time_in_dict = DateTimeFunctions.convert_time_of_record_into_dict_form(time)

        time_in_seconds = str(round(float(time_in_dict["hours"]) * 3600 + float(time_in_dict["minutes"]) * 60 + float(
            time_in_dict["seconds"]) + float(time_in_dict["milliseconds"]) * 0.001, 3))

        # Remove 118.0 milliseconds part, because in PSG this is present as 118
        if time_in_seconds.split(".")[1] == "0":
            time_in_seconds = time_in_seconds.split(".")[0]
        return time_in_seconds
