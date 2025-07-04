from abc import abstractmethod, ABC

from annotation.helpers.utils.datetime_functions import DatetimeFunctions


class ContinuousStructure(ABC):
    """
        Abstract base class for representing RML nodes with a @Start property but no @Duration.

        Designed to support continuous events like SleepStages and BodyPositions.
        Supports both single elements and lists of elements.
    """

    def __init__(self, root):
        self.root = root

    @abstractmethod
    def edit_comment(self, string_comment, element_group):
        """
        Adds an annotation comment to a given ePPG line string.

        Args:
            string_comment (str): The original comment line.
            element_group (str): Group label (e.g., 'SleepStages' or 'BodyPositions') to annotate.

        Returns:
            str: The modified comment string with appended annotation.
        """
        pass

    @abstractmethod
    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        """
        Adds annotation to the line if RML event time matches the ePPG timestamp.

        Args:
            line_time_in_seconds (str): Time from the ePPG line.
            string_comment (str): Existing comment string to modify.
            element_group (str): Group label (e.g., 'SleepStages' or 'BodyPositions') to annotate.
            rml_offset_time (float): Time offset for aligning RML with ePPG.

        Returns:
            str: The updated (or original) comment string.
        """
        pass


class ContinuousStructureList(ContinuousStructure):
    """
    Handles annotation logic for RML nodes that appear as lists (e.g., multiple SleepStages or BodyPositions).
    """

    def __init__(self, root, eppg_offset_time, filters, element_property_name):
        super().__init__(root)
        self.root_length = len(self.root)
        self.current_number_of_element = 0
        self.filters = filters
        self.element_property_name = element_property_name

        # Skip the elements while the event wasn't last, if they were recorded only in RML (RML recording started earlier, but ePPG recording later)
        # OR the type isn't required by client's filters
        while (self.current_number_of_element < self.root_length and
               (eppg_offset_time > float(self.root[self.current_number_of_element]["@Start"]) or
                self.root[self.current_number_of_element][self.element_property_name] not in self.filters)):
            self.current_number_of_element += 1

    def edit_comment(self, string_comment, element_group):
        string_comment = f"{string_comment.split("\n")[0]}\t#* {element_group}: {self.root[self.current_number_of_element][self.element_property_name]}\n"
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        # 1. Check whether the nodes (e.g. <Stage>, <BodyPositionItem>) did not run out of
        if self.current_number_of_element < self.root_length:
            # 2. Calculate the synchronized time of the record
            current_element_time = DatetimeFunctions.time_plus_timedelta(
                self.root[self.current_number_of_element]["@Start"], rml_offset_time)
            # 3. Check whether the synchronized time equal to ePPG line time
            if line_time_in_seconds == current_element_time:
                # 4. Initialize new line with annotation to write to ePPG
                string_comment = self.edit_comment(string_comment, element_group)
                # 5. Find the node which is in requested filters and save its number for further processing
                self.current_number_of_element += 1
                while (self.current_number_of_element < self.root_length and
                       self.root[self.current_number_of_element][self.element_property_name] not in self.filters):
                    self.current_number_of_element += 1
        # Return whether not edited or annotated line
        return string_comment


class ContinuousStructureNotList(ContinuousStructure):
    """
    Handles annotation logic for RML nodes that appear as a single element.
    """

    def __init__(self, root, eppg_offset_time, element_property_name):
        super().__init__(root)
        self.element_is_recorded = False
        self.element_was_skipped = False
        self.element_property_name = element_property_name

        # Skip the element, if it was recorded earlier than the ePPG recordings were started
        if float(self.root["@Start"]) < eppg_offset_time:
            self.element_was_skipped = True

    def edit_comment(self, string_comment, element_group):
        string_comment = f'{string_comment.split("\n")[0]}\t#* {element_group}: {self.root[self.element_property_name]}\n'
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment, element_group, rml_offset_time):
        # 1. Check whether the element wasn't skipped
        if not self.element_was_skipped:
            # 2. Calculate the synchronized time
            element_start_time = DatetimeFunctions.time_plus_timedelta(self.root["@Start"],
                                                                       rml_offset_time)
            # 3. Adjust the annotation to the line, if the times (from RML and ePPG) are equal
            if line_time_in_seconds == element_start_time:
                self.element_is_recorded = True
                string_comment = self.edit_comment(string_comment, element_group)
        return string_comment
