"""
Custom exceptions module for the Binance Futures Trading Bot.
Defines domain-specific exception classes that inherit from a common base.
"""

class TradingBotError(Exception):
    """Base exception class for all errors in the trading bot application."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(TradingBotError):
    """Exception raised when input parameter validation fails."""
    pass


class AuthenticationError(TradingBotError):
    """Exception raised when API authentication credentials are invalid or missing."""
    pass


class APIError(TradingBotError):
    """
    Exception raised when the Binance API returns an error response.
    
    Attributes:
        code (int): Binance internal error code (e.g. -1013, -2015).
        status_code (int | None): HTTP status code of the response.
    """
    def __init__(self, message: str, code: int, status_code: int | None = None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

    def __str__(self) -> str:
        status_part = f" (HTTP {self.status_code})" if self.status_code else ""
        return f"[API Error {self.code}]{status_part}: {self.message}"


class NetworkError(TradingBotError):
    """Exception raised for network timeout, connection drops, or DNS failures."""
    pass
