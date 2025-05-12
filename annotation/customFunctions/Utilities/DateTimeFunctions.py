from datetime import datetime, timedelta

class DateTimeUtilities:
    # Converts the date and time (in serial number) of the ePPG file into datetime format
    # Further information about serial numbers is described in the LabChart documentation
    # https://www.adinstruments.com/support/knowledge-base/how-do-i-set-specific-start-time-and-date-imported-text-file
    @staticmethod
    def convert_serial_number_to_date(serial_number_date):
        temp = datetime(1899, 12, 30)

        # Round to precision of 7 numbers after comma according to the excel
        rounded_serial_number = round(serial_number_date, 7)
        result = temp + timedelta(days=rounded_serial_number)

        # Round the microseconds (to seconds) according to the rounding rule
        if result.microsecond >= 1000000/2:
            result += timedelta(seconds=1)

        # Afterwords, remove microseconds
        return result.replace(microsecond=0)

    @staticmethod
    def convert_datetime_from_rml(datetime_element):
        return datetime.strptime(datetime_element,"%Y-%m-%dT%H:%M:%S")

    # Compares the difference between RML date/time recording and ePPG date/time recording
    # Returns positive value, if RML recording started earlier than ePPG recording
    # Otherwise, returns negative value (ePPG recorded earlier)
    # EXCEPTION is raised, when the difference is more than 8 hours
    @staticmethod
    def compare_datetime_from_rml_and_ePPG(rml_datetime, ePPG_datetime):
        maximum_possible_difference = timedelta(hours=8)
        difference_between_datetime = rml_datetime - ePPG_datetime
        if abs(difference_between_datetime) >= maximum_possible_difference:
            raise Exception("Mistake: review your files, they have the difference more than 8 hours.")
        return difference_between_datetime.total_seconds()

    @staticmethod
    def calculate_timedelta_plus_time_in_seconds(start, delta):
        # Apply round(number, 3) to make sure that time will calculated exactly with precision 3
        new_time_with_offset= str(round(float(start) + float(delta), 3))
        # IMPORTANT: Don't forget to take number in such form as "118" instead of "118.0"
        if new_time_with_offset.split('.')[1] == "0":
             new_time_with_offset = new_time_with_offset.split(".")[0]
        return new_time_with_offset

    @staticmethod
    def convert_time_of_record_into_dict_form(time_of_record):
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
        time_in_dict = DateTimeUtilities.convert_time_of_record_into_dict_form(time)
        time_in_seconds = str(round(float(time_in_dict["hours"]) * 3600 + float(time_in_dict["minutes"]) * 60 + float(
            time_in_dict["seconds"]) + float(time_in_dict["milliseconds"]) * 0.001, 3))
        if time_in_seconds.split(".")[1] == "0":
            time_in_seconds = time_in_seconds.split(".")[0]
        return time_in_seconds