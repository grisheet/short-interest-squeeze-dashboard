"""SQLAlchemy ORM models for all core database tables."""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    Text, ForeignKey, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class Role(str, enum.Enum):
    analyst = "analyst"
    admin = "admin"


class AlertType(str, enum.Enum):
    squeeze_score = "squeeze_score"
    borrow_fee = "borrow_fee"
    utilization = "utilization"
    si_pct_float = "si_pct_float"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.analyst)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    watchlists = relationship("Watchlist", back_populates="user")
    alerts = relationship("Alert", back_populates="user")


class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    market_cap = Column(Float)
    shares_outstanding = Column(Float)
    float_shares = Column(Float)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    short_interest_records = relationship("ShortInterest", back_populates="ticker")
    borrow_records = relationship("BorrowMetrics", back_populates="ticker")
    price_records = relationship("PriceVolume", back_populates="ticker")
    options_records = relationship("OptionsData", back_populates="ticker")
    squeeze_scores = relationship("SqueezeScore", back_populates="ticker")
    ml_features = relationship("MLFeature", back_populates="ticker")


class ShortInterest(Base):
    """FINRA-reported short interest (twice-monthly, stale)."""
    __tablename__ = "short_interest"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    report_date = Column(Date, nullable=False)
    settlement_date = Column(Date)
    short_interest = Column(Float)  # shares
    si_pct_float = Column(Float)  # percent of float
    days_to_cover = Column(Float)  # SI / ADV
    adv_30d = Column(Float)  # average daily volume 30-day
    is_stale = Column(Boolean, default=True)  # always True for FINRA data
    source = Column(String(50), default="FINRA")
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="short_interest_records")
    __table_args__ = (UniqueConstraint("ticker_id", "report_date", name="uq_si_ticker_date"),)


class BorrowMetrics(Base):
    """Securities lending data (near-realtime)."""
    __tablename__ = "borrow_metrics"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    shares_on_loan = Column(Float)
    cost_to_borrow = Column(Float)  # annualized %
    borrow_fee = Column(Float)  # daily %
    utilization = Column(Float)  # % of lendable supply
    lendable_shares = Column(Float)
    source = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="borrow_records")
    __table_args__ = (UniqueConstraint("ticker_id", "as_of_date", "source", name="uq_borrow_ticker_date_src"),)


class PriceVolume(Base):
    __tablename__ = "price_volume"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    trade_date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    vwap = Column(Float)
    adv_30d = Column(Float)
    volume_ratio = Column(Float)  # volume / adv_30d
    rsi_14 = Column(Float)
    momentum_5d = Column(Float)  # 5-day price return
    momentum_20d = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="price_records")
    __table_args__ = (UniqueConstraint("ticker_id", "trade_date", name="uq_pv_ticker_date"),)


class OptionsData(Base):
    __tablename__ = "options_data"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    strike = Column(Float)
    option_type = Column(String(4))  # call | put
    open_interest = Column(Integer)
    volume = Column(Integer)
    implied_volatility = Column(Float)
    delta = Column(Float)
    gamma = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="options_records")


class OptionsAggregate(Base):
    """Pre-computed options aggregates per ticker per date."""
    __tablename__ = "options_aggregates"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    call_oi_total = Column(Float)
    put_oi_total = Column(Float)
    put_call_ratio = Column(Float)
    gamma_exposure = Column(Float)  # net dealer gamma
    net_delta = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("ticker_id", "as_of_date", name="uq_oa_ticker_date"),)


class SqueezeScore(Base):
    __tablename__ = "squeeze_scores"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    score_date = Column(Date, nullable=False)
    score = Column(Float)  # 0-100
    rule_score = Column(Float)  # rule-based component
    ml_score = Column(Float)  # ML model component
    signal_breakdown = Column(JSON)  # {component: contribution}
    is_high_conviction = Column(Boolean, default=False)
    model_version = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="squeeze_scores")
    __table_args__ = (UniqueConstraint("ticker_id", "score_date", name="uq_ss_ticker_date"),)


class MLFeature(Base):
    __tablename__ = "ml_features"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    feature_date = Column(Date, nullable=False)
    features = Column(JSON)
    label = Column(Integer)  # 1 = squeeze within 30 days, 0 = no squeeze
    created_at = Column(DateTime, server_default=func.now())
    ticker = relationship("Ticker", back_populates="ml_features")
    __table_args__ = (UniqueConstraint("ticker_id", "feature_date", name="uq_mlf_ticker_date"),)


class SqueezeEpisode(Base):
    __tablename__ = "squeeze_episodes"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    start_date = Column(Date)
    peak_date = Column(Date)
    end_date = Column(Date)
    peak_return_pct = Column(Float)
    trigger = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    watchlist = relationship("Watchlist", back_populates="items")
    ticker = relationship("Ticker")


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    alert_type = Column(Enum(AlertType))
    threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="alerts")
    ticker = relationship("Ticker")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    strategy = Column(String(50))  # rules | ml | both
    start_date = Column(Date)
    end_date = Column(Date)
    universe = Column(JSON)  # list of symbols
    results = Column(JSON)  # metrics dict
    created_at = Column(DateTime, server_default=func.now())


class DataFreshness(Base):
    __tablename__ = "data_freshness"
    id = Column(Integer, primary_key=True)
    data_type = Column(String(100), unique=True)
    last_updated = Column(DateTime)
    record_count = Column(Integer)
    status = Column(String(50))  # ok | stale | error
    details = Column(JSON)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
