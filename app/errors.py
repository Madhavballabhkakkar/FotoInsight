"""Application errors that should become a clear message, not a stack trace."""


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
