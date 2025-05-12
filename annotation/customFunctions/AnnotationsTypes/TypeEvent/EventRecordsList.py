from .Event import Event
import logging
logger = logging.getLogger(__name__)


# Implementation for list events_records
class EventRecordsList:
    def __init__(self, root, rml_offset_time, ePPG_offset_time, events_filters):
        self.events_records = root
        self.length_events_records = len(self.events_records)
        self.no_events_left_to_observe_from_file = False
        self.current_event_sequence_number = 0
        # The dictionary, which will contain all END events (in the form "END_TIME : EVENT_END_NAME")
        self.waiting_dictionary_with_end_event_times = dict()
        self.current_event = None
        self.__rml_offset_time = rml_offset_time
        self.filters = events_filters

        if self.skipEventsBeforeStartOfEPPG(ePPG_offset_time):
            # if self.skipUserEvents():
            if self.skipFilterOrientedEvents():
                self.array_START_events = []
                # Fill first events into the structures
                self.find_events_with_the_same_time_start()

    def is_waiting_dictionary_with_end_event_times_empty(self):
        return not self.waiting_dictionary_with_end_event_times

    def increase_events_and_check_the_end(self):
        self.current_event_sequence_number += 1
        if self.length_events_records == self.current_event_sequence_number:
            self.no_events_left_to_observe_from_file = True
            return False
        return True

    def create_new_event(self):
        self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)

    def skipUserEvents(self):
        while self.events_records[self.current_event_sequence_number]["@Family"] == "User":
        #     if not self.increase_events_and_check_the_end():
        #         return False
        # self.create_new_event()
            self.current_event_sequence_number += 1
            if self.length_events_records == self.current_event_sequence_number:
                self.no_events_left_to_observe_from_file = True
                return False
        self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)
        return True

    def skipEventsBeforeStartOfEPPG(self, ePPG_offset_time):
        while float(self.events_records[self.current_event_sequence_number]["@Start"]) < ePPG_offset_time:
        #     if not self.increase_events_and_check_the_end():
        #         return False
        # self.create_new_event()
            self.current_event_sequence_number += 1
            if self.length_events_records == self.current_event_sequence_number:
                self.no_events_left_to_observe_from_file = True
                return False
        self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)
        return True

    def skipFilterOrientedEvents(self):
        family = self.events_records[self.current_event_sequence_number]["@Family"]
        type = self.events_records[self.current_event_sequence_number]["@Type"]
        while (family not in self.filters) or (type not in self.filters.get(family, [])):
            # if not self.increase_events_and_check_the_end():
            #     return False
            self.current_event_sequence_number += 1
            if self.length_events_records == self.current_event_sequence_number:
                self.no_events_left_to_observe_from_file = True
                return False
            family = self.events_records[self.current_event_sequence_number]["@Family"]
            type = self.events_records[self.current_event_sequence_number]["@Type"]
        self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)

        # self.create_new_event()
        return True


    # Different events can occur at the same time (for example Cardio: tachycardia and Nasal: snore)
    # Therefore, this function finds such events and returns them as an array
    # Also, returns the next event number
    # Of note, the same type of event can't start before it will end (for instance Cardio: tachycardia and Cardio: tachycardia)
    def find_events_with_the_same_time_start(self):
        # Update both dictionary with end events and array with first values
        self.update_START_events_array()
        self.update_end_events_waiting_dictionary()

        # Find the events with the same start time as the first one
        self.current_event_sequence_number += 1
        while (
            self.length_events_records > self.current_event_sequence_number and
            self.events_records[self.current_event_sequence_number]["@Start"] == self.current_event.getNonSynchronisedOnsetTime()
        ):
            if self.events_records[self.current_event_sequence_number]["@Family"] == "User":
                self.current_event_sequence_number += 1
                continue
            family = self.events_records[self.current_event_sequence_number]["@Family"]
            type = self.events_records[self.current_event_sequence_number]["@Type"]
            if family not in self.filters and type not in self.filters[family]:
                self.current_event_sequence_number += 1
                continue


            self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)

            self.update_START_events_array()
            self.update_end_events_waiting_dictionary()

            self.current_event_sequence_number += 1


    #----------------------------------------Updating methods---------------------------------------------------------
    def update_START_events_array(self):
        # Add first event start name into the array
        self.array_START_events.append("Start " + self.current_event.getName())

    # Update the waiting dictionary with pair "event_end_time : event_name_END"
    def update_end_events_waiting_dictionary(self):
        end_time = self.current_event.getEndTime()
        end_name = "End " + self.current_event.getName()


        # 1.Whether such time is already in the dictionary with one event associated => associate the list of events with that time
        if (end_time in self.waiting_dictionary_with_end_event_times.keys() and
                not isinstance(self.waiting_dictionary_with_end_event_times[end_time], list)):

            self.waiting_dictionary_with_end_event_times[end_time] = self.make_list_instance(self.waiting_dictionary_with_end_event_times[end_time])
            self.waiting_dictionary_with_end_event_times[end_time].append(end_name)

        # 2.Whether such time is already in the dictionary with list of events associated => add this event into the list
        elif (end_time in self.waiting_dictionary_with_end_event_times.keys() and
              isinstance(self.waiting_dictionary_with_end_event_times[end_time], list)):

            self.waiting_dictionary_with_end_event_times[end_time].append(end_name)

        # 3.Whether there is no such pair => add this pair
        else:
            self.waiting_dictionary_with_end_event_times.update({end_time: end_name})

    # Transform one element into the list with that element
    def make_list_instance(self, element_to_transform):
        new_list_element = list()
        new_list_element.append(element_to_transform)
        return new_list_element

    # ----------------------------------------Writing methods into the file---------------------------------------------------------

    # Write the current start events into the file
    # Update the start events with the new one
    def write_START_events_into_comment_line(self, line_time_in_seconds, string_comment):
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
                self.current_event = Event(self.events_records[self.current_event_sequence_number], self.__rml_offset_time)
                # Skip "User" events
                #self.skipUserEvents()
                if self.skipFilterOrientedEvents():
                    self.find_events_with_the_same_time_start()
            else:
                self.no_events_left_to_observe_from_file = True

        return string_comment

    def check_if_write_START_events_is_possible(self, line_time_in_seconds):
        if not self.no_events_left_to_observe_from_file and self.current_event.getSynchronisedOnsetTime() == line_time_in_seconds:
            return True
        return False


    def write_END_events_into_comment_line(self, line_time_in_seconds, string_comment):
        if line_time_in_seconds in self.waiting_dictionary_with_end_event_times.keys():
            string_comment = string_comment.split("\n")[0]
            end_events_to_write = self.waiting_dictionary_with_end_event_times[line_time_in_seconds]

            if isinstance(end_events_to_write, list):
                for end_event_name in end_events_to_write:
                    string_comment = string_comment + "\t#* " + end_event_name
            else:
                string_comment = string_comment + "\t#* " + end_events_to_write
            string_comment = string_comment + "\n"

            self.waiting_dictionary_with_end_event_times.pop(line_time_in_seconds)

        return string_comment