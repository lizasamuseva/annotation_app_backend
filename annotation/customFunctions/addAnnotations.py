import sys
import traceback

from .additionalFunctions import *
from .customExceptions import *
from annotation.customFunctions.Parsers.parserFromRML import parse_RML_to_Dict

# # Create the comment name structure
# def create_event_name(event):
#     event_name = event['@Family'] + ": " + event['@Type']
#     if "@EdfSignal" in event:
#         event_name = event_name + " (" + event['@EdfSignal'] + ")"
#     for parameter in event.keys():
#         if "@" not in parameter:
#             event_name = event_name + f'({parameter}: {event[parameter]})'
#
#     return event_name
#
# # Transform one element into the list with that element
# def make_list_instance(element_to_transform):
#     new_list_element = list()
#     new_list_element.append(element_to_transform)
#     return new_list_element
#
# # Update the waiting dictionary with pair "event_end_time : event_name_END"
# def update_waiting_dictionary(current_event_end_time, waiting_dictionary_with_end_event_times, current_event_name_END):
#     # Whether such time is already in the dictionary with one event associated => associate the list of events with that time
#     if (current_event_end_time in waiting_dictionary_with_end_event_times.keys() and
#             not isinstance(waiting_dictionary_with_end_event_times[current_event_end_time], list)):
#         waiting_dictionary_with_end_event_times[current_event_end_time] = make_list_instance(
#             waiting_dictionary_with_end_event_times[current_event_end_time])
#         waiting_dictionary_with_end_event_times[current_event_end_time].append(current_event_name_END)
#     # Whether such time is already in the dictionary with list of events associated => add this event into the list
#     elif (current_event_end_time in waiting_dictionary_with_end_event_times.keys() and
#           isinstance(waiting_dictionary_with_end_event_times[current_event_end_time], list)):
#         waiting_dictionary_with_end_event_times[current_event_end_time].append(current_event_name_END)
#     # Whether there is no such pair => add this pair
#     else:
#         waiting_dictionary_with_end_event_times.update({current_event_end_time: current_event_name_END})
#
# def update_start_events_array(event_name, events_with_the_same_start_time):
#     # Add first event start name into the array
#     event_name_START = "Start " + event_name
#     events_with_the_same_start_time.append(event_name_START)
#
# def update_end_events_waiting_dictionary(event_start_time, event_name, event_duration, waiting_dictionary_with_end_event_times):
#     # Calculate the end time
#     # Apply round(number, 3) to make sure that time will calculated exactly with precision 3
#     event_end_time = str(round(float(event_start_time) + float(event_duration), 3))
#     # IMPORTANT: Don't forget to take number in such form as "118" instead of "118.0"
#     if event_end_time.split(".")[1] == "0":
#         event_end_time = event_end_time.split(".")[0]
#     event_name_END = "End " + event_name
#     # Further add the structure "time_of_end_event : event_name_END" into the waiting dictionary
#     update_waiting_dictionary(event_end_time, waiting_dictionary_with_end_event_times, event_name_END)
#
#
#
# # Different events can occur at the same time (for example Cardio: tachycardia and Nasal: snore)
# # Therefore, this function finds such events and returns them as an array
# # Also, returns the next event number
# # Of note, the same type of event can't start before it will end (for instance Cardio: tachycardia and Cardio: tachycardia)
# def find_events_with_the_same_time_start(events_records, current_event_number, waiting_dictionary_with_end_event_times):
#     events_with_the_same_start_time = list()
#     start_time = events_records[current_event_number]["@Start"]
#     current_event_name = create_event_name(events_records[current_event_number])
#
#     # Update both dictionary with end events and array with start events
#     update_start_events_array(current_event_name, events_with_the_same_start_time)
#     update_end_events_waiting_dictionary(start_time, current_event_name, events_records[current_event_number]["@Duration"], waiting_dictionary_with_end_event_times)
#
#     # Find the events with the same start time as the first one
#     current_event_number = current_event_number + 1
#     while len(events_records) > current_event_number and events_records[current_event_number]["@Start"] == start_time:
#         if events_records[current_event_number]["@Family"] == "User":
#             current_event_number = current_event_number + 1
#             continue
#
#         current_event_name = create_event_name(events_records[current_event_number])
#
#         update_start_events_array(current_event_name, events_with_the_same_start_time)
#         update_end_events_waiting_dictionary(start_time, current_event_name,
#                                              events_records[current_event_number]["@Duration"],
#                                              waiting_dictionary_with_end_event_times)
#
#         current_event_number = current_event_number + 1
#     return events_with_the_same_start_time, current_event_number
#
# # Write the current start events into the file
# # Update the start events with the new one
# def write_START_events_into_comment_line(events_records, string_comment, no_events_left_to_observe_from_file, events_list_with_the_same_time, waiting_dictionary_with_end_event_times, current_event_number):
#     string_comment = string_comment.split("\n")[0]
#
#     # Append all OLD events to the comment, which starts at the same start time
#     for event_name in events_list_with_the_same_time:
#         string_comment = string_comment + "\t#* " + event_name
#     string_comment = string_comment + "\n"
#
#     # Find the NEW events to review, ONLY if they didn't run out of
#     if len(events_records) > current_event_number:
#         # Skip "User" events
#         while events_records[current_event_number]["@Family"] == "User":
#             current_event_number = current_event_number + 1
#             if len(events_records) == current_event_number:
#                 no_events_left_to_observe_from_file = True
#                 break
#         if not no_events_left_to_observe_from_file:
#             events_list_with_the_same_time, current_event_number = find_events_with_the_same_time_start(events_records, current_event_number, waiting_dictionary_with_end_event_times)
#     else:
#         no_events_left_to_observe_from_file = True
#     return string_comment, no_events_left_to_observe_from_file, current_event_number, events_list_with_the_same_time
#
#
# def write_END_events_into_comment_line(line_time_in_seconds, waiting_dictionary_with_end_event_times, string_comment):
#     if line_time_in_seconds in waiting_dictionary_with_end_event_times.keys():
#         string_comment = string_comment.split("\n")[0]
#         end_events_to_write = waiting_dictionary_with_end_event_times[line_time_in_seconds]
#
#         if isinstance(end_events_to_write, list):
#             for end_event_name in end_events_to_write:
#                 string_comment = string_comment + "\t#* " + end_event_name
#         else:
#             string_comment = string_comment + "\t#* " + end_events_to_write
#
#         waiting_dictionary_with_end_event_times.pop(line_time_in_seconds)
#         string_comment = string_comment + "\n"
#     return string_comment

