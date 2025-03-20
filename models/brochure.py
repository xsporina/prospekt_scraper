from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Brochure:    
    title: str
    thumbnail: str
    shop_name: str
    valid_from: Optional[str]
    valid_to: Optional[str]
    parsed_time: Optional[str]

    def __post_init__(self):
        if self.parsed_time is None:
            self.parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")