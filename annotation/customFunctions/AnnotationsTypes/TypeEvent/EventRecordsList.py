from .Event import Event

class EventRecordsList:
    """
    Represents a list of <Event> nodes with metadata and filtering.

    Handles:
    - Tracking of current event position and sequence
    - Skipping events based on recording start time and filter criteria
    - Storing start and end event annotations for time-aligned processing

    Attributes:
    - events_records: List of event dictionaries
    - waiting_dictionary_with_end_event_times: {end_time: [event_names]}
    - current_event: The currently active Event instance
    - array_START_events: Events that started at the same timestamp
    """
    def __init__(self, root, rml_offset_time, ePPG_offset_time, events_filters):
        self.events_records = root
        self.length_events_records = len(self.events_records)
        self.no_events_left_to_observe_from_file = False
        self.current_event_sequence_number = 0
        self.waiting_dictionary_with_end_event_times = dict()
        self.current_event = None
        self.rml_offset_time = rml_offset_time
        self.filters = events_filters

        # Skip all unwanted events and initialize the working one
        if self.skip_events_before_start_of_ePPG(ePPG_offset_time):
            if self.skip_filter_oriented_events():
                # Initialize the new event to proceed further
                self.current_event = Event(self.events_records[self.current_event_sequence_number],self.rml_offset_time)
                self.array_START_events = []
                # Find the further events
                self.find_events_with_the_same_time_start()

    # def increase_events_and_check_the_end(self):
    #     self.current_event_sequence_number += 1
    #     if self.length_events_records == self.current_event_sequence_number:
    #         self.no_events_left_to_observe_from_file = True
    #         return False
    #     return True
    #
    # def create_new_event(self):
    #     self.current_event = Event(self.events_records[self.current_event_sequence_number], self.rml_offset_time)

    def skip_events_before_start_of_ePPG(self, ePPG_offset_time):
        """
        Skips events that started before the ePPG offset time.
        """
        while float(self.events_records[self.current_event_sequence_number]["@Start"]) < ePPG_offset_time:
            self.current_event_sequence_number += 1
            if self.length_events_records == self.current_event_sequence_number:
                self.no_events_left_to_observe_from_file = True
                return False
        # # Initialize the new event to proceed further
        # self.current_event = Event(self.events_records[self.current_event_sequence_number], self.rml_offset_time)
        return True

    def skip_filter_oriented_events(self):
        """
        Skips events that do not match the provided filter criteria.
        """

        family = self.events_records[self.current_event_sequence_number]["@Family"]
        type = self.events_records[self.current_event_sequence_number]["@Type"]
        while (family not in self.filters) or (type not in self.filters.get(family, [])):
            self.current_event_sequence_number += 1
            if self.length_events_records == self.current_event_sequence_number:
                self.no_events_left_to_observe_from_file = True
                return False

            family = self.events_records[self.current_event_sequence_number]["@Family"]
            type = self.events_records[self.current_event_sequence_number]["@Type"]
        # self.current_event = Event(self.events_records[self.current_event_sequence_number], self.rml_offset_time)
        return True

    def find_events_with_the_same_time_start(self):
        """
        Finds and stores events that start at the same time as the current event.
        Updates START events array and waiting dictionary accordingly.
        """
        # Initialize both array_START_events and waiting_dictionary_with_end_event_times with first values
        self.update_START_events_array()
        self.update_end_events_waiting_dictionary()

        # Find the events, which have the same START time as the already filled one
        self.current_event_sequence_number += 1
        while (
            self.length_events_records > self.current_event_sequence_number and
            self.events_records[self.current_event_sequence_number]["@Start"] == self.current_event.non_synchronised_onset_time
        ):

            # Skip if the event wasn't requested in the filters
            family = self.events_records[self.current_event_sequence_number]["@Family"]
            type = self.events_records[self.current_event_sequence_number]["@Type"]
            if family not in self.filters and type not in self.filters[family]:
                self.current_event_sequence_number += 1
                continue
            # When the event was found, create a new Event
            self.current_event = Event(self.events_records[self.current_event_sequence_number], self.rml_offset_time)

            # Add to the structures (array_START and waiting_dictionary) with the new Event
            self.update_START_events_array()
            self.update_end_events_waiting_dictionary()

            # Set pointer to the next <Event>
            self.current_event_sequence_number += 1


    #----------------------------------------Updating methods---------------------------------------------------------
    def update_START_events_array(self):
        """
        Fills the array_START_events with the start annotations' names.
        """
        self.array_START_events.append("Start " + self.current_event.name)

    def update_end_events_waiting_dictionary(self):
        """
        Fills the waiting dictionary with pair {event_end_time : event_name_END}.
        """
        end_time = self.current_event.end_time
        end_name = "End " + self.current_event.name

        existing = self.waiting_dictionary_with_end_event_times.get(end_time)

        if existing is None:
            # Is empty, add event
            self.waiting_dictionary_with_end_event_times[end_time] = end_name
        elif isinstance(existing, list):
            # Append to the existing list of events
            existing.append(end_name)
        else:
            # Convert single element to list and append the new name
            self.waiting_dictionary_with_end_event_times[end_time] = [existing, end_name]

        # # 1. Whether such time is already in the dictionary with one event associated => associate the list of events with that time
        # if (end_time in self.waiting_dictionary_with_end_event_times.keys() and
        #         not isinstance(self.waiting_dictionary_with_end_event_times[end_time], list)):
        #
        #     self.waiting_dictionary_with_end_event_times[end_time] = self.make_list_instance(self.waiting_dictionary_with_end_event_times[end_time])
        #     self.waiting_dictionary_with_end_event_times[end_time].append(end_name)
        #
        # # 2. Whether such time is already in the dictionary with list of events associated => add this event into the list
        # elif (end_time in self.waiting_dictionary_with_end_event_times.keys() and
        #       isinstance(self.waiting_dictionary_with_end_event_times[end_time], list)):
        #
        #     self.waiting_dictionary_with_end_event_times[end_time].append(end_name)
        #
        # # 3. Whether there is no such pair => add this pair
        # else:
        #     self.waiting_dictionary_with_end_event_times.update({end_time: end_name})

    def make_list_instance(self, element):
        """
        Transforms one element into the list with that element.
        """
        # new_list_element = list()
        # new_list_element.append(element_to_transform)
        # return new_list_element
        return [element]

    # ----------------------------------------Writing methods into the file---------------------------------------------------------

    def write_START_events_into_comment_line(self, line_time_in_seconds, string_comment):
        """
        After the checking whether the writing of the annotation appendix is possible, append the annotations to the line from ePPG.
        Initializes the further events to process.
        Returns either the annotated or raw string.
        """
        if self.check_if_write_START_events_is_possible(line_time_in_seconds):
            string_comment = string_comment.split("\n")[0]

            # Append all OLD events to the comment, which starts at the same start time
            for event_name in self.array_START_events:
                string_comment = string_comment + "\t#* " + event_name
            string_comment = string_comment + "\n"
            # Clear the array for the next START events
            self.array_START_events = []

            # Find NEW events to review, ONLY if they didn't run out of
            if self.length_events_records > self.current_event_sequence_number:
                self.current_event = Event(self.events_records[self.current_event_sequence_number], self.rml_offset_time)
                # Skip the non-requested events
                if self.skip_filter_oriented_events():
                    self.find_events_with_the_same_time_start()
            else:
                self.no_events_left_to_observe_from_file = True

        return string_comment

    def check_if_write_START_events_is_possible(self, line_time_in_seconds):
        """
        Checks whether the Events did not run out of during the previous write_START_events_into_comment_line.
        Checks whether the line_time_in_seconds from the ePPG is the same as the synchronized time of the START Events.
        """
        if not self.no_events_left_to_observe_from_file and self.current_event.synchronised_onset_time == line_time_in_seconds:
            return True
        return False


    def write_END_events_into_comment_line(self, line_time_in_seconds, string_comment):
        """
        Retrieves the END events associated with current time from ePPG and writes them to the comment line.
        Returns either the annotated or raw string.
        """
        if line_time_in_seconds in self.waiting_dictionary_with_end_event_times.keys():
            string_comment = string_comment.split("\n")[0]
            end_events_to_write = self.waiting_dictionary_with_end_event_times[line_time_in_seconds]

            # Append annotations according to the structure associated with the time key
            if isinstance(end_events_to_write, list):
                for end_event_name in end_events_to_write:
                    string_comment = string_comment + "\t#* " + end_event_name
            else:
                string_comment = string_comment + "\t#* " + end_events_to_write
            string_comment = string_comment + "\n"

            # Delete the commented events
            self.waiting_dictionary_with_end_event_times.pop(line_time_in_seconds)

        return string_comment