from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models import AlertRecord

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    symbol: str
    alert_type: str  # SCORE_THRESHOLD | SHORT_INCREASE | DAYS_TO_COVER
    threshold: float


class AlertResponse(BaseModel):
    id: str
    symbol: str
    type: str
    threshold: float
    active: bool
    createdAt: str


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(db: Session = Depends(get_db)):
    """List all configured price/score alerts."""
    alerts = db.query(AlertRecord).filter(AlertRecord.active == True).all()
    return [
        AlertResponse(
            id=str(a.id),
            symbol=a.symbol,
            type=a.alert_type,
            threshold=a.threshold,
            active=a.active,
            createdAt=a.created_at.isoformat(),
        )
        for a in alerts
    ]


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert for a ticker."""
    valid_types = ["SCORE_THRESHOLD", "SHORT_INCREASE", "DAYS_TO_COVER"]
    if payload.alert_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"alert_type must be one of {valid_types}")

    alert = AlertRecord(
        id=str(uuid.uuid4()),
        symbol=payload.symbol.upper(),
        alert_type=payload.alert_type,
        threshold=payload.threshold,
        active=True,
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return AlertResponse(
        id=str(alert.id),
        symbol=alert.symbol,
        type=alert.alert_type,
        threshold=alert.threshold,
        active=alert.active,
        createdAt=alert.created_at.isoformat(),
    )


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """Deactivate/delete an alert."""
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.active = False
    db.commit()
