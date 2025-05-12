"""
ParsedRML class illustrates the instance of the structure, which contains related information to the RML file.

To maintain accurate code and not confuse among different instances of the one/different RML files,
the instance of the class should be only one through the whole programme.
=>Therefore the class implements SingletonBase class.
"""
class ParsedRML:
    """
    a) raw_RML - the file, uploaded by the client

    b) namespaces - represents dictionary of all namespaces from RML file
    For instance, it is the namespace from RML: xmlns:ce="http://www.respironics.com/CustomEventTypeDefs.xsd"

    c) parsed_file - the file, which is parsed into the dictionary form. Further the programme works with this file

    d) roots_to_elements - the roots to the elements of the parsed_file. They are saved there, because will be used through the whole programme.
    Important: If the RML file structure changes, this hardcoded part of the programme also should be changed.
    """
    def __init__(self, raw_RML_file):
        self.raw_RML = raw_RML_file
        self.namespaces = dict({})
        self.parsed_file = None
        self.roots_to_elements = dict({})

    '''
    Initializes the path to roots of the structures in RML file. 
    For now, they are: <Event>, <Stage>(which is <UserStaging>), <BodyPositionItem>.
    
    Throws KeyError if RML file structure doesn't contain the defined path to the element. 
    In this way, you will need to update the path to the element. 
    '''
