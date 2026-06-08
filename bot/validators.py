"""
Validators module for the trading bot.
Provides functions to check symbol format, order sides, types, quantity, price, and stop price.
"""

import re
from bot.exceptions import ValidationError

def validate_symbol(symbol: str) -> str:
    """
    Validates the trading pair symbol.
    
    Args:
        symbol (str): The symbol to validate (e.g. 'BTCUSDT').
        
    Returns:
        str: The cleaned, uppercase symbol.
        
    Raises:
        ValidationError: If the symbol is empty, invalid type, or not in valid format.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string.")
    
    clean_symbol = symbol.strip().upper()
    # Binance symbols are generally alphanumeric uppercase, between 2 and 20 chars
    if not re.match(r"^[A-Z0-9]{2,20}$", clean_symbol):
        raise ValidationError(
            f"Symbol '{symbol}' is not in a valid format. Must be alphanumeric (e.g., BTCUSDT)."
        )
    return clean_symbol


def validate_side(side: str) -> str:
    """
    Validates the order side (BUY or SELL).
    
    Args:
        side (str): The order side.
        
    Returns:
        str: Uppercase order side.
        
    Raises:
        ValidationError: If the side is invalid.
    """
    if not side or not isinstance(side, str):
        raise ValidationError("Side must be a non-empty string.")
    
    clean_side = side.strip().upper()
    if clean_side not in ["BUY", "SELL"]:
        raise ValidationError(f"Invalid side '{side}'. Side must be either BUY or SELL.")
    return clean_side


def validate_type(order_type: str) -> str:
    """
    Validates the order type (MARKET, LIMIT, STOP_LIMIT).
    
    Args:
        order_type (str): The order type.
        
    Returns:
        str: Uppercase order type.
        
    Raises:
        ValidationError: If the order type is invalid.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type must be a non-empty string.")
    
    clean_type = order_type.strip().upper()
    if clean_type not in ["MARKET", "LIMIT", "STOP_LIMIT"]:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Supported types: MARKET, LIMIT, STOP_LIMIT."
        )
    return clean_type


def validate_quantity(quantity: float) -> float:
    """
    Validates that the quantity is a positive number.
    
    Args:
        quantity (float): The quantity.
        
    Returns:
        float: Validated quantity.
        
    Raises:
        ValidationError: If quantity is <= 0 or not numeric.
    """
    try:
        val = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity '{quantity}' must be a numeric value.")
    
    if val <= 0:
        raise ValidationError(f"Quantity must be strictly greater than 0. Got: {val}")
    return val


def validate_price(price: float | None, order_type: str) -> float | None:
    """
    Validates the price parameter. Required for LIMIT and STOP_LIMIT orders.
    Must not be specified for MARKET orders.
    
    Args:
        price (float | None): The price.
        order_type (str): The validated order type.
        
    Returns:
        float | None: Validated price or None.
        
    Raises:
        ValidationError: If price validation conditions are violated.
    """
    if order_type in ["LIMIT", "STOP_LIMIT"]:
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            val = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price '{price}' must be a numeric value.")
        if val <= 0:
            raise ValidationError(f"Price must be strictly greater than 0. Got: {val}")
        return val
    else:
        if price is not None:
            raise ValidationError(f"Price should not be specified for MARKET orders. Got: {price}")
        return None


def validate_stop_price(stop_price: float | None, order_type: str) -> float | None:
    """
    Validates the stop_price parameter. Required for STOP_LIMIT orders.
    Must not be specified for MARKET or LIMIT orders.
    
    Args:
        stop_price (float | None): The stop price.
        order_type (str): The validated order type.
        
    Returns:
        float | None: Validated stop price or None.
        
    Raises:
        ValidationError: If stop price validation conditions are violated.
    """
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price (trigger price) is required for STOP_LIMIT orders.")
        try:
            val = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price '{stop_price}' must be a numeric value.")
        if val <= 0:
            raise ValidationError(f"Stop price must be strictly greater than 0. Got: {val}")
        return val
    else:
        if stop_price is not None:
            raise ValidationError(f"Stop price should only be specified for STOP_LIMIT orders. Got: {stop_price}")
        return None
