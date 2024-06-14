from abc import abstractmethod

class Strategy:    
    @abstractmethod
    async def analyze(self, coins):
        pass