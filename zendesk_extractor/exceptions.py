"""
Custom exceptions for the Zendesk extractor application.
"""

class ZendeskExtractorError(Exception):
    """Base exception for the application."""
    pass

class ZendeskAPIError(ZendeskExtractorError):
    """Raised for errors related to the Zendesk API."""
    pass

class FileSaveError(ZendeskExtractorError):
    """Raised for errors related to saving files."""
    pass
