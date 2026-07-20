from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import ShortInterestRecord, SqueezeScoreRecord
from ..squeeze_score import calculate_squeeze_score

router = APIRouter(prefix="/api/v1/tickers", tags=["tickers"])


@router.get("/summary")
async def get_tickers_summary(
    min_score: Optional[int] = Query(None, ge=0, le=100),
    min_short_percent: Optional[float] = Query(None, ge=0, le=100),
    sort_by: str = Query("score", regex="^(score|shortPercent|daysToCover|symbol)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Get summary of all tracked tickers with short interest data and squeeze scores.

    NOTE: Short interest data sourced from FINRA and published twice monthly.
    Data may be 1-14 days stale. Days-to-Cover = Short Interest / Avg 20-Day Volume.
    """
    records = db.query(ShortInterestRecord).all()

    result = []
    for record in records:
        score_record = (
            db.query(SqueezeScoreRecord)
            .filter(SqueezeScoreRecord.symbol == record.symbol)
            .order_by(SqueezeScoreRecord.calculated_at.desc())
            .first()
        )

        if not score_record:
            score_data = calculate_squeeze_score(record)
        else:
            score_data = score_record

        ticker_data = {
            "symbol": record.symbol,
            "companyName": record.company_name,
            "price": record.price or 0.0,
            "priceChange": record.price_change or 0.0,
            "priceChangePercent": record.price_change_pct or 0.0,
            "borrowRate": record.borrow_rate or 0.0,
            "marketCap": record.market_cap or 0,
            "floatShares": record.float_shares or 0,
            "shortData": {
                "symbol": record.symbol,
                "companyName": record.company_name,
                "shortInterest": record.short_interest,
                "shortPercentOfFloat": record.short_percent_of_float,
                "daysTocover": record.days_to_cover,
                "shortPercentOfSharesOutstanding": record.short_pct_of_shares_outstanding,
                "settleDate": record.settle_date.isoformat() if record.settle_date else None,
                "dataSource": "FINRA",
                "dataFreshness": record.data_freshness,
                "nextUpdateDate": record.next_update_date.isoformat() if record.next_update_date else None,
            },
            "squeezeScore": {
                "symbol": record.symbol,
                "score": getattr(score_data, 'score', 0),
                "grade": getattr(score_data, 'grade', 'F'),
                "components": {
                    "shortInterestScore": getattr(score_data, 'si_score', 0),
                    "daysToCoverScore": getattr(score_data, 'dtc_score', 0),
                    "borrowCostScore": getattr(score_data, 'borrow_score', 0),
                    "momentumScore": getattr(score_data, 'momentum_score', 0),
                    "floatScore": getattr(score_data, 'float_score', 0),
                },
                "lastCalculated": datetime.utcnow().isoformat(),
            },
        }
        result.append(ticker_data)

    # Filter
    if min_score is not None:
        result = [t for t in result if t["squeezeScore"]["score"] >= min_score]
    if min_short_percent is not None:
        result = [t for t in result if t["shortData"]["shortPercentOfFloat"] >= min_short_percent]

    # Sort
    sort_key_map = {
        "score": lambda t: t["squeezeScore"]["score"],
        "shortPercent": lambda t: t["shortData"]["shortPercentOfFloat"],
        "daysToCover": lambda t: t["shortData"]["daysTocover"],
        "symbol": lambda t: t["symbol"],
    }
    result.sort(key=sort_key_map.get(sort_by, sort_key_map["score"]), reverse=(sort_order == "desc"))

    return result[:limit]


@router.get("/{symbol}")
async def get_ticker_detail(symbol: str, db: Session = Depends(get_db)):
    """Get detailed short interest data for a specific ticker."""
    record = (
        db.query(ShortInterestRecord)
        .filter(ShortInterestRecord.symbol == symbol.upper())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
    return record
