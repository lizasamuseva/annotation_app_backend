from annotation.helpers.utils.datetime_functions import DatetimeFunctions


class Event:
    """
    This class stores all information about node <Event>.
    """
    name: str = ""

    def __init__(self, event_info, rml_offset_time):
        """
        Initializes an Event instance using raw event metadata and an RML offset.
        - Generates an event name (annotation appendix).
        - Computes synchronized onset and end times using the RML offset and event duration.
        """
        self.create_event_name(event_info)
        self.non_synchronised_onset_time = event_info["@Start"]
        self.synchronised_onset_time = DatetimeFunctions.time_plus_timedelta(
            self.non_synchronised_onset_time, rml_offset_time)
        self.end_time = DatetimeFunctions.time_plus_timedelta(self.synchronised_onset_time, event_info["@Duration"])

    def create_event_name(self, event):
        """
        Generates a descriptive event name using "@Family", "@Type", and optionally "@EdfSignal" and other custom parameters.
        """

        self.name = event["@Family"] + ": " + event["@Type"]
        if "@EdfSignal" in event:
            self.name = self.name + " (" + event["@EdfSignal"] + ")"
        for parameter in event.keys():
            if "@" not in parameter:
                self.name = self.name + f"({parameter}: {event[parameter]})"
