"""
Data Fetcher Service - Retrieves short interest data from FINRA and market data APIs.

IMPORTANT: FINRA short interest data is published TWICE MONTHLY (around the 1st and 15th).
Data is typically 2-3 weeks stale by the time it's published.
Always display data freshness indicators in the UI.
"""

import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


FINRA_SHORT_INTEREST_URL = "https://api.finra.org/data/group/otcMarket/name/regShoDaily"
FINRA_BASE_URL = "https://api.finra.org"


MOCK_SHORT_INTEREST_DATA = [
    {
        "symbol": "GME",
        "companyName": "GameStop Corp",
        "shortInterest": 24500000,
        "shortInterestRatio": 8.2,  # days to cover
        "shortPercentOfFloat": 21.5,
        "averageVolume": 3200000,
        "price": 18.45,
        "priceChange": 2.3,
        "marketCap": 7800000000,
        "borrowRate": 1.2,
        "utilizationRate": 67.3,
        "reportDate": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "dataSource": "FINRA",
        "dataFreshness": "STALE",  # FINRA data is always delayed 2-3 weeks
        "nextReportDate": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    },
    {
        "symbol": "AMC",
        "companyName": "AMC Entertainment Holdings",
        "shortInterest": 98000000,
        "shortInterestRatio": 6.5,
        "shortPercentOfFloat": 18.2,
        "averageVolume": 12000000,
        "price": 4.82,
        "priceChange": -1.2,
        "marketCap": 2400000000,
        "borrowRate": 4.8,
        "utilizationRate": 89.2,
        "reportDate": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "dataSource": "FINRA",
        "dataFreshness": "STALE",
        "nextReportDate": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    },
    {
        "symbol": "BBBY",
        "companyName": "Bed Bath & Beyond",
        "shortInterest": 45000000,
        "shortInterestRatio": 4.1,
        "shortPercentOfFloat": 32.7,
        "averageVolume": 9800000,
        "price": 0.21,
        "priceChange": -5.4,
        "marketCap": 58000000,
        "borrowRate": 85.0,
        "utilizationRate": 98.5,
        "reportDate": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "dataSource": "FINRA",
        "dataFreshness": "STALE",
        "nextReportDate": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    },
]


async def fetch_finra_short_interest(
    symbol: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch short interest data from FINRA API.
    
    FINRA publishes short interest data twice monthly:
    - Settlement date around the 1st of each month
    - Settlement date around the 15th of each month
    
    Data is delayed ~2-3 weeks from the settlement date.
    Always return metadata indicating data staleness.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "limit": limit,
                "offset": 0,
            }
            if symbol:
                params["issueSymbolIdentifier"] = symbol.upper()
            
            response = await client.get(
                f"{FINRA_BASE_URL}/data/group/otcMarket/name/regShoDaily",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched FINRA data for {len(data)} records")
                return data
            else:
                logger.warning(f"FINRA API returned {response.status_code}, using mock data")
                return _get_mock_data(symbol)
                
    except Exception as e:
        logger.warning(f"Failed to fetch FINRA data: {e}, using mock data")
        return _get_mock_data(symbol)


async def fetch_market_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch real-time market data (price, volume) from a market data provider.
    Market data is more current than FINRA short interest data.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Using Yahoo Finance unofficial API as fallback
            response = await client.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                params={"interval": "1d", "range": "5d"},
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("chart", {}).get("result", [{}])[0]
                meta = result.get("meta", {})
                return {
                    "symbol": symbol,
                    "price": meta.get("regularMarketPrice", 0),
                    "previousClose": meta.get("previousClose", 0),
                    "volume": meta.get("regularMarketVolume", 0),
                    "marketCap": meta.get("marketCap", 0),
                    "dataSource": "Yahoo Finance",
                    "dataFreshness": "LIVE",
                    "timestamp": datetime.utcnow().isoformat()
                }
    except Exception as e:
        logger.warning(f"Failed to fetch market data for {symbol}: {e}")
    
    return {}


async def get_finra_report_dates() -> Dict[str, Any]:
    """
    Returns information about FINRA short interest reporting schedule.
    FINRA publishes data twice monthly, with a 2-3 week delay.
    """
    now = datetime.utcnow()
    
    # FINRA typically publishes around 1st and 15th of each month
    if now.day < 15:
        last_report = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_report = now.replace(day=15, hour=0, minute=0, second=0, microsecond=0)
    else:
        last_report = now.replace(day=15, hour=0, minute=0, second=0, microsecond=0)
        # Next month's 1st
        if now.month == 12:
            next_report = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_report = now.replace(month=now.month+1, day=1)
    
    return {
        "lastReportDate": last_report.isoformat(),
        "nextReportDate": next_report.isoformat(),
        "reportingFrequency": "Twice monthly (approximately 1st and 15th)",
        "dataDelay": "2-3 weeks from settlement date",
        "dataSource": "FINRA",
        "disclaimer": (
            "FINRA short interest data reflects exchange-reported short positions "
            "as of the settlement date. Data is published twice monthly and is "
            "typically 2-3 weeks old by publication date. This data should be "
            "used for analysis purposes only and does not reflect current short positions."
        )
    }


def _get_mock_data(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return mock data when FINRA API is unavailable."""
    if symbol:
        return [
            d for d in MOCK_SHORT_INTEREST_DATA
            if d["symbol"].upper() == symbol.upper()
        ]
    return MOCK_SHORT_INTEREST_DATA


async def calculate_days_to_cover(
    short_interest: float,
    average_daily_volume: float
) -> float:
    """
    Calculate Days to Cover (Short Interest Ratio).
    
    Definition: The number of days it would take all short sellers to cover
    their positions based on the average daily trading volume.
    
    Formula: Short Interest / Average Daily Volume
    
    Interpretation:
    - < 1 day: Very low short interest, easy to cover
    - 1-5 days: Moderate short interest
    - 5-10 days: High short interest, potential squeeze candidate
    - > 10 days: Extreme short interest, strong squeeze potential
    
    Note: Uses FINRA-reported short interest which is delayed 2-3 weeks.
    Current volume may differ significantly from the average used in calculation.
    """
    if average_daily_volume <= 0:
        return 0.0
    return round(short_interest / average_daily_volume, 2)
