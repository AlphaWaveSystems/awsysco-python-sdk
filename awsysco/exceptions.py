"""Exceptions raised by the AWSYS.CO SDK."""

from __future__ import annotations

from typing import Any, Optional


class AwsysError(Exception):
    """Base exception for all AWSYS SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        status: Optional[int] = None,
        raw: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.raw = raw

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status={self.status!r})"
        )


class AwsysAuthError(AwsysError):
    """401 Unauthorized — invalid or missing API key."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 401)
        super().__init__(message, **kwargs)


class AwsysForbiddenError(AwsysError):
    """403 Forbidden — valid key but insufficient permissions."""

    def __init__(
        self,
        message: str = "Access forbidden. Insufficient permissions.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 403)
        super().__init__(message, **kwargs)


class AwsysNotFoundError(AwsysError):
    """404 Not Found — resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 404)
        super().__init__(message, **kwargs)


class AwsysConflictError(AwsysError):
    """409 Conflict — e.g. custom slug already taken."""

    def __init__(
        self,
        message: str = "Conflict. Resource already exists.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 409)
        super().__init__(message, **kwargs)


class AwsysValidationError(AwsysError):
    """400 Bad Request — invalid request parameters."""

    def __init__(
        self,
        message: str = "Validation error.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 400)
        super().__init__(message, **kwargs)


class AwsysRateLimitError(AwsysError):
    """429 Too Many Requests — rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please slow down.",
        *,
        retry_after: Optional[float] = None,
        resets_at: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("status", 429)
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.resets_at = resets_at


class AwsysServerError(AwsysError):
    """5xx — the platform reported an internal error."""

    def __init__(
        self,
        message: str = "Server error. Please try again later.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class AwsysNetworkError(AwsysError):
    """A transport-level failure (connection reset/refused, DNS, etc.) with no HTTP response."""

    def __init__(
        self,
        message: str = "Network error while contacting the AWSYS API.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class AwsysTimeoutError(AwsysNetworkError):
    """A request did not complete within the configured timeout."""

    def __init__(
        self,
        message: str = "Request to the AWSYS API timed out.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class AwsysConfigurationError(AwsysError):
    """Invalid SDK configuration (missing API key, bad base URL) — raised before any network call."""

    def __init__(
        self,
        message: str = "Invalid AWSYS SDK configuration.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