# def write_SLEEP_STAGES_into_comments(line_time_in_seconds, sleep_stages_records, current_number_of_sleep_stage_record, string_comment):
#     current_sleep_stage_time = sleep_stages_records[current_number_of_sleep_stage_record]["@Start"]
#     if line_time_in_seconds == current_sleep_stage_time:
#         string_comment = string_comment.split("\n")[0] + "\t#* " + sleep_stages_records[current_number_of_sleep_stage_record]["@Type"] + "\n"
#         current_number_of_sleep_stage_record = current_number_of_sleep_stage_record + 1
#     return current_number_of_sleep_stage_record, string_comment

# # The Continuous structure means the structure from RML file, which has @Start property and not @End property
# # Ending time is defined with the start of the next element
# # Examples, Sleep Stages and Body Position
# # Attention, the function is for root, which is list
# def write_CONTINUOUS_LIST_STRUCTURE_into_comments(line_time_in_seconds, root, current_number_of_element, element_property, element_group, string_comment):
#     current_element_time = root[current_number_of_element]["@Start"]
#     if line_time_in_seconds == current_element_time:
#         string_comment = f"{string_comment.split("\n")[0]}\t#* {element_group}: {element_property}\n"
#         current_number_of_element = current_number_of_element + 1
#     return current_number_of_element, string_comment
#
# # Attention, the function is for root, which is not list
# def write_CONTINUOUS_NOT_LIST_STRUCTURE_into_comments(line_time_in_seconds, element, element_property, element_group, string_comment):
#     if convert_time_of_occasion_into_seconds(line_time_in_seconds) == element["@Start"]:
#         string_comment = f'{string_comment.split("\n")[0]}\t#* {element_group}: {element_property}\n'
#         return string_comment
#     return False


