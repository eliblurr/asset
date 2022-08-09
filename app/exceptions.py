class BaseException(Exception):
    def __init__(self, message="Something went wrong"):
        self.message = message
        super().__init__(self.message)

    def _message(self):
        return self.message

class PermissionLimitReached(BaseException):
    def __init__(self):
        self.message = 'permission limit reached'
        super().__init__(self.message)

class OperationNotAllowed(BaseException):
    pass

class BlacklistedToken(BaseException):
    pass

class MaxOccurrenceError(BaseException):
    pass

class BadRequestError(BaseException):
    pass

class FileNotSupported(BaseException):
    pass

class UploadNotAllowed(BaseException):
    pass

class NotFound(BaseException):
    pass