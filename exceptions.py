"""
Custom Exception Hierarchy for AI Call Agent
Categorizes errors as Transient (retryable) or Permanent (non-retryable)
"""


# Base exception class
class CallAgentError(Exception):
    """Base exception for all call agent errors"""

    def __init__(self, message, service_name=None):
        self.message = message
        self.service_name = service_name
        super().__init__(self.message)


# Transient Errors - These can be retried
class TransientError(CallAgentError):
    """Errors that are temporary and can be retried"""
    pass


class TimeoutError(TransientError):
    """Service took too long to respond"""
    pass


class NetworkError(TransientError):
    """Network connection failed"""
    pass


class ServiceUnavailableError(TransientError):
    """Service returned 503 or is temporarily down"""
    pass


class RateLimitError(TransientError):
    """Too many requests - temporary throttling"""
    pass


# Permanent Errors - These should NOT be retried
class PermanentError(CallAgentError):
    """Errors that are permanent and should not be retried"""
    pass


class AuthenticationError(PermanentError):
    """Invalid credentials or unauthorized - 401/403"""
    pass


class InvalidPayloadError(PermanentError):
    """Request data is invalid or malformed"""
    pass


class QuotaExceededError(PermanentError):
    """Account quota exceeded - cannot retry"""
    pass


class ResourceNotFoundError(PermanentError):
    """Resource does not exist - 404"""
    pass


def classify_error(status_code, error_message=""):
    """
    Simple helper to classify errors based on HTTP status codes

    Args:
        status_code: HTTP status code
        error_message: Optional error message

    Returns:
        Appropriate exception instance
    """
    if status_code == 503:
        return ServiceUnavailableError(f"Service unavailable (503): {error_message}")
    elif status_code == 429:
        return RateLimitError(f"Rate limit exceeded (429): {error_message}")
    elif status_code == 408 or status_code == 504:
        return TimeoutError(f"Request timeout ({status_code}): {error_message}")
    elif status_code == 401 or status_code == 403:
        return AuthenticationError(f"Authentication failed ({status_code}): {error_message}")
    elif status_code == 404:
        return ResourceNotFoundError(f"Resource not found (404): {error_message}")
    elif status_code == 400:
        return InvalidPayloadError(f"Invalid request (400): {error_message}")
    elif 500 <= status_code < 600:
        return TransientError(f"Server error ({status_code}): {error_message}")
    else:
        return PermanentError(f"Unknown error ({status_code}): {error_message}")