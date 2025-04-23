from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    def scrape(self) -> List[Dict]:
        pass
