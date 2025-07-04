from annotation.customFunctions.Utilities.parser_rml import ParserRML


class Filters:
    """
    Extracts subtypes of <Event>, <NeuroAdultAASMStaging>, and <BodyPositionItem> nodes from a parsed RML structure.

    Filters are stored as a dictionary and can be accessed via the getFilters() method.
    """

    def __init__(self, parsed_RML):
        self.filters = dict()
        elements_roots = ParserRML.get_dictionary_of_root_elements(parsed_RML)
        self.fill_filters(elements_roots)

    def fill_filters(self, elements_roots):
        """
        Initializes the filters dictionary using the root elements from the parsed RML.

        Notes:
            If a root element contains only a single record, it is wrapped in a list to ensure consistent processing.

        Raises:
            ValueError: If all root elements are empty and no filters are created.
        """

        # 1. Events
        events_root = elements_roots["Events"]
        if len(events_root):
            if not isinstance(events_root, list):
                events_root = [events_root]
            self.initialize_filters_for_events(events_root)

        # 2. Sleep Stages
        sleep_stages_root = elements_roots["SleepStages"]
        if len(sleep_stages_root):
            if not isinstance(sleep_stages_root, list):
                sleep_stages_root = [sleep_stages_root]
            self.initialize_filters_for_positions_and_stages(
                sleep_stages_root,
                "SleepStages",
                "@Type")

        # 3. Body Positions
        body_positions_root = elements_roots["BodyPositions"]
        if len(body_positions_root):
            if not isinstance(body_positions_root, list):
                body_positions_root = [body_positions_root]
            self.initialize_filters_for_positions_and_stages(
                body_positions_root,
                "BodyPositions",
                "@Position")

        # Raise ValueError if all root elements (<Event>, <NeuroAdultAASMStaging>, <BodyPositionItem>) are empty
        if not self.filters:
            raise ValueError(
                "The RML file structure is invalid: roots <Event>, <UserStaging><NeuroAdultAASMStaging> and <BodyPositionItem> are empty.")

    def initialize_filters_for_events(self, events):
        """
        Initializes filters for <Event> nodes, excluding those with Family="User".

        Each <Event> is categorized by:
        1. Family (e.g., "Cardiac")
        2. Type (e.g., "Bradycardia")

        Resulting structure: {Family: set of distinct Type values}.
        """

        if isinstance(events, dict):
            events = [events]
        for event in events:
            family_name = event["@Family"]
            if family_name != "User":
                if family_name not in self.filters.keys():
                    self.filters.update({family_name: set()})
                self.filters[family_name].add(event["@Type"])

    def initialize_filters_for_positions_and_stages(self, root, family_name, type_name_specification):
        """
        Initializes filters for <NeuroAdultAASMStaging> and <BodyPositionItem> nodes.

        Filtering is based on:
        - SleepStages: @Type (e.g., Type="NREM1")
        - BodyPositions: @Position (e.g., Position="Up")

        Resulting structure: {family_name: set of distinct attribute values},
        where family_name is either "SleepStages" or "BodyPositions".
        """

        if family_name not in self.filters.keys():
            self.filters.update({family_name: set()})
        if isinstance(root, dict):
            root = [root]
        for item in root:
            self.filters[family_name].add(item[type_name_specification])

    def get_filters(self):
        """
        Returns the dictionary of extracted filters.
        """
        return self.filters
