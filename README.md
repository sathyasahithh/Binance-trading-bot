# Binance Futures USDT-M Testnet Trading Bot

A clean, production-ready Python command-line utility for executing orders on the **Binance Futures Testnet (USDT-M)**. Designed with modularity, clean architecture, strict input validation, custom error mapping, and rich command-line interfaces.

---

## Features

- **Order Types**: Supports `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
- **Order Sides**: Executes both `BUY` and `SELL` instructions.
- **Robust Validations**: Standardizes symbols, restricts side options, ensures strictly positive quantities, and checks for required price points prior to executing requests.
- **Clean Architecture**: Separates validations, network client wrappers, execution triggers, CLI configurations, and log setups.
- **Rich CLI UX**: Implements `rich` formatting for styled parameter summaries, success/error banners, and clean execution output tables.
- **Robust Exception Handling**: Maps generic errors and HTTP library timeouts into custom domain exceptions (`ValidationError`, `AuthenticationError`, `APIError`, `NetworkError`).
- **Development/Dry-Run Support**: Includes a mock-trading simulation mode that runs the full execution path without requiring active Binance API credentials.

---

## Project Structure

```text
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py             # Client wrapper and exception translator
│   ├── orders.py             # Order placement orchestrator
│   ├── validators.py         # Strictly validates CLI inputs
│   ├── logging_config.py     # Setup for rotating file-based logger
│   └── exceptions.py         # Custom application exceptions
│
├── logs/
│   └── trading.log           # Application request, response, and error logs
│
├── cli.py                    # Main executable interface
├── requirements.txt          # Python dependencies
├── .env.example              # Sample environment template
├── .env                      # Active local configuration (Git-ignored)
├── README.md                 # Complete documentation
└── .gitignore                # Excludes cache, environments, and secret files
```

---

## Installation

### 1. Clone or Extract the Project
Ensure the project structure is placed in your working directory.

### 2. Set Up a Virtual Environment (Recommended)
Navigate to the project root and create a virtual environment:

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required third-party libraries:
```bash
pip install -r requirements.txt
```

---

## Configuration & Credentials

### Binance Futures Testnet Setup
1. Log in to the [Binance Futures Testnet Portal](https://testnet.binancefuture.com) (using a GitHub or Google account).
2. Generate your **Testnet API Key** and **Testnet API Secret** from the API Key dashboard.
3. Fund your Testnet account using the testnet faucet controls on the portal dashboard.

### Environment Variable Setup
Copy the configuration template:
```bash
cp .env.example .env
```
Open `.env` and fill in your API keys:
```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
MOCK_MODE=false
```

> [!TIP]
> **Mock Mode**: Setting `MOCK_MODE=true` in your `.env` runs the bot in simulated mode. It bypasses live Binance network calls and generates mocked responses, which is ideal for testing the interface or when you do not have API keys on hand.

---

## Example Usage Commands

### 1. Show Help & Option Details
```bash
python cli.py --help
```

### 2. MARKET BUY Order
Places a market order to buy 0.01 BTCUSDT immediately at the current market price:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### 3. LIMIT SELL Order
Places a limit order to sell 0.05 BTCUSDT when the price reaches 68,000 USDT:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.05 --price 68000
```

### 4. STOP_LIMIT BUY Order (Bonus Feature)
Places a stop-limit order to buy 0.02 BTCUSDT with a limit price of 69,100 USDT when the trigger price reaches 69,000 USDT:
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.02 --price 69100 --stop-price 69000
```

### 5. Input Validation Demonstration (Expect failure)
If parameters are missing or out of valid ranges, the validators reject them without sending request calls:
```bash
# Missing price for limit order:
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01

# Invalid quantity:
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity -0.1
```

---

## Sample Console Output

### LIMIT SELL Command:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.05 --price 68000
```

### Response Presentation:
```text
    Order Request Summary     
+----------------------------+
| Parameter   | Value        |
|-------------+--------------|
| Symbol      | BTCUSDT      |
| Side        | SELL         |
| Order Type  | LIMIT        |
| Quantity    | 0.05         |
| Limit Price | 68000.0 USDT |
+----------------------------+

Initializing client and sending request to Binance Testnet...
+-----------------------------------------------------------------------------+
| SUCCESS: Order placed successfully on Binance Futures Testnet!              |
+-----------------------------------------------------------------------------+
        Order Response Details        
+------------------------------------+
| Field               | Value        |
|---------------------+--------------|
| Order ID            | 48953260     |
| Status              | NEW          |
| Executed Qty        | 0.00         |
| Avg Execution Price | 68000.0 USDT |
+------------------------------------+
```

---

## Structured Logs (`logs/trading.log`)

