# RML paths to the records
EVENTS_ROOT_PATH = ['PatientStudy', 'ScoringData', 'Events', 'Event']
SLEEP_STAGES_ROOT_PATH = ['PatientStudy', 'ScoringData', 'StagingData', 'UserStaging', 'NeuroAdultAASMStaging', 'Stage']
BODY_POSITIONS_ROOT_PATH = ['PatientStudy', 'BodyPositionState', 'BodyPositionItem']
RECORD_TIME_ROOT_PATH = ['PatientStudy', 'Acquisition', 'Sessions', 'Session', 'RecordingStart']

# Cache keys
CACHE_KEY_PARSED_RML = 'parsed_rml_cache_key'
CACHE_KEY_ALL_POSSIBLE_FILTERS = 'all_possible_filters_cache_key'
CACHE_KEY_REQUIRED_FILTERS = 'required_filters_cache_key'
CACHE_KEY_EPPG_PATH = 'eppg_path_cache_key'

# Files/Json keys in requests
KEY_IN_REQUEST_RML = "RML_src"
KEY_IN_REQUEST_REQUIRED_FILTERS = "filters"
KEY_IN_REQUEST_EPPG = "EPPG_src"

