class AppError(Exception):
    """Base application error."""


class ConflictError(AppError):
    """Raised when entity already exists."""


class UnauthorizedError(AppError):
    """Raised when authentication fails."""


class ForbiddenError(AppError):
    """Raised when access is forbidden."""


class NotFoundError(AppError):
    """Raised when entity is not found."""


class ExternalServiceError(AppError):
    """Raised when external service returns an error."""