Every API request, response, and validation/system error is tracked using python's rotating file logger. Below are example log entries:

```text
2026-06-08 14:58:59,315 - [INFO] - bot.orders - Order request: MARKET BUY BTCUSDT Qty: 0.01, Price: None, StopPrice: None
2026-06-08 14:58:59,315 - [INFO] - bot.client - Sending request to Binance API: futures_create_order with args: (), kwargs: {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.01, 'type': 'MARKET'}
2026-06-08 14:58:59,515 - [INFO] - bot.client - Received response from Binance API for futures_create_order: {'orderId': 27881335, 'symbol': 'BTCUSDT', 'status': 'FILLED', 'clientOrderId': 'mock_mkt_27881335', 'price': '0.00', 'avgPrice': '65230.50', 'origQty': '0.01', 'executedQty': '0.01', 'cumQty': '0.01', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'time': 1780910939515, 'updateTime': 1780910939515}
2026-06-08 14:58:59,515 - [INFO] - bot.orders - Order successfully placed. Details: {'orderId': 27881335, 'symbol': 'BTCUSDT', 'status': 'FILLED', 'clientOrderId': 'mock_mkt_27881335', 'price': '0.00', 'avgPrice': '65230.50', 'origQty': '0.01', 'executedQty': '0.01', 'cumQty': '0.01', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'time': 1780910939515, 'updateTime': 1780910939515}

2026-06-08 14:59:16,437 - [INFO] - bot.orders - Order request: LIMIT SELL BTCUSDT Qty: 0.05, Price: 68000.0, StopPrice: None
2026-06-08 14:59:16,437 - [INFO] - bot.client - Sending request to Binance API: futures_create_order with args: (), kwargs: {'symbol': 'BTCUSDT', 'side': 'SELL', 'quantity': 0.05, 'type': 'LIMIT', 'price': '68000.0', 'timeInForce': 'GTC'}
2026-06-08 14:59:16,644 - [INFO] - bot.client - Received response from Binance API for futures_create_order: {'orderId': 48953260, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'mock_lmt_48953260', 'price': '68000.0', 'avgPrice': '0.00', 'origQty': '0.05', 'executedQty': '0.00', 'cumQty': '0.00', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'time': 1780910956644, 'updateTime': 1780910956644}
2026-06-08 14:59:16,644 - [INFO] - bot.orders - Order successfully placed. Details: {'orderId': 48953260, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'mock_lmt_48953260', 'price': '68000.0', 'avgPrice': '0.00', 'origQty': '0.05', 'executedQty': '0.00', 'cumQty': '0.00', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'time': 1780910956644, 'updateTime': 1780910956644}
```

---

## Assumptions

1. **Testnet URL Mapping**: The project strictly uses `https://testnet.binancefuture.com` as its base. In `python-binance`, calling the constructor with `testnet=True` points requests to the testnet, but this client explicitly overwrites the `FUTURES_URL` property to guarantee routing.
2. **USDT-Margined Contracts**: The bot assumes target instruments are USDT-Margined Futures contracts (e.g. BTCUSDT, ETHUSDT).
3. **Time In Force**: All non-market orders default to `GTC` (Good Till Canceled) for standard trading execution.
4. **Binance Futures Order Types**:
   - `MARKET` -> Submitted to API as type `MARKET`.
   - `LIMIT` -> Submitted to API as type `LIMIT`.
   - `STOP_LIMIT` -> Submitted to API as type `STOP` (which requires both `price` and `stopPrice` parameters).

---

## Troubleshooting

### 1. `ValidationError: Price is required for LIMIT orders.`
- **Cause**: Attempted to place a LIMIT or STOP_LIMIT order without specifying the `--price` argument.
- **Solution**: Add `--price <value>` to your command (e.g. `--price 60000`).

### 2. `AuthenticationError: Binance API credentials missing.`
- **Cause**: The `.env` file does not exist, or does not contain `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
- **Solution**: Set up a `.env` file containing your valid testnet credentials, or set `MOCK_MODE=true` to test offline.

### 3. `APIError -2015: Invalid API-key, IP, or permissions.`
- **Cause**: The keys provided in your `.env` are invalid for the Binance Futures Testnet, have expired, or do not have API permissions enabled.
- **Solution**: Double-check your API key credentials at the [Binance Futures Testnet API Key](https://testnet.binancefuture.com) portal. Make sure you are using Testnet keys, not Mainnet keys.

### 4. `NetworkError: Network connection failed.`
- **Cause**: DNS issues, active firewalls blocking ports, or internet disconnection.
- **Solution**: Verify your internet connectivity and make sure python has outbound access to `testnet.binancefuture.com` on port 443.
