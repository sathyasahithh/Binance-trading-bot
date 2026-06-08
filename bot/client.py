"""
Client wrapper for Binance Futures Testnet API.
Handles client initialization, dotenv loading, and exception mapping.
"""

import os
import logging
from typing import Any, Callable
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import RequestException, ConnectionError, Timeout

from bot.exceptions import APIError, NetworkError, AuthenticationError

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Wrapper for python-binance Client to trade on Binance Futures Testnet.
    """
    
    def __init__(self) -> None:
        """
        Initializes the Binance client using credentials from environment.
        
        Raises:
            AuthenticationError: If credentials are not set or initialization fails.
        """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            logger.warning("Running in MOCK MODE. Real API calls are disabled.")
            if not self.api_key:
                self.api_key = "MOCK_KEY"
            if not self.api_secret:
                self.api_secret = "MOCK_SECRET"
            self.client = None
            return
            
        if not self.api_key or not self.api_secret:
            logger.error("API keys missing from environment.")
            raise AuthenticationError(
                "Binance API credentials missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET "
                "in your .env file or environment variables."
            )
            
        try:
            logger.info("Initializing python-binance Client with Testnet=True")
            # Initialize with testnet=True to target testnet base URLs
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            # Explicitly force Futures URL to Binance Futures Testnet base endpoint
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
        except Exception as e:
            logger.error("Failed to initialize Binance Client: %s", e)
            raise AuthenticationError(f"Failed to initialize Binance Client: {e}") from e

    def execute_request(self, func_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Executes a Binance API request with robust error handling and logs.
        Translates library exceptions into custom domain exceptions.
        
        Args:
            func_name (str): The name of the Binance client method to call.
            *args: Arguments for the client method.
            **kwargs: Keyword arguments for the client method.
            
        Returns:
            The raw response from the Binance API.
            
        Raises:
            AuthenticationError: On credential or signature issues.
            APIError: On Binance API validation or account issues.
            NetworkError: On timeout or connection issues.
        """
        logger.info("Sending request to Binance API: %s with args: %s, kwargs: %s", func_name, args, kwargs)
        
        if self.mock_mode:
            import time
            import random
            time.sleep(0.2)  # Simulate network latency
            
            symbol = kwargs.get("symbol", "BTCUSDT")
            side = kwargs.get("side", "BUY")
            order_type = kwargs.get("type", "MARKET")
            qty = kwargs.get("quantity", 1.0)
            price = kwargs.get("price", "0.0")
            stop_price = kwargs.get("stopPrice", "0.0")
            
            order_id = random.randint(10000000, 99999999)
            
            if order_type == "MARKET":
                response = {
                    "orderId": order_id,
                    "symbol": symbol,
                    "status": "FILLED",
                    "clientOrderId": f"mock_mkt_{order_id}",
                    "price": "0.00",
                    "avgPrice": "65230.50" if "BTC" in symbol else "3420.20",
                    "origQty": str(qty),
                    "executedQty": str(qty),
                    "cumQty": str(qty),
                    "timeInForce": "GTC",
                    "type": "MARKET",
                    "side": side,
                    "time": int(time.time() * 1000),
                    "updateTime": int(time.time() * 1000)
                }
            elif order_type == "LIMIT":
                response = {
                    "orderId": order_id,
                    "symbol": symbol,
                    "status": "NEW",
                    "clientOrderId": f"mock_lmt_{order_id}",
                    "price": str(price),
                    "avgPrice": "0.00",
                    "origQty": str(qty),
                    "executedQty": "0.00",
                    "cumQty": "0.00",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": side,
                    "time": int(time.time() * 1000),
                    "updateTime": int(time.time() * 1000)
                }
            else:  # STOP (which represents STOP_LIMIT in our code)
                response = {
                    "orderId": order_id,
                    "symbol": symbol,
                    "status": "NEW",
                    "clientOrderId": f"mock_stp_{order_id}",
                    "price": str(price),
                    "avgPrice": "0.00",
                    "origQty": str(qty),
                    "executedQty": "0.00",
                    "cumQty": "0.00",
                    "timeInForce": "GTC",
                    "type": "STOP",
                    "side": side,
                    "stopPrice": str(stop_price),
                    "time": int(time.time() * 1000),
                    "updateTime": int(time.time() * 1000)
                }
            logger.info("Mock response generated for %s: %s", func_name, response)
            return response

        try:
            func = getattr(self.client, func_name)
        except AttributeError as e:
            logger.error("Binance Client does not have method %s: %s", func_name, e)
            raise APIError(f"Binance Client missing method {func_name}", -1) from e

        try:
            response = func(*args, **kwargs)
            logger.info("Received response from Binance API for %s: %s", func_name, response)
            return response
            
        except BinanceAPIException as e:
            logger.error("Binance API exception in %s: [Code %s] %s", func_name, e.code, e.message)
            # Map known API authentication or permission error codes
            # -2015: Invalid API-key, IP, or permissions
            # -1022: Signature verification failed
            # -1002: Unauthorized
            if e.code in [-2015, -1022, -1002] or "signature" in e.message.lower() or "invalid api-key" in e.message.lower():
                raise AuthenticationError(f"Binance API authentication/authorization failed: {e.message}") from e
            raise APIError(e.message, e.code, e.status_code) from e
            
        except (ConnectionError, Timeout) as e:
            logger.error("Network connection/timeout error in %s: %s", func_name, e)
            raise NetworkError(f"Network connection failed: {e}") from e
            
        except RequestException as e:
            logger.error("HTTP request error in %s: %s", func_name, e)
            raise NetworkError(f"API request failed: {e}") from e
            
        except Exception as e:
            logger.error("Unexpected error executing %s: %s", func_name, e)
            raise e
