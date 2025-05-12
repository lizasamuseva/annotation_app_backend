import logging
from annotation.customFunctions.Utilities.ParserRML import ParserRML
'''
\\TODO: WRITE COMMENTS HERE A LITTLE BIT LATER

This class should be instantiated first in the programme
'''
logger = logging.getLogger(__name__)
# Because it sets up the filters, which will be rendered in the application
#
# It sets only <Events>, <Stage>, and <BodyPositionItem>
class Filters:
    def __init__(self, parsed_RML):
        self.__filters = dict()
        elements_roots = ParserRML.get_dictionary_of_root_elements(parsed_RML)
        self.__fillFilters(elements_roots)
        # self.__encode_to_JSON()

    # Fills filters
    # If the root contains only one record => rewrite it like an element of the list
    def __fillFilters(self, elements_roots):
        # 1. Events
        events_root = elements_roots["Events"]
        if len(events_root):
            if len(events_root) == 1:
                events_root = [events_root]
            self.__filtersInitializationForEvents(events_root)

        # 2. Sleep Stages
        sleep_stages_root = elements_roots["SleepStages"]
        if len(sleep_stages_root):
            if len(sleep_stages_root) == 1:
                sleep_stages_root = [sleep_stages_root]
            self.__filtersInitializationForBodyPosAndStages(
                sleep_stages_root,
                "SleepStages",
                "@Type")

        # 3. Body Positions
        body_positions_root = elements_roots["BodyPositions"]
        if len(body_positions_root):
            if len(body_positions_root) == 1:
                body_positions_root = [body_positions_root]
            self.__filtersInitializationForBodyPosAndStages(
                body_positions_root,
                "BodyPositions",
                "@Position")

        # 4. Raises ValueError if the RML file contains the empty root's elements
        if not self.__filters:
            raise ValueError("The RML file structure is invalid: roots <Event>, <Stage> (for <UserStaging>) and <BodyPositionItem> are empty.")

    # Manages the addition of the UNIQUE Family Name of the event into the dictionary
    # Attention! Except Family = "User"
    # Also, adds the extension types into the Filter() extension
    def __filtersInitializationForEvents(self, events):
        if isinstance(events, dict):
            events = [events]
        for event in events:
            family_name = event["@Family"]
            if family_name != "User":
                if family_name not in self.__filters.keys():
                    self.__filters.update({family_name: set()})
                self.__filters[family_name].add(event["@Type"])

    # Manages the addition of the Family Name for Body Position and Stages structures, because they are quite similar
    # If somebody wants to call this function one more than one time
    # => checks, if the family name already exists and do nothing if yes
    # Fills the Filter() with extensions Types
    def __filtersInitializationForBodyPosAndStages(self, root, family_name, type_name_specification):
        if family_name not in self.__filters.keys():
            self.__filters.update({family_name: set()})
        if isinstance(root, dict):
            root = [root]
        for item in root:
            self.__filters[family_name].add(item[type_name_specification])

    def getFilters(self):
        return self.__filters
