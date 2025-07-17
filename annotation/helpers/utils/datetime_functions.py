from datetime import datetime, timedelta

from annotation.helpers.utils.custom_exceptions import EPPGFileInvalid


class DatetimeFunctions:
    """
    Utility class for handling date and time conversions/synchronization related to ePPG and PSG files time difference.
    """

    @staticmethod
    def parse_excel(serial_number_date: int | float):
        """
        Converts the datetime (in Excel format) of the ePPG file into datetime format.
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
    def parse_rml(datetime_element: str):
        """
        Converts the recording start datetime from PSG file into datetime format
        """

        return datetime.strptime(datetime_element, "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def compare_datetime(rml_datetime: datetime, eppg_datetime: datetime):
        """
        Compares the difference between PSG and ePPG start datetime recordings.
        Returns positive value, if PSG recording started earlier than ePPG recording
        Returns negative value, if ePPG started recording earlier
        EPPGFileInvalid is raised, when the difference between file's times is more than 8 hours
        """

        maximum_possible_difference = timedelta(hours=8)
        difference_between_datetime = rml_datetime - eppg_datetime
        if abs(difference_between_datetime) >= maximum_possible_difference:
            raise EPPGFileInvalid("Review your files, they have the difference more than 8 hours.")
        return difference_between_datetime.total_seconds()

    @staticmethod
    def time_plus_timedelta(start: int | float, delta: int | float | timedelta):
        """
        Adjusts the synchronization time delta to the event time from ePPG/PSG.
        Outputs the synchronized time.

        Example:
            Input: start = 113, delta = 17.5
            Output: 130.500

        Time formats:
        1) Time should be float number with precision 3
        2) If the part after "." is 000, this part should be removed
        """

        new_time_with_offset = str(round(float(start) + float(delta), 3))
        if new_time_with_offset.split(".")[1] == "0":
            new_time_with_offset = new_time_with_offset.split(".")[0]
        return new_time_with_offset

    @staticmethod
    def as_dict(time_of_record: str):
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
    def as_seconds(time: str):
        """
        This function converts the time of ePPG time record to seconds.
        This is useful for comparison of event's time between ePPG and PSG records.

        Example:
            Input: "00:00:10.000"
            Output: "10"
        """

        time_in_dict = DatetimeFunctions.as_dict(time)
        time_in_seconds = str(round(
            float(time_in_dict["hours"]) * 60 * 60 + float(time_in_dict["minutes"]) * 60 +
            float(time_in_dict["seconds"]) + float(time_in_dict["milliseconds"]) * 0.001,
            3))

        # Remove 118.0 milliseconds part, because in PSG this is present as 118
        if time_in_seconds.split(".")[1] == "0":
            time_in_seconds = time_in_seconds.split(".")[0]
        return time_in_seconds
