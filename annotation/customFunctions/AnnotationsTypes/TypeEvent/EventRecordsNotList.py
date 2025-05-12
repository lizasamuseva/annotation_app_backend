from annotation.customFunctions.AnnotationsTypes.TypeEvent.Event import Event


class EventRecordsNotList:
    def __init__(self, event_root, rml_offset_time, ePPG_offset_time):
        self.__event = Event(event_root, rml_offset_time)
        self.__isEventSkipped = False
        self.__isOnsetTimeRecorded = False
        self.__isEndTimeRecorded = False

        if float(self.__event.getSynchronisedOnsetTime()) < ePPG_offset_time or event_root["@Family"] == "User":
            self.__isEventSkipped = True


    def __edit_comment(self, string_comment, mode):
        string_comment = f'{string_comment.split("\n")[0]}\t#* {mode} {self.__event.getName()}\n'
        return string_comment

    def write_into_comments(self, line_time_in_seconds, string_comment):
        if not self.__isEventSkipped:
            if not self.__isOnsetTimeRecorded and line_time_in_seconds == self.__event.getSynchronisedOnsetTime():
                return self.__edit_comment(string_comment, "Start")
            elif not self.__isEndTimeRecorded and line_time_in_seconds == self.__event.getEndTime():
                return self.__edit_comment(string_comment, "End")
        return string_comment