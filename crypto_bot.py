from strategy1 import Strategy1
import threading
from configs import COLORS
from miner import Miner
from trader import Trader
from datetime import datetime
import time
import asyncio
from strategy import Strategy

class CryptoBot():
    REPORT_INTERVAL = 120 # 5 minutes
        
    def __init__(self):
        print(f"{COLORS.YELLOW}DPCryptoBot - v1.0{COLORS.ENDC}")
        self._miner = Miner()
        self._trader = Trader()
        self._wallet = Wallet()
        self._buyer = Buyer(self._miner, self._trader, self._wallet)
        self._seller = Seller(self._miner, self._trader, self._wallet)
    
    def __del__(self):
        for t in self._threads:
            t.join()
    
    async def buy(self):
        time.sleep(4)
        await self._buyer.execute()
        
    async def sell(self):
        time.sleep(4)
        await self._seller.execute()
        
    async def report_status(self):
        while True:
            print(f"{COLORS.YELLOW}-----STATUS-----{COLORS.ENDC}")
            print(f"{COLORS.BLUE}GMT TIME: {COLORS.ENDC}{datetime.utcnow()}")
            init_coin = await self._trader.get_initial_coin_value()
            current_coin = await self._trader.get_current_coin_value()
            print(f"{COLORS.BLUE}INITIAL USDT VALUE: {COLORS.ENDC}{init_coin}")
            print(f"{COLORS.BLUE}CURRENT USDT VALUE: {COLORS.ENDC}{current_coin}")
            profit = current_coin - init_coin
            p_profit = (profit / init_coin) * 100
            print(f"{COLORS.BLUE}PROFIT(USDT): {COLORS.ENDC}{profit}")
            print(f"{COLORS.BLUE}PROFIT(%): {COLORS.ENDC}{p_profit}")
            time.sleep(self.REPORT_INTERVAL)
    
    async def execute(self):
        async def _run_async(func):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            await func()
        self._threads = []
        report_thread = threading.Thread(target=lambda: asyncio.run(_run_async(self.report_status)))
        self._threads.append(report_thread)
        buy_thread = threading.Thread(target=lambda: asyncio.run(_run_async(self.buy)))
        self._threads.append(buy_thread)
        sell_thread = threading.Thread(target=lambda: asyncio.run(_run_async(self.sell)))
        self._threads.append(sell_thread)
        for thread in self._threads:
            thread.start()
        for thread in self._threads:
            thread.join()
        
