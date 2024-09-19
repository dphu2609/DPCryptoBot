import os
from dotenv import load_dotenv

load_dotenv()

class KEY:
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    BASE_URL = 'https://testnet.binance.vision'


class COLORS:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    ORANGE = '\033[33m'
    VIOLET = '\033[35m'
    PINK = '\033[95m'
    ENDC = '\033[0m'
    

