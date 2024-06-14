# DPCryptoBot

Welcome to DPCryptoBot! This project is a Python-based cryptocurrency trading bot via `Binance API`.

## Features
- Real-time market data analysis
- Automated & customizable trading strategies

## Project Structure

### crypto_bot.py

#### Components:
1. **CryptoBot**: The main class that initializes and coordinates the various components of the bot. It manages the buying, selling, and reporting tasks.
2. **Buyer**: Handles the process of selecting and buying cryptocurrencies based on a strategy. It updates the list of potential coins to buy and executes buy orders.
3. **Seller**: Manages the selling of cryptocurrencies. It evaluates the holdings and executes sell orders based on the analysis of potential profits or losses.
4. **Wallet**: Manages the bot's wallet, keeping track of the current holdings and executing buy/sell orders through the trader component.
5. **Miner** and **Trader**: These components interact with the external services to gather market data and execute trades.

#### Key Features:
- **Concurrency**: The bot uses Python's `asyncio` library along with threading to run multiple tasks in parallel. This ensures that tasks such as market data fetching, buying, and selling can occur simultaneously without blocking each other.
- **Strategy-Driven**: The buying and selling decisions are based on a predefined strategy (`Strategy1`). This can be customized or extended to implement different trading strategies.
- **Reporting**: The bot periodically reports its status, including the initial and current value of its holdings, and calculates the profit in both absolute and percentage terms.

### miner.py
This module provides classes to handle real-time cryptocurrency data streaming and interaction with the Binance API. 

#### Components:
- **DataStream**: Manages WebSocket connections to Binance for streaming data.
- **WebSocketClient**: Handles WebSocket requests to Binance's API.
- **Miner**: Provides various methods to fetch market data using both WebSocket streams and HTTP requests.

#### Key Features:
- **Singleton Pattern**: Ensures only one instance of the class is created.
- **Thread-Safe**: Uses threading locks to ensure thread safety.
- **Signal Handling**: Gracefully handles interrupts to close connections properly.
- **WebSocket Connections**: Manages connections and listens for messages from Binance's WebSocket API.


### trader.py
The `Trader` class is designed for managing cryptocurrency trades, including buying, selling, and fetching account balances using the Binance API. It utilizes environment variables for API credentials and provides methods to interact with Binance's trading functionalities.

#### Key Features:
- **Singleton Pattern**: Ensures only one instance of the class is created.
- **Authentication**: Authenticates with Binance API using API keys.
- **Balance Management**: Fetches account balances and calculates the total value in USDT.
- **Trading Operations**: Places test orders and real orders for buying and selling cryptocurrencies.
- **Profit Calculation**: Calculates the profit made based on the initial and current coin values.

### strategy.py
This module serves as an interface for strategies applied to the bot.

### strategy1.py
The `Strategy1` class extends the abstract `Strategy` class to implement a specific asynchronous strategy for analyzing coins. It interacts with a `Miner` instance to fetch data and compute delta values for coins based on their K-line data.

**Note:** This code provides a simple example of an analyzing algorithm. Users are encouraged to implement and test other strategies to trade effectively.

### configs.py
This module contains the configuration settings for DPCryptoBot.

#### Key Features:
- **API Keys**: Store your Binance API keys here for authentication.

**Note**: It is vital to store your API Key and API Secret to your local `.env` file.




## Installation

To get started with DPCryptoBotPython, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/your-username/DPCryptoBot.git
    ```

2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Configure the bot:
    - Open the `config.py` file and enter your API keys and trading preferences.
    - Customize the trading strategies in the `strategies.py` file.

4. Run the bot:
    ```
    python crypto_bot.py
    ```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact
If you have any questions or need further assistance, feel free to contact me at [leducphu.contact@gmail.com](mailto:leducphu.contact@gmail.com).

Happy trading with DPCryptoBot!
