from xml.etree.ElementTree import ParseError

import xmltodict
import xml.etree.ElementTree as ET


from annotation.customFunctions.Utilities.Constants.constants import EVENTS_ROOT_PATH, SLEEP_STAGES_ROOT_PATH, BODY_POSITIONS_ROOT_PATH
from annotation.customFunctions.Utilities.customExceptions import MissingRMLKeyError, InvalidRMLStructure

import logging

logger = logging.getLogger(__name__)

'''
ParserFromRML aims to initialize the ParsedRML structure, which will contain all related information to RML file, 
including the parsed into dictionary form outcome file.

For more information about structure ParsedRML, look at FilesStructures.ParsedRML.
'''
class ParserRML:
    # Dynamically extracts the namespaces from the file
    @staticmethod
    def extract_namespaces(file):
        namespaces = dict({})
        file.seek(0)
        for event, elem in ET.iterparse(file, events=("start-ns",)):
            namespaces[elem[1]] = elem[0]
        return namespaces

    # Converts RML file into dictionary form
    @staticmethod
    def parse_RML_to_Dict(path_to_tmp_RML):
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
        except ParseError as e:
            # logger.error(f"Error parsing RML file {path_to_tmp_RML}: {e}")
            raise InvalidRMLStructure()

    @staticmethod
    def get_nested_root_element(dictionary, path):
        try:
            for key in path:
                dictionary = dictionary[key]

        except KeyError as key:
            raise MissingRMLKeyError(key)
        return dictionary

    @staticmethod
    def get_dictionary_of_root_elements(RML_dictionary):
        return {
            "Events" : ParserRML.get_nested_root_element(RML_dictionary, EVENTS_ROOT_PATH),
            "SleepStages": ParserRML.get_nested_root_element(RML_dictionary, SLEEP_STAGES_ROOT_PATH),
            "BodyPositions": ParserRML.get_nested_root_element(RML_dictionary, BODY_POSITIONS_ROOT_PATH)
        }