from zope.interface import Interface, Attribute
class EventsRecordsStructure(Interface):
    current_event = Attribute("Current event for record")