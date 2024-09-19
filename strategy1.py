from strategy import Strategy
from configs import COLORS
from miner import Miner

class Strategy1(Strategy):
    _instance = None  # Class variable to hold the singleton instance
    KLINE_INTERVAL = "3m"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Strategy1, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            print(f"{COLORS.GREEN}Applying STRATEGY 1{COLORS.ENDC}")
            super().__init__()
            self._miner = Miner()
            self._initialized = True  # Avoid reinitialization
        
    async def sort_coins_by_kline(self, coins):
        while True:
            legit = False
            for coin in coins:
                kline = await self._miner.get_kline(coin, self.KLINE_INTERVAL)
                if kline is None:
                    break
                legit = True
            if legit:
                break   
        result = []
        for coin in coins:
            kline = await self._miner.get_kline(coin, self.KLINE_INTERVAL)
            if kline is None:
                continue
            delta = ((float(kline['k']['c']) - float(kline['k']['o'])) / float(kline['k']['o'])) * 100
            result.append((coin, delta))
        return sorted(result, key=lambda x: x[1], reverse=True)

    async def analyze(self, coins):
        if len(coins) == 0:
            return None
        sorted_coins = await self.sort_coins_by_kline(coins)  # result is (name, delta)
        return sorted_coins