"""AWSYS.CO Python SDK — Official client library for the AWSYS.CO URL Shortener API."""

from .client import Client
from .exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysValidationError,
)
from .models import (
    BulkLinkResult,
    BulkResult,
    ClickEvent,
    Folder,
    FolderList,
    Link,
    LinkList,
    LinkStats,
    MeResponse,
)

__version__ = "0.1.0"
__all__ = [
    # Client
    "Client",
    # Exceptions
    "AwsysError",
    "AwsysAuthError",
    "AwsysForbiddenError",
    "AwsysNotFoundError",
    "AwsysConflictError",
    "AwsysValidationError",
    "AwsysRateLimitError",
    # Models
    "Link",
    "LinkList",
    "LinkStats",
    "ClickEvent",
    "Folder",
    "FolderList",
    "BulkResult",
    "BulkLinkResult",
    "MeResponse",
]