class Buyer:
    UPDATE_COIN_LIST_INTERVAL = 3600 # 1 hour
    DELAY_BETWEEN_BUYING = 19 # 19 seconds
    NUM_COINS_TO_HOLD = 10
    AMOUNT_TO_BUY = 100 # 100 USDT
    LIMIT_POTENTIAL_COINS = 200
    
    def __init__(self, miner, trader, wallet):
        self._miner = miner
        self._trader = trader
        self._strategy = Strategy(Strategy1())
        self._wallet = wallet
        self._threads = []
        self._coin_list = None
            
    async def _run_async(self, func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await func()
        
    async def update_coin_list(self): # get current top 200 trade pairs
        while True:
            self._coin_list = await self._miner.get_top_trade_usdt_pairs(limit=self.LIMIT_POTENTIAL_COINS)
            time.sleep(self.UPDATE_COIN_LIST_INTERVAL)
            
    async def process_coins(self):
        while self._coin_list is None:
            time.sleep(0.5)
        while True:
            potential_coins = await self._strategy.analyze(self._coin_list) # return {(name, delta)}
            if len(potential_coins) < self.NUM_COINS_TO_HOLD:
                continue
            coins_holding = self._wallet.get_coins_holding()
            if coins_holding is None:
                num_coins_to_buy = self.NUM_COINS_TO_HOLD
                for coin in potential_coins:
                    if num_coins_to_buy == 0 or coin[1] < 0:
                        break
                    print(f"{COLORS.VIOLET}BUY {coin[0]}, POTENTIAL: {coin[1]}{COLORS.ENDC}")
                    order = await self._wallet.buy_by_usdt(coin[0], self.AMOUNT_TO_BUY)
                    if order is not None:
                        self._wallet.add_coin_holding(coin[0], order['origQty']) 
                        num_coins_to_buy -= 1
                cur_coins_holding = self._wallet.get_coins_holding()
                print(f"{COLORS.YELLOW}Coins holding: {cur_coins_holding}{COLORS.ENDC}")
            else:
                coins_name = [coin['name'] for coin in coins_holding]
                if (len(coins_name) < self.NUM_COINS_TO_HOLD):
                    num_coins_to_buy = self.NUM_COINS_TO_HOLD - len(coins_name)
                    for coin in potential_coins:
                        if coin[1] < 0:
                            break
                        if coin[0] not in coins_name:
                            print(f"{COLORS.VIOLET}BUY {coin[0]}, POTENTIAL: {coin[1]}{COLORS.ENDC}")
                            order = await self._wallet.buy_by_usdt(coin[0], self.AMOUNT_TO_BUY)
                            if order is not None:
                                self._wallet.add_coin_holding(coin[0], order['origQty'])
                                num_coins_to_buy -= 1
                        if num_coins_to_buy == 0:
                            break
                    cur_coins_holding = self._wallet.get_coins_holding()
                    print(f"{COLORS.YELLOW}Coins holding: {cur_coins_holding}{COLORS.ENDC}")
            time.sleep(self.DELAY_BETWEEN_BUYING)
        
    async def execute(self):
        print(f"{COLORS.GREEN}Buying thread started!{COLORS.ENDC}")
        update_coin_list_thread = threading.Thread(target=lambda: asyncio.run(self._run_async(self.update_coin_list)))
        self._threads.append(update_coin_list_thread)
        process_coin_thread = threading.Thread(target=lambda: asyncio.run(self._run_async(self.process_coins)))
        self._threads.append(process_coin_thread)
        for thread in self._threads:
            thread.start()
        for thread in self._threads:
            thread.join()
            
class Seller:
    DELAY_BETWEEN_SELLING = 17 # 17 seconds
    
    def __init__(self, miner, trader, wallet):
        self._miner = miner
        self._trader = trader
        self._strategy = Strategy(Strategy1)
        self._wallet = wallet
    
    async def sell_coins_holding(self):
        print("Selling all coins...")
        coins_holding = self._wallet.get_coins_holding()
        if coins_holding is not None:
            for coin in coins_holding:
                print(f"{COLORS.BLUE}Selling {coin['name']}...{COLORS.ENDC}")
                await self._wallet.sell(f"{coin['name']}", coin['quantity'])
                
    async def sell_all_coins(self):
        coins = await self._wallet.get_coins()
        for coin in coins:
            if coin['quantity'] == 0:
                continue
            await self._wallet.sell(f"{coin['name']}USDT", coin['quantity'])
            time.sleep(1)
            
    async def _run_async(self, func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await func()
        
    async def process_coins(self):
        # await self.sell_all_coins()
        while True:              
            coins_holding = self._wallet.get_coins_holding()
            if coins_holding is None:
                continue
            symbols = []
            for coin in coins_holding:
                symbols.append(f"{coin['name']}")
            analyzed_coins = await self._strategy.analyze(symbols)
            print(f"{COLORS.BLUE}Analyzed holding coins: {analyzed_coins}{COLORS.ENDC}")
            if analyzed_coins is None:
                continue
            for coin in analyzed_coins:
                if coin[1] < 0:
                    print(f"{COLORS.PINK}SELL {coin[0]}, POTENTIAL: {coin[1]}{COLORS.ENDC}")
                    await self._wallet.sell_coin_holding(coin[0])
                    self._wallet.delete_coin_holding(coin[0])
            time.sleep(self.DELAY_BETWEEN_SELLING)
            
    async def handle_signal(self):
        print("Handling...")
            
    async def execute(self):
        print(f"{COLORS.GREEN}Selling thread started!{COLORS.ENDC}")
        self._threads = []
        process_coin_thread = threading.Thread(target=lambda: asyncio.run(self._run_async(self.process_coins)))
        self._threads.append(process_coin_thread)
        for thread in self._threads:
            thread.start()
        for thread in self._threads:
            thread.join()
            
class Wallet:
    _instance = None
    
    def __init__(self):
        self._miner = Miner()
        self._trader = Trader()
        self._coins = None
        self._coins_holding = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_coins(self):
        if self._coins is None:
            coins = await self._trader.get_balance()
            self._coins = [{"name": coin['asset'], "quantity": float(coin['free'])} for coin in coins if (coin['asset'] != 'USDT' and float(coin['free']) != 0)]
        return self._coins
    
    async def update_coins(self):
        coins = await self._trader.get_balance()
        self._coins = [{"name": coin['asset'], "quantity": float(coin['free'])} for coin in coins if (coin['asset'] != 'USDT' and float(coin['free']) != 0)]
    
    async def get_usdt(self):
        coins = await self._trader.get_balance()
        for coin in coins:
            if coin['asset'] == 'USDT':
                return coin['free']
            
    async def buy_by_quantity(self, coin, quantity):
        params = {
            "symbol": f"{coin}",
            "side": "BUY",
            "type": "MARKET",
            "quantity": quantity
        }
        return await self._trader.place_order(params)
        
    async def buy_by_usdt(self, coin, usdt):
        params = {
            "symbol": f"{coin}",
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": usdt
        }
        return await self._trader.place_order(params)

            
    async def sell(self, symbol, quantity):
        params = {
            "symbol": f"{symbol}",
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity
        }
        return await self._trader.place_order(params)
    
    async def sell_all(self, symbol):
        await self.update_coins()
        coins = await self.get_coins()
        quantity = 0
        for coin in coins:
            coin_name = coin['name'].replace('USDT', '')
            if coin_name == coin:
                quantity = coin['quantity']
                break
        if quantity == 0:
            print(f"{COLORS.RED}No {symbol} to sell{COLORS.ENDC}")
            return None
        params = {
            "symbol": f"{symbol}",
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity
        }
        return await self._trader.place_order(params)
    
    async def sell_coin_holding(self, symbol):
        coins_holding = self.get_coins_holding()
        if coins_holding is None:
            return None
        for coin in coins_holding:
            if coin['name'] == symbol:
                params = {
                    "symbol": f"{symbol}",
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": coin['quantity']
                }
                return await self._trader.place_order(params)
        return None
    
    def add_coin_holding(self, coin, quantity):
        if self._coins_holding is None:
            self._coins_holding = []
        self._coins_holding.append({"name": coin, "quantity": quantity})
        
    def delete_coin_holding(self, symbol):
        if self._coins_holding is None:
            return None
        for coin in self._coins_holding:
            if coin['name'] == symbol:
                self._coins_holding.remove(coin)
                break
        if len(self._coins_holding) == 0:
            self._coins_holding = None
    
    def update_coin_holding(self, coin, quantity):
        if self._coins_holding is None:
            self.add_coin_holding(coin, quantity)
        founded = False
        for coin in self._coins_holding:
            if coin['name'] == coin:
                coin['quantity'] = quantity
                founded = True
                break
        if not founded:
            self.add_coin_holding(coin, quantity)
    
    def get_coins_holding(self):
        return self._coins_holding 
    
if __name__ == "__main__":
    bot = CryptoBot()
    asyncio.run(bot.execute())
