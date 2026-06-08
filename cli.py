#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.
Provides an interactive command-line interface using argparse and Rich.
"""

import argparse
import sys
import logging

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.logging_config import setup_logging
from bot.exceptions import TradingBotError, ValidationError
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.client import BinanceFuturesClient
from bot.orders import place_order

# Initialize Rich Console
console = Console()
logger = logging.getLogger("cli")


def main() -> None:
    # Set up logging to logs/trading.log
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Binance Futures USDT-M Testnet Trading Bot CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example commands:\n"
               "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
               "  python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000\n"
               "  python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 60000 --stop-price 59500"
    )
    
    parser.add_argument(
        "--symbol",
        required=True,
        type=str,
        help="Trading pair symbol (e.g. BTCUSDT, ETHUSDT)"
    )
    parser.add_argument(
        "--side",
        required=True,
        type=str,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type",
        required=True,
        type=str,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type: MARKET, LIMIT, or STOP_LIMIT"
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        help="Order quantity (must be strictly greater than 0)"
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit price (Required for LIMIT and STOP_LIMIT orders)"
    )
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        help="Trigger price (Required for STOP_LIMIT orders)"
    )

    # If no arguments provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    try:
        # 1. Validate inputs using validation layer
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_type(args.type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
        
    except ValidationError as e:
        logger.error("CLI input validation failed: %s", e.message)
        console.print(Panel(
            f"[bold red]Validation Error:[/bold red] {e.message}",
            title="Input Validation Failed",
            border_style="red"
        ))
        sys.exit(1)

    # 2. Print Order Request Summary
    summary_table = Table(title="Order Request Summary", title_style="bold cyan", border_style="cyan")
    summary_table.add_column("Parameter", style="yellow", no_wrap=True)
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Symbol", symbol)
    summary_table.add_row("Side", side)
    summary_table.add_row("Order Type", order_type)
    summary_table.add_row("Quantity", f"{quantity}")
    if price is not None:
        summary_table.add_row("Limit Price", f"{price} USDT")
    if stop_price is not None:
        summary_table.add_row("Stop Trigger Price", f"{stop_price} USDT")
        
    console.print(summary_table)
    console.print()

    # 3. Instantiate client and submit order
    try:
        console.print("[bold yellow]Initializing client and sending request to Binance Testnet...[/bold yellow]")
        client = BinanceFuturesClient()
        
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        # 4. Display response details
        # Futures REST response parameters:
        # orderId, status, origQty, avgPrice, price, executedQty, type, side, etc.
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", "N/A")
        avg_price = response.get("avgPrice")
        
        # Some orders (e.g. LIMIT/STOP before filled) might have avgPrice = "0.00000" or similar
        # Fall back to specified price if average price is not calculated
        try:
            if not avg_price or float(avg_price) == 0.0:
                avg_price = response.get("price", "N/A")
        except (ValueError, TypeError):
            avg_price = response.get("price", "N/A")

        avg_price_display = f"{avg_price} USDT" if avg_price != "N/A" else "N/A"

        response_table = Table(title="Order Response Details", title_style="bold green", border_style="green")
        response_table.add_column("Field", style="yellow")
        response_table.add_column("Value", style="white")
        
        response_table.add_row("Order ID", f"{order_id}")
        response_table.add_row("Status", f"{status}")
        response_table.add_row("Executed Qty", f"{executed_qty}")
        response_table.add_row("Avg Execution Price", avg_price_display)
        
        console.print(Panel(
            "[bold green]SUCCESS: Order placed successfully on Binance Futures Testnet![/bold green]",
            border_style="green"
        ))
        console.print(response_table)
        
    except TradingBotError as e:
        # Handled custom application exception
        console.print(Panel(
            f"[bold red]ORDER EXECUTION FAILED![/bold red]\n\n{e}",
            title="API / Network / Auth Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        # Unexpected error fallback
        console.print(Panel(
            f"[bold red]CRITICAL SYSTEM ERROR![/bold red]\n\n{e}",
            title="Fatal Exception",
            border_style="red"
        ))
        logger.exception("An unexpected critical exception occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
