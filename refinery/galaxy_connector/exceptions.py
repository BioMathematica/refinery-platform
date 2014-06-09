class ConnectionError(RuntimeError):
    '''No connection to Galaxy

    '''
    def __init__(self):
        super(ConnectionError, self).__init__(
            "Could not connect to Galaxy instance")


class ResponseError(RuntimeError):
    '''Galaxy sent less bytes than specified by Content-Length.
    This can happen when Galaxy is overloaded.

    '''
    def __init__(self):
        super(ResponseError, self).__init__(
            "Galaxy sent less bytes than specified by Content-Length")


class ResourceError(RuntimeError):
    '''HTTP status code 400
    returned for invalid workflow and history IDs, and Galaxy misconfiguration?

    '''
    def __init__(self):
        super(ResourceError, self).__init__("Galaxy request error")


class AuthenticationError(RuntimeError):
    '''HTTP status code 401

    '''
    def __init__(self):
        super(AuthenticationError, self).__init__("Invalid authentication")


class AuthorizationError(RuntimeError):
    '''HTTP status code 403

    '''
    def __init__(self):
        super(AuthorizationError, self).__init__("Authenticated but access forbidden")


class ResourceNameError(RuntimeError):
    '''HTTP status code 404

    '''
    def __init__(self):
        super(ResourceNameError, self).__init__("Galaxy URL not found")


class DatasetError(RuntimeError):
    '''HTTP status code 416 (returned when using an invalid dataset IDs)

    '''
    def __init__(self):
        super(DatasetError, self).__init__("Invalid Galaxy dataset ID")


class ServerError(RuntimeError):
    '''HTTP status code 500

    '''
    def __init__(self):
        super(ServerError, self).__init__("Miscellaneous Galaxy error")


class ServiceError(RuntimeError):
    '''HTTP status code 503

    '''
    def __init__(self):
        super(ServerError, self).__init__("Galaxy service temporarily unavailable")


class UnknownResponseError(RuntimeError):
    '''Any HTTP status code except errors above
    Example: 501 is returned for certain API endpoints like /api/datasets

    '''
    def __init__(self):
        super(UnknownResponseError, self).__init__(
            "Unknown response code from Galaxy instance")


class TimeoutError(RuntimeError):
    '''Galaxy connection timed out

    '''
    def __init__(self):
        super(TimeoutError, self).__init__(
            "Galaxy instance is taking too long to respond")


class InvalidResponseError(RuntimeError):
    '''Received invalid JSON response
    Galaxy sometimes reports errors in the body of the HTTP 200 response
    which is not possible to parse as JSON

    '''
    def __init__(self):
        super(InvalidResponseError, self).__init__(
            "Invalid response from Galaxy instance")


class MalformedResourceID(RuntimeError):
    '''Workflow, history or history content ID is None or not a string

    '''
    def __init__(self, resource_id):
        super(MalformedResourceID, self).__init__(
            "Malformed Galaxy resource id '{}' specified".format(resource_id))


class TestError(Exception):
    def __init__(self, msg="TestError exception"):
        self.message = msg
        super(TestError, self).__init__(msg)
