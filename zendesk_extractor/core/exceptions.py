"""Custom exceptions for the Zendesk extractor application."""

class ZendeskExtractorError(Exception):
    """Base exception for all application-specific errors.

    This exception can be caught to handle any error originating from the
    Zendesk extractor application.
    """
    pass

class ZendeskAPIError(ZendeskExtractorError):
    """Raised for errors related to the Zendesk API.

    This exception is raised when there are issues with API requests, such as
    authentication failures, network problems, or invalid API responses.
    """
    pass

class FileSaveError(ZendeskExtractorError):
    """Raised for errors related to saving files.

    This exception is raised when the application encounters an error while
    attempting to save data to a file, such as permission errors or disk
    space issues.
    """
    pass
