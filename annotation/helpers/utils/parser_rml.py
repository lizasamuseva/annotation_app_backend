from xml.etree.ElementTree import ParseError

import xmltodict
import xml.etree.ElementTree as ET

from annotation.helpers.utils.constants.constants import EVENTS_ROOT_PATH, SLEEP_STAGES_ROOT_PATH, \
    BODY_POSITIONS_ROOT_PATH
from annotation.helpers.utils.custom_exceptions import MissingRMLKeyError, InvalidRMLStructure
import logging

logger = logging.getLogger(__name__)


class ParserRML:
    """
    Parses RML files into dictionary form and extracts relevant nodes for use throughout the application.
    """

    @staticmethod
    def extract_namespaces(file):
        """
        Extracts XML namespaces dynamically from the provided RML file.
        """
        namespaces = dict({})
        file.seek(0)
        for event, elem in ET.iterparse(file, events=("start-ns",)):
            namespaces[elem[1]] = elem[0]
        return namespaces

    @staticmethod
    def parse_RML_to_dict(path_to_tmp_RML):
        """
        Parses an RML file into a dictionary using xmltodict.

        Raises:
            InvalidRMLStructure: If the XML structure is invalid or cannot be parsed.
        """
        try:
            with open(path_to_tmp_RML, 'rb') as file:
                namespaces = ParserRML.extract_namespaces(file)
                file.seek(0)
                parsed_dict = xmltodict.parse(
                    file.read().decode('utf-8'),
                    process_namespaces=True,
                    namespaces=namespaces,
                    namespace_separator=":"
                )
            return parsed_dict
        except ParseError:
            raise InvalidRMLStructure()

    @staticmethod
    def get_nested_root_element(dictionary, path):
        """
        Retrieves a nested node from a dictionary following a specified path.

        Raises:
            MissingRMLKeyError: If any key in the path is missing from the dictionary.
        """
        try:
            for key in path:
                dictionary = dictionary[key]

        except KeyError as key:
            raise MissingRMLKeyError(key)
        return dictionary

    @staticmethod
    def get_dictionary_of_root_elements(RML_dictionary):
        """
        Extracts and returns key RML sections (Events, SleepStages, BodyPositions) from the parsed dictionary.
        """
        return {
            "Events": ParserRML.get_nested_root_element(RML_dictionary, EVENTS_ROOT_PATH),
            "SleepStages": ParserRML.get_nested_root_element(RML_dictionary, SLEEP_STAGES_ROOT_PATH),
            "BodyPositions": ParserRML.get_nested_root_element(RML_dictionary, BODY_POSITIONS_ROOT_PATH)
        }
