import os

class KEY:
    API_KEY = os.getenv('YOUR_API_KEY')
    API_SECRET = os.getenv('YOUR_API_SECRET')
    BASE_URL = 'https://api.binance.com'


class COLORS:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    ORANGE = '\033[33m'
    VIOLET = '\033[35m'
    PINK = '\033[95m'
    ENDC = '\033[0m'
    

