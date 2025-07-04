from annotation.customFunctions.AnnotationsTypes.TypeEvent.Event import Event
from zope.interface import implementer

from .EventsRecordsStructure import EventsRecordsStructure


@implementer(EventsRecordsStructure)
class EventRecordsNotList:
    """
    Represents a single node <Event> with metadata and filtering.

    Attributes:
    - event (Event): The Event instance holding annotation data.
    - isEventSkipped (bool): Flag to indicate whether the event is skipped (e.g., due to being too early or of an unwanted type).
    - isOnsetTimeRecorded (bool): Tracks whether the start time annotation has been written.
    - isEndTimeRecorded (bool): Tracks whether the end time annotation has been written.
    """

    def __init__(self, event_root, rml_offset_time, ePPG_offset_time):
        self.current_event = Event(event_root, rml_offset_time)
        self.is_event_skipped = False
        self.is_onset_time_recorded = False
        self.is_end_time_recorded = False

        # Skip event if it's before the ePPG start
        if float(self.current_event.synchronised_onset_time) < ePPG_offset_time:
            self.is_event_skipped = True

    def edit_comment(self, string_comment, mode):
        """
        Appends the annotation (Start or End) to the current ePPG line.
        Returns the line from ePPG with appended annotation.
        """
        string_comment = f'{string_comment.split("\n")[0]}\t#* {mode} {self.current_event.name}\n'
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment):
        """
        Conditionally appends the annotation to the comment line based on timing and state.
        Returns whether raw or annotated string.
        """
        if not self.is_event_skipped:
            if not self.is_onset_time_recorded and line_time_in_seconds == self.current_event.synchronised_onset_time:
                return self.edit_comment(string_comment, "Start")
            elif not self.is_end_time_recorded and line_time_in_seconds == self.current_event.end_time:
                return self.edit_comment(string_comment, "End")
        return string_comment
