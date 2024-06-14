import os
import asyncio
import binance
import binance.error
from dotenv import load_dotenv
from binance.spot import Spot
from configs import COLORS
from configs import KEY

# Load variables from .env file
load_dotenv()

# Access API key and secret from environment
API_KEY = KEY.API_KEY
API_SECRET = KEY.API_SECRET

BASE_URL = KEY.BASE_URL

class Trader: # this class serves buying, selling, and getting balance of the account
    _instance = None
    
    def __init__(self):
        self._client = None
        self._initial_coin_value = None
        self._authenticate()
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _authenticate(self):
        try:
            print(f"{COLORS.GREEN}Authenticating with API Key: {API_KEY}{COLORS.ENDC}")
            self._client = Spot(base_url=BASE_URL, api_key=API_KEY, api_secret=API_SECRET)
            print(f"{COLORS.GREEN}Authenticated successfully!{COLORS.ENDC}")
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
            print(f"{COLORS.RED}Authentication failed! Please check your API key and secret!{COLORS.ENDC}")
    
    async def get_balance(self):
        try:
            return self._client.account()['balances']
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
    
    async def get_current_coin_value(self):
        try:
            symbols = []
            quantity = []
            total_usdt = 0
            balances = await self.get_balance()
            for coin in balances:
                if coin['asset'] == 'USDT':
                    total_usdt = float(coin['free'])
                    continue
                symbols.append(coin['asset'] + 'USDT')
                quantity.append(coin['free'])
            
            prices = self._client.ticker_price()
            
            for price in prices:
                if price['symbol'] in symbols:
                    index = symbols.index(price['symbol'])
                    total_usdt += float(price['price']) * float(quantity[index])
            
            return total_usdt
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
            
    async def get_asset(self, symbol):
        try:
            balances = await self.get_balance()
            for coin in balances:
                if coin['asset'] == symbol:
                    return coin
            return None
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
            
    async def test_order(self, params=None):
        try:
            if (params['side'] == 'BUY'):
                print(f"TESTING {COLORS.YELLOW}BUY {params['symbol']}{COLORS.ENDC} at {params['price']} with {params['quantity']} quantity")
            elif (params['side'] == 'SELL'):
                print(f"TESTING {COLORS.BLUE}SELL {params['symbol']}{COLORS.ENDC} at {params['price']} with {params['quantity']} quantity")
            print(params)  
            return self._client.new_order_test(**params)
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
            
    async def place_order(self, params):
        try:
            if (params['side'] == 'BUY'):
                print(f"{COLORS.BLUE}BUY{COLORS.ENDC} {COLORS.ORANGE} {params['symbol']}{COLORS.ENDC}")
            elif (params['side'] == 'SELL'):
                print(f"{COLORS.RED}SELL{COLORS.ENDC} {COLORS.ORANGE}{params['symbol']}{COLORS.ENDC} with {params['quantity']} quantity")
            print(params)    
            return self._client.new_order(**params)
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")
            return None
            
    async def get_initial_coin_value(self):
        if self._initial_coin_value is None:
            self._initial_coin_value = await self.get_current_coin_value()
            return self._initial_coin_value
        return self._initial_coin_value
            
    async def get_profit(self):
        try:
            current_value = await self.get_current_coin_value()
            initial_value = await self.get_initial_coin_value()
            profit = current_value - initial_value
            return profit, (profit / initial_value) * 100
        except binance.error.ClientError as e:
            print(f"{COLORS.RED}{e}{COLORS.ENDC}")

async def main():
    trader1 = Trader()
    value = await trader1.get_total_value()
    print(value)

if __name__ == '__main__':
    asyncio.run(main())
