import asyncio
import websockets
import json
import threading
from configs import COLORS
import time
import signal
from random import randint
from binance.spot import Spot

BASE_STREAM_ENDPOINT = "wss://stream.binance.com:9443/ws"  
BASE_WS_ENDPOINT = "wss://ws-api.binance.com:443/ws-api/v3"


class DataStream:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._data = {}
        self._endpoints = {}
        self._connections = {}
        
        signal.signal(signal.SIGINT, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        self.__del__()
        raise KeyboardInterrupt

    async def __del__(self):
        await self.disconnect_all()
        
    async def disconnect(self, endpoint):
        self._data.pop(endpoint, None)
        self._endpoints.pop(endpoint, None)
        connection = self._connections.pop(endpoint, None)
        if connection:
            connection.join()

    async def disconnect_all(self):
        for endpoint in list(self._endpoints.keys()):
            await self.disconnect(endpoint)

    async def connect(self, endpoint):
        if endpoint not in self._endpoints:
            self._endpoints[endpoint] = endpoint
            self._connections[endpoint] = threading.Thread(target=self._run_connection, args=(endpoint,))
            self._connections[endpoint].start()

    def _run_connection(self, endpoint):
        uri = f"{BASE_STREAM_ENDPOINT}/{endpoint}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._listen_to_websocket(uri, endpoint))

    async def _listen_to_websocket(self, uri, endpoint):
        async with websockets.connect(uri) as ws:
            print(f"{COLORS.GREEN}Connected to {endpoint}!{COLORS.ENDC}")
            while True:
                try:
                    message = await ws.recv()
                    self._data[endpoint] = json.loads(message)
                except websockets.exceptions.ConnectionClosed:
                    print(f"{COLORS.RED}Connection to {endpoint} closed unexpectedly!{COLORS.ENDC}")
                    break
                except Exception as e:
                    print(f"{COLORS.RED}An error occurred: {e}{COLORS.ENDC}")
                    break

    async def get_data(self, endpoint):
        if endpoint not in self._data:
            self._data[endpoint] = None
            await self.connect(endpoint)
        return self._data[endpoint]
    
    
    
class WebSocketClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass    
    
    async def get(self, method, params=None):
        async with websockets.connect(BASE_WS_ENDPOINT) as ws:
            print(f"{COLORS.GREEN}Connected to {BASE_WS_ENDPOINT}!{COLORS.ENDC}")
            req = {
                "id": randint(1, 1000),
                "method": method,
                "params": params
            }
            await ws.send(json.dumps(req))
            res = await ws.recv()
            return json.loads(res)

class Miner:    
    _instance = None
    
    def __init__(self):
        self._stream = DataStream()
        self._ws = WebSocketClient()
        self.client = Spot()
        print(f"{COLORS.GREEN}Connected to HTTP Server: {self.client.base_url}{COLORS.ENDC}")
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    async def connect(self, endpoint):
        await self._stream.connect(endpoint)
        
    async def check_connection(self, endpoint):
        if (self._stream._data[endpoint] is None):
            return False
        return True
        
    async def get_time(self):
        return self.client.time()
            
    async def get_trade(self, symbol):
        endpoint = f"{symbol.lower()}@trade"    
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_depth(self, symbol):
        endpoint = f"{symbol.lower()}@depth"
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_aggTrade(self, symbol):
        endpoint = f"{symbol.lower()}@aggTrade"
        data = await self._stream.get_data(endpoint)
        return data
        
    async def get_kline(self, symbol, interval): # interval = {1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M}
        endpoint = f"{symbol.lower()}@kline_{interval}"
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_ticker(self, symbol, interval): # interval = {1h, 4h, 1d}
        endpoint = f"{symbol.lower()}@ticker_{interval}"
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_avgPrice(self, symbol):
        endpoint = f"{symbol.lower()}@avgPrice"
        data = await self._stream.get_data(endpoint)
        return data
        # {
        #     "e": "avgPrice",          // Event type
        #     "E": 1693907033000,       // Event time
        #     "s": "BTCUSDT",           // Symbol
        #     "i": "5m",                // Average price interval
        #     "w": "25776.86000000",    // Average price
        #     "T": 1693907032213        // Last trade time
        # }
            
    async def get_all_ticker(self, interval): # interval = {1h, 4h, 1d}
        endpoint = f"!ticker_{interval}@arr"
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_bookTicker(self, symbol):
        endpoint = f"{symbol.lower()}@bookTicker"
        data = await self._stream.get_data(endpoint)
        return data
    
    async def get_ws_data(self, method, params=None):
        data = await self._ws.get(method, params)
        return data
    
    async def get_all_usdt_pairs(self):
        exchange_info = self.client.ticker_24hr()
        usdt_pairs = [symbol['symbol'] for symbol in exchange_info if symbol['symbol'].endswith('USDT')]
        return usdt_pairs
        
    async def get_top_trade_usdt_pairs(self, limit=100):
        exchange_info = self.client.ticker_24hr()
        usdt_pairs = [symbol for symbol in exchange_info if symbol['symbol'].endswith('USDT')]
        sorted_usdt_pairs = sorted(usdt_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
        top_usdt_pairs = [pair['symbol'] for pair in sorted_usdt_pairs[:limit]]
        return top_usdt_pairs

async def main():
    miner = Miner()
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'UNIUSDT', 'LTCUSDT', 'LINKUSDT']
    while True:
        for symbol in symbols:            
            kline = await miner.get_kline(symbol, '1m')
            print(f"{COLORS.YELLOW}{symbol} KLINE: {kline}{COLORS.ENDC}")
        print("\n")
        time.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
