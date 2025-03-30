class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class AuthorizationError(BaseAppException):
    """Raised when a user doesn't have permission for an action."""

    def __init__(
        self, message: str = "You don't have permission to perform this action"
    ):
        super().__init__(message)


class ResourceNotFoundError(BaseAppException):
    """Raised when a requested resource doesn't exist."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message)


class ValidationError(BaseAppException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class DatabaseError(BaseAppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message)
