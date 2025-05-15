# The Continuous structure represents the structure from RML file, which has @Start property and not @Duration property
# Ending time is defined with the start of the next element
# Examples, Sleep Stages and Body Position
# Attention, the function is for root, which is list
from abc import abstractmethod, ABC
import logging
from annotation.customFunctions.Utilities.DateTimeFunctions import DateTimeFunctions

logger = logging.getLogger(__name__)


class ContinuousStructure(ABC):
    def __init__(self, root):
        self.root = root

    @abstractmethod
    def edit_comment(self, string_comment, element_group):
        pass

    @abstractmethod
    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        pass


class ContinuousStructureList(ContinuousStructure):
    def __init__(self, root, ePPG_offset_time, filters, element_property_name):
        super().__init__(root)
        self.root_length = len(self.root)
        self.current_number_of_element = 0
        self.filters = filters
        self.element_property_name = element_property_name

        # Skip the elements while the event wasn't last, if they were recorded only in RML (RML recording started earlier, but ePPG recording later)
        # OR the type isn't required by client

        while (self.current_number_of_element < self.root_length and
               (ePPG_offset_time > float(self.root[self.current_number_of_element]["@Start"]) or
               self.root[self.current_number_of_element][self.element_property_name] not in self.filters)):
            logger.error("Root: %s", self.current_number_of_element)
            self.current_number_of_element += 1

    def getCurrentNumberOfElement(self):
        return self.current_number_of_element

    def edit_comment(self, string_comment, element_group):
        string_comment = f"{string_comment.split("\n")[0]}\t#* {element_group}: {self.root[self.current_number_of_element][self.element_property_name]}\n"
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        if self.current_number_of_element < self.root_length:
            current_element_time = DateTimeFunctions.calculate_timedelta_plus_time_in_seconds(self.root[self.current_number_of_element]["@Start"], rml_offset_time)
            if line_time_in_seconds == current_element_time:
                string_comment = self.edit_comment(string_comment, element_group)
                self.current_number_of_element += 1
                while (self.current_number_of_element < self.root_length and
                       self.root[self.current_number_of_element][self.element_property_name] not in self.filters):
                    self.current_number_of_element += 1
        return string_comment


class ContinuousStructureNotList(ContinuousStructure):
    def __init__(self, root, ePPG_offset_time, element_property_name):
        super().__init__(root)
        self.element_is_recorded = False
        self.element_was_skipped = False
        self.element_property_name = element_property_name

        if float(self.root["@Start"]) < ePPG_offset_time:
            self.element_was_skipped = True

    def getElementIsRecorded(self):
        return self.element_is_recorded
    def getElementIsSkipped(self):
        return self.element_was_skipped

    def edit_comment(self, string_comment, element_group):
        string_comment = f'{string_comment.split("\n")[0]}\t#* {element_group}: {self.root[self.element_property_name]}\n'
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        if not self.element_was_skipped:
            element_start_time = DateTimeFunctions.calculate_timedelta_plus_time_in_seconds(self.root["@Start"], rml_offset_time)
            if line_time_in_seconds == element_start_time:
                self.element_is_recorded = True
                string_comment = self.edit_comment(string_comment, element_group)
        return string_comment