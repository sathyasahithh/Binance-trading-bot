"""
Order placement logic for the trading bot.
Coordinates between CLI inputs and the Binance Client wrapper.
"""

import logging
from typing import Any, Dict

from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None
) -> Dict[str, Any]:
    """
    Submits an order to Binance Futures Testnet based on parameters.
    
    Args:
        client (BinanceFuturesClient): The wrapped Binance client.
        symbol (str): Trading pair (e.g. BTCUSDT).
        side (str): Side (BUY or SELL).
        order_type (str): Type of order (MARKET, LIMIT, STOP_LIMIT).
        quantity (float): Quantity of asset to trade.
        price (float | None): Target price for LIMIT/STOP_LIMIT orders.
        stop_price (float | None): Trigger price for STOP_LIMIT orders.
        
    Returns:
        dict: The response details from Binance.
    """
    logger.info(
        "Order request: %s %s %s Qty: %s, Price: %s, StopPrice: %s",
        order_type,
        side,
        symbol,
        quantity,
        price,
        stop_price
    )
    
    # Base arguments common to all orders
    order_params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity
    }
    
    if order_type == "MARKET":
        order_params["type"] = "MARKET"
        
    elif order_type == "LIMIT":
        order_params["type"] = "LIMIT"
        # Price must be formatted as string to prevent floating-point precision issues with API
        order_params["price"] = str(price)
        order_params["timeInForce"] = "GTC"
        
    elif order_type == "STOP_LIMIT":
        # In Binance Futures, STOP triggers a Limit Order.
        # It requires both price (limit price) and stopPrice (trigger price).
        order_params["type"] = "STOP"
        order_params["price"] = str(price)
        order_params["stopPrice"] = str(stop_price)
        order_params["timeInForce"] = "GTC"
        
    # Send request using our client wrapper which includes error handling and logging
    response = client.execute_request("futures_create_order", **order_params)
    
    logger.info("Order successfully placed. Details: %s", response)
    return response