# The function takes the recorded events information (except type="User") from the polysomnography RML file
# And adds them like the comments into the source file of ePPG =>
# The resulting file path is defined in ePPG_out_file_path
def add_annotations(polysomnography_file_src_path, ePPG_file_src_path, ePPG_out_file_path):
    # Create output directory, if such doesn't exist
    ePPG_output = open_output_file(ePPG_out_file_path)

    #Get events information from RML file
    root = parse_RML_to_Dict(polysomnography_file_src_path)
    events_records = root['PatientStudy']['ScoringData']['Events']['Event']
    sleep_stages_records = root['PatientStudy']['ScoringData']['StagingData']['UserStaging']['NeuroAdultAASMStaging']['Stage']
    body_position_states_records = root['PatientStudy']['BodyPositionState']['BodyPositionItem']

    #Go through each element in roots records
    current_number_of_event_record = 0
    current_number_of_sleep_stage_record = 0
    current_number_of_body_position_state = 0

    # Are there left new events (in the source file), which should be observed?
    no_events_left_to_observe_from_file = False

    # If the source has 1 sleep stage/body position state, was it recorded?
    sleep_stage_is_recorded = False
    body_position_state_is_recorded = False

    # TODO:// initialize the structure (create a function initializer)
    # #Don't record User events
    # if isinstance(events_records, list):
    #     while events_records[current_number_of_event_record]["@Family"] == "User":
    #         current_number_of_event_record = current_number_of_event_record + 1
    #         if len(events_records) == current_number_of_event_record:
    #             no_events_left_to_observe_from_file = True
    #             break

    # # The dictionary, which will contain all END events (in the form "END_TIME : EVENT_END_NAME")
    # waiting_dictionary_with_end_event_times = dict()
    #
    # # Initialization of structures for START events and END events
    # # Events with the same start time will be saved as the list, which will renew with each new start time
    # if isinstance(events_records, list) and not no_events_left_to_observe_from_file:
    #     current_event_start_time = events_records[current_number_of_event_record]["@Start"]
    #     # Fill first events into the structures
    #     events_list_with_the_same_time, current_number_of_event_record = find_events_with_the_same_time_start(events_records, current_number_of_event_record, waiting_dictionary_with_end_event_times)
    with (open(ePPG_file_src_path, 'r') as ePPG_source_file):
        lines = ePPG_source_file.readlines()
        i = 0
        try:
            # Write header to the output file
            # The first record will always start from "00:00:00.000"
            while lines[i][0] != "0":
                ePPG_output.write(lines[i])
                i = i + 1
            if i == 0:
                raise HeaderDoesNotPresentInSourceFile()

            for line in lines[i:]:
                line_time = line.split("\t")[0]
                string_comment = line

                # DONE//
                # # 1. Write the START events
                # # IMPORTANT: current_event_start_time must be in seconds in string form
                # if isinstance(events_records, list) and not no_events_left_to_observe_from_file and current_event_start_time == convert_time_of_occasion_into_seconds(line_time):
                #     string_comment, no_events_left_to_observe_from_file, current_number_of_event_record, events_list_with_the_same_time = write_START_events_into_comment_line(
                #         events_records, string_comment, no_events_left_to_observe_from_file, events_list_with_the_same_time, waiting_dictionary_with_end_event_times, current_number_of_event_record)
                #     # The function returns the number of the next (new) element
                #     # Therefore, define the current time to find (new time) as start time of previous element
                    # TODO: DON'T forget about this structure (important after writeStart)       if not no_events_left_to_observe_from_file:
                  #       current_event_start_time = events_records[current_number_of_event_record - 1]["@Start"]

                # TODO: Create class for not list instances
                # elif not isinstance(events_records, list) and not no_events_left_to_observe_from_file and events_records["@Family"] != "User":
                #     if convert_time_of_occasion_into_seconds(line_time) == events_records["@Start"]:
                #         event_name = create_event_name(events_records)
                #         string_comment = f'{string_comment.split("\n")[0]}\t#* Start {event_name}\n'
                #         update_end_events_waiting_dictionary(events_records["@Start"], event_name, events_records["@Duration"], waiting_dictionary_with_end_event_times)
                #         no_events_left_to_observe_from_file = True

                # # 2. Write the END events
                # if waiting_dictionary_with_end_event_times:
                #     string_comment = write_END_events_into_comment_line(
                #         convert_time_of_occasion_into_seconds(line_time), waiting_dictionary_with_end_event_times, string_comment)

                # # 3. Write the sleep stages
                # if isinstance(sleep_stages_records, list) and current_number_of_sleep_stage_record < len(sleep_stages_records):
                #     # current_number_of_sleep_stage_record, string_comment = write_SLEEP_STAGES_into_comments(
                #     #     convert_time_of_occasion_into_seconds(line_time), sleep_stages_records, current_number_of_sleep_stage_record, string_comment)
                #     current_number_of_sleep_stage_record, string_comment = write_CONTINUOUS_LIST_STRUCTURE_into_comments(
                #         convert_time_of_occasion_into_seconds(line_time),
                #         sleep_stages_records,
                #         current_number_of_sleep_stage_record,
                #         sleep_stages_records[current_number_of_sleep_stage_record]["@Type"],
                #         "Sleep stage",
                #         string_comment)
                # elif not isinstance(sleep_stages_records, list):
                #     possible_string_comment = write_CONTINUOUS_NOT_LIST_STRUCTURE_into_comments(
                #         line_time,
                #         sleep_stages_records,
                #         sleep_stages_records["@Type"],
                #         "Sleep stage",
                #         string_comment)
                #
                #     if possible_string_comment:
                #         string_comment = possible_string_comment
                #         sleep_stage_is_recorded = True
                #
                # # 4. Write the body position
                # if isinstance(body_position_states_records, list) and current_number_of_body_position_state < len(body_position_states_records):
                #     current_number_of_body_position_state, string_comment = write_CONTINUOUS_LIST_STRUCTURE_into_comments(
                #         convert_time_of_occasion_into_seconds(line_time),
                #         body_position_states_records,
                #         current_number_of_body_position_state,
                #         body_position_states_records[current_number_of_body_position_state]["@Position"],
                #         "Body position",
                #         string_comment)
                # elif not isinstance(body_position_states_records, list):
                #     possible_string_comment = write_CONTINUOUS_NOT_LIST_STRUCTURE_into_comments(
                #         line_time,
                #         body_position_states_records,
                #         body_position_states_records["@Position"],
                #         "Body position",
                #         string_comment)
                #
                #     if possible_string_comment:
                #         string_comment = possible_string_comment
                #         body_position_state_is_recorded = True



                # 5. Finally, write the line into the file
                ePPG_output.write(string_comment)

            # Raise an exception, whether some events, sleep stages are left unrecorded
            if isinstance(events_records, list) and current_number_of_event_record != len(events_records):
                raise Exception(f"WARNING: The programme didn't write all events' start time.\nThe number of events in rml file is {len(events_records)}.\nThe number of events that have been written into the txt file is {current_number_of_event_record}."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if isinstance(events_records, list) and waiting_dictionary_with_end_event_times:
                raise Exception(f"WARNING: The programme didn't write all events' end time."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if (not isinstance(events_records, list) and events_records["@Family"] != "User" and
                not no_events_left_to_observe_from_file and waiting_dictionary_with_end_event_times):
                raise Exception("WARNING: The programme didn't write event's start or end time."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if isinstance(sleep_stages_records, list) and len(sleep_stages_records) != current_number_of_sleep_stage_record:
                raise Exception(f"WARNING: The programme didn't write all sleep stages records.\nThe number of sleep stages in rml file is {len(sleep_stages_records)}.\nThe number of sleep stages that have been written into the txt file is {current_number_of_sleep_stage_record}."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if not isinstance(sleep_stages_records, list) and not sleep_stage_is_recorded:
                raise Exception(f"WARNING: The programme didn't write sleep stage record."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if isinstance(body_position_states_records, list) and len(body_position_states_records) != current_number_of_body_position_state:
                raise Exception(f"WARNING: The programme didn't write all body position states records.\nThe number of body position states in rml file is {len(body_position_states_records)}."
                                f"\nThe number of body position state that have been written into the txt file is {current_number_of_body_position_state}."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
            if not isinstance(body_position_states_records, list) and not body_position_state_is_recorded:
                raise Exception(f"WARNING: The programme didn't write body position state record."
                                f"\nYour ePPG file comprises less time measurements than PSG file.")
        except HeaderDoesNotPresentInSourceFile as e:
            sys.stderr.write(f"The ERROR has occurred: {e.message} (file: {ePPG_file_src_path}).")
        except Exception as e:
            if "WARNING" in str(e):
                sys.stderr.write(f"{e}")
            else:
                sys.stderr.write(f"An UNEXPECTED ERROR has occurred: {e}\n{traceback.format_exc()}")
        finally:
            ePPG_source_file.close()
            ePPG_output.close()