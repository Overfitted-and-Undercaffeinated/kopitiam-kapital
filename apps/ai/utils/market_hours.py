"""
Market hours tracking for different exchanges
Prevents wasted API calls during closed hours
"""
from datetime import datetime, time, timedelta
from typing import Dict, List
import pytz
import logging

logger = logging.getLogger(__name__)

class MarketHours:
    """Track market hours for different exchanges"""
    
    SCHEDULES = {
        'SGX': {
            'name': 'Singapore Exchange',
            'timezone': 'Asia/Singapore',
            'open': time(9, 0),
            'close': time(17, 0),
            'days': [0, 1, 2, 3, 4],  # Monday=0 to Friday=4
            'lunch_break': (time(12, 0), time(13, 0))  # Optional lunch break
        },
        'NYSE': {
            'name': 'New York Stock Exchange',
            'timezone': 'America/New_York',
            'open': time(9, 30),
            'close': time(16, 0),
            'days': [0, 1, 2, 3, 4],
            'lunch_break': None
        },
        'NASDAQ': {
            'name': 'NASDAQ',
            'timezone': 'America/New_York',
            'open': time(9, 30),
            'close': time(16, 0),
            'days': [0, 1, 2, 3, 4],
            'lunch_break': None
        },
        'LSE': {
            'name': 'London Stock Exchange',
            'timezone': 'Europe/London',
            'open': time(8, 0),
            'close': time(16, 30),
            'days': [0, 1, 2, 3, 4],
            'lunch_break': None
        },
        'HKEX': {
            'name': 'Hong Kong Exchange',
            'timezone': 'Asia/Hong_Kong',
            'open': time(9, 30),
            'close': time(16, 0),
            'days': [0, 1, 2, 3, 4],
            'lunch_break': (time(12, 0), time(13, 0))
        },
        'CRYPTO': {
            'name': 'Cryptocurrency Markets',
            'timezone': 'UTC',
            'open': time(0, 0),
            'close': time(23, 59),
            'days': [0, 1, 2, 3, 4, 5, 6],  # 24/7
            'lunch_break': None
        }
    }
    
    def is_market_open(self, exchange: str, check_time: datetime = None) -> bool:
        """
        Check if a specific market is currently open
        
        Args:
            exchange: Exchange code (SGX, NYSE, etc.)
            check_time: Optional specific time to check (default: now)
        
        Returns:
            True if market is open, False otherwise
        """
        if exchange not in self.SCHEDULES:
            logger.warning(f"Unknown exchange: {exchange}. Assuming open.")
            return True
        
        schedule = self.SCHEDULES[exchange]
        tz = pytz.timezone(schedule['timezone'])
        
        if check_time is None:
            now = datetime.now(tz)
        else:
            now = check_time.astimezone(tz)
        
        # Check day of week
        if now.weekday() not in schedule['days']:
            logger.debug(f"{exchange} closed (weekend/holiday)")
            return False
        
        # Check time
        current_time = now.time()
        
        if current_time < schedule['open'] or current_time > schedule['close']:
            logger.debug(f"{exchange} closed (outside trading hours)")
            return False
        
        # Check lunch break
        if schedule['lunch_break']:
            lunch_start, lunch_end = schedule['lunch_break']
            if lunch_start <= current_time <= lunch_end:
                logger.debug(f"{exchange} closed (lunch break)")
                return False
        
        return True
    
    def get_active_markets(self, check_time: datetime = None) -> List[str]:
        """
        Get list of currently open markets
        
        Returns:
            List of exchange codes that are currently open
        """
        active = []
        
        for exchange in self.SCHEDULES.keys():
            if self.is_market_open(exchange, check_time):
                active.append(exchange)
        
        return active
    
    def get_next_open_time(self, exchange: str) -> datetime:
        """
        Get the next opening time for a market
        
        Returns:
            Datetime of next market open
        """
        if exchange not in self.SCHEDULES:
            return datetime.now()
        
        schedule = self.SCHEDULES[exchange]
        tz = pytz.timezone(schedule['timezone'])
        now = datetime.now(tz)
        
        # If currently open, return now
        if self.is_market_open(exchange):
            return now
        
        # Find next trading day
        next_open = now.replace(
            hour=schedule['open'].hour,
            minute=schedule['open'].minute,
            second=0,
            microsecond=0
        )
        
        # If past today's open time, move to next day
        if now.time() > schedule['open']:
            next_open += timedelta(days=1)
        
        # Skip to next valid trading day
        while next_open.weekday() not in schedule['days']:
            next_open += timedelta(days=1)
        
        return next_open
    
    def get_market_info(self, exchange: str) -> Dict:
        """Get full market information"""
        if exchange not in self.SCHEDULES:
            return {}
        
        schedule = self.SCHEDULES[exchange]
        tz = pytz.timezone(schedule['timezone'])
        now = datetime.now(tz)
        
        return {
            'exchange': exchange,
            'name': schedule['name'],
            'timezone': schedule['timezone'],
            'is_open': self.is_market_open(exchange),
            'local_time': now.strftime('%H:%M:%S'),
            'open_time': schedule['open'].strftime('%H:%M'),
            'close_time': schedule['close'].strftime('%H:%M'),
            'next_open': self.get_next_open_time(exchange).isoformat()
        }

# Global instance
market_hours = MarketHours()

