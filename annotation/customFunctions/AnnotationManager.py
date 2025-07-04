import os
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from api import settings
from .AnnotationsTypes.TypeEvent.EventRecordsNotList import EventRecordsNotList
from .Utilities.Constants.constants import RECORD_TIME_ROOT_PATH
from .Utilities.CustomExceptions import SessionExpired
from .Utilities.DateTimeFunctions import DateTimeFunctions
from .Utilities.ParserRML import ParserRML
from .AnnotationsTypes.TypeEvent.EventRecordsList import EventRecordsList
from .AnnotationsTypes.ContinuousStructures.ContinuousStructure import ContinuousStructureList, \
    ContinuousStructureNotList


class AnnotationManager:
    """
    Handles annotation of ePPG recordings using synchronized PSG (RML) data.
    """

    def __init__(self, RML_dict, ePPG_path, filters):
        """
        Initializes the ProcessAnnotations class.

        Args:
            RML_dict (dict): Parsed RML structure containing annotations.
            ePPG_path (str): Path to the raw ePPG file.
            filters (dict): Filters specifying which structures or events to include.
        """
        self.RML_dict = RML_dict
        self.ePPG_path = ePPG_path
        self.filters = filters

        self.roots_to_elements = ParserRML.get_dictionary_of_root_elements(self.RML_dict)

        self.ePPG_offset_time = None
        self.RML_offset_time = None

        self.events_structure = None
        self.sleep_stages_structure = None
        self.body_position_structure = None

    def calculate_time_offset(self, date_time_line):
        """
        Calculates and sets the time offset between the RML and ePPG recordings.

        If the RML started after the ePPG, adjusts the RML event times (rml_offset).
        If the RML started before the ePPG, adjusts the ePPG line times(eppg_offset.
        """

        rml_datetime_recording = DateTimeFunctions.convert_datetime_from_rml(
            ParserRML.get_nested_root_element(self.RML_dict, RECORD_TIME_ROOT_PATH)
        )

        ePPG_datetime_recording = DateTimeFunctions.convert_serial_number_to_date(
            float(date_time_line.split("=")[1].split("\n")[0]))
        time_offset = DateTimeFunctions.compare_datetime_from_rml_and_ePPG(rml_datetime_recording,
                                                                           ePPG_datetime_recording)

        self.ePPG_offset_time = timedelta(seconds=0).total_seconds()
        self.RML_offset_time = timedelta(seconds=0).total_seconds()

        # RML file has started the recording after ePPG file has started
        if time_offset > timedelta(seconds=0).total_seconds():
            self.RML_offset_time = time_offset
        else:
            # RML file has started the recording before ePPG file has started
            self.ePPG_offset_time = abs(time_offset)

    def structures_initialization(self):
        """
        Initializes annotation structures (Events, SleepStages, BodyPositions)
        based on the filters and the RML data structure format (list or single node).
        """

        # ------------Event Structure-------------------
        not_event_filters = ["SleepStages", "BodyPositions"]
        has_events_filters = not set(self.filters.keys()).issubset(not_event_filters)
        if has_events_filters:
            event_filters = {k: v for k, v in self.filters.items() if k not in not_event_filters}
            if isinstance(self.roots_to_elements["Events"], list):
                self.events_structure = EventRecordsList(self.roots_to_elements["Events"], self.RML_offset_time,
                                                         self.ePPG_offset_time, event_filters)
            else:
                self.events_structure = EventRecordsNotList(self.roots_to_elements["Events"], self.RML_offset_time,
                                                            self.ePPG_offset_time)

        # ------------SleepStages Structure-------------------
        if "SleepStages" in self.filters:
            if isinstance(self.roots_to_elements["SleepStages"], list):
                self.sleep_stages_structure = ContinuousStructureList(self.roots_to_elements["SleepStages"],
                                                                      self.ePPG_offset_time,
                                                                      self.filters["SleepStages"], "@Type")
            else:
                self.sleep_stages_structure = ContinuousStructureNotList(self.roots_to_elements["SleepStages"],
                                                                         self.ePPG_offset_time, "@Type")

        # ------------BodyPositions Structure-------------------
        if "BodyPositions" in self.filters:
            if isinstance(self.roots_to_elements["BodyPositions"], list):
                self.body_position_structure = ContinuousStructureList(self.roots_to_elements["BodyPositions"],
                                                                       self.ePPG_offset_time,
                                                                       self.filters["BodyPositions"], "@Position")
            else:
                self.body_position_structure = ContinuousStructureNotList(self.roots_to_elements["BodyPositions"],
                                                                          self.ePPG_offset_time, "@Position")

    def add_annotations(self):
        """
        Reads the ePPG file, calculates offsets, initializes annotation structures,
        and writes a new annotated file based on matched timestamps.

        Returns:
            str: Path to the newly created annotated file.
        Raises:
            SessionExpired: If the ePPG file path does not exist/wasn't uploaded/expired.
        """
        # Check if the file exists before proceeding
        if not os.path.exists(self.ePPG_path):
            raise SessionExpired

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))

        with open(self.ePPG_path, 'r') as f:
            lines = f.readlines()
            self.calculate_time_offset(lines[0])
            self.structures_initialization()

            new_file_path = os.path.join(fs.location, 'annotated_file.txt')

            with open(new_file_path, 'w') as out_file:

                out_file.writelines(lines[:2])

                for line in lines[2:]:
                    line_time = line.split("\t")[0]
                    # Convert the time of the record from ePPG and convert it into seconds
                    line_time_in_seconds = DateTimeFunctions.convert_time_of_occasion_into_seconds(line_time)
                    # Calculate synchronized time of the record
                    line_time_with_delta = DateTimeFunctions.calculate_timedelta_plus_time_in_seconds(
                        line_time_in_seconds, self.ePPG_offset_time
                    )
                    string_comment = line

                    # Append annotations to the current line if the corresponding structure is initialized.
                    if self.events_structure:
                        if isinstance(self.events_structure, EventRecordsList):
                            string_comment = self.events_structure.write_START_events_into_comment_line(
                                line_time_with_delta, string_comment)
                            string_comment = self.events_structure.write_END_events_into_comment_line(
                                line_time_with_delta, string_comment)
                        else:
                            string_comment = self.events_structure.write_into_comments(line_time_with_delta,
                                                                                       string_comment)
                    if self.sleep_stages_structure:
                        string_comment = self.sleep_stages_structure.write_into_comments(
                            line_time_with_delta, string_comment, "Sleep Stages", self.RML_offset_time
                        )

                    if self.body_position_structure:
                        string_comment = self.body_position_structure.write_into_comments(
                            line_time_with_delta, string_comment, "Body Position", self.RML_offset_time
                        )

                    out_file.write(string_comment)

        return new_file_path
