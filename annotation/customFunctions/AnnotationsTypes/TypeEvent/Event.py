from annotation.customFunctions.Utilities.DateTimeFunctions import DateTimeUtilities

class Event:
    def __init__(self, event_info, rml_offset_time):
        self.__create_event_name(event_info)
        self.__non_synchronised_onset_time = event_info["@Start"]
        self.__synchronised_onset_time = DateTimeUtilities.calculate_timedelta_plus_time_in_seconds(self.__non_synchronised_onset_time, rml_offset_time)
        self.__end_time = DateTimeUtilities.calculate_timedelta_plus_time_in_seconds(self.__synchronised_onset_time, event_info["@Duration"])

    # Create the comment name structure
    def __create_event_name(self, event):
        self.__name = event['@Family'] + ": " + event['@Type']
        if "@EdfSignal" in event:
            self.__name = self.__name + " (" + event['@EdfSignal'] + ")"
        for parameter in event.keys():
            if "@" not in parameter:
                self.__name = self.__name + f'({parameter}: {event[parameter]})'


    def getName(self):
        return self.__name
    def getSynchronisedOnsetTime(self):
        return self.__synchronised_onset_time
    def getNonSynchronisedOnsetTime(self):
        return self.__non_synchronised_onset_time
    def getEndTime(self):
        return self.__end_time