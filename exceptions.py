class TrackerException(Exception):
    pass

class NoItemsLeftException(TrackerException):
    pass

class InvalidItemException(TrackerException):
    pass

class IpDoesNotMatchException(TrackerException):
    pass

class ProjectNotActiveException(TrackerException):
    pass
