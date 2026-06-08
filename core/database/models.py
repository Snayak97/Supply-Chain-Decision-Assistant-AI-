from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON
)
from datetime import datetime

from core.database.session import Base


# =========================
# SKU MASTER
# =========================

class SKUMaster(Base):
    """Master SKU catalog with attributes for scenario filtering and analysis."""
    __tablename__ = "sku_master"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False, index=True)
    supplier = Column(String, nullable=False, index=True)
    is_core = Column(Boolean, default=False, index=True)
    gross_margin_pct = Column(Float)
    moq = Column(Integer)  # Minimum Order Quantity
    unit_cost = Column(Float)  # Cost per unit for OTB calculations
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# FORECAST WITH CI
# =========================

class Forecast(Base):
    """Demand forecast with confidence intervals for scenario simulation."""
    __tablename__ = "forecast"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)
    
    # Base forecast before campaign adjustments
    base_forecast_qty = Column(Float, nullable=False)
    
    # Adjusted forecast after campaign uplift (used for scenario calculations)
    adjusted_forecast_qty = Column(Float, nullable=False)
    
    # Confidence intervals (80% and 95%)
    lower_ci_80 = Column(Float)
    upper_ci_80 = Column(Float)
    lower_ci_95 = Column(Float)
    upper_ci_95 = Column(Float)
    
    # Volatility proxy for risk assessment
    ci_width_80 = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# INVENTORY POSITION
# =========================

class Inventory(Base):
    """Current inventory position across warehouses and channels."""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String, nullable=False, index=True)
    warehouse = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False, index=True)
    
    on_hand_qty = Column(Float, nullable=False)
    in_transit_qty = Column(Float, default=0)
    reserved_qty = Column(Float, default=0)
    
    # Net available to sell
    net_available_qty = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# SALES ACTUALS
# =========================

class SalesActual(Base):
    """Historical sales data for forecast bias detection."""
    __tablename__ = "sales_actual"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)
    actual_sales_qty = Column(Float, nullable=False)
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# OPEN PURCHASE ORDERS
# =========================

class PurchaseOrder(Base):
    """Open POs with cancelability flags for OTB and recommendation logic."""
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, nullable=False, index=True)
    sku_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    supplier = Column(String, nullable=False, index=True)
    
    ordered_qty = Column(Float, nullable=False)
    unit_cost = Column(Float)
    total_value = Column(Float)
    
    expected_delivery_date = Column(String, nullable=False)
    cancelable_until_date = Column(String)
    
    status = Column(String, nullable=False)  # OPEN, IN_TRANSIT, DELIVERED, CANCELLED
    is_cancelable = Column(Boolean, default=False)
    cancel_penalty_pct = Column(Float, default=0)
    
    priority = Column(String, default="MEDIUM")  # HIGH, MEDIUM, LOW
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# LEAD TIMES
# =========================

class LeadTime(Base):
    """Supplier lead-time distributions for stockout risk calculation."""
    __tablename__ = "lead_time"

    id = Column(Integer, primary_key=True, index=True)
    supplier = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    
    lead_time_days = Column(Integer, nullable=False)
    lead_time_std_dev = Column(Float)  # For Monte Carlo simulation
    min_lead_time = Column(Integer)
    max_lead_time = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# OTB PLAN
# =========================

class OTBPlan(Base):
    """Open-to-Buy budget vs committed spend by category and period."""
    __tablename__ = "otb_plan"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    period = Column(String, nullable=False, index=True)  # e.g., "2026-Q2"
    
    budget = Column(Float, nullable=False)
    committed_spend = Column(Float, default=0)
    available_otb = Column(Float)
    
    utilization_pct = Column(Float)
    is_overcommitted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =========================
# SCENARIO SESSION STATE
# =========================

class ScenarioSession(Base):
    """Persisted scenario state for multi-turn conversations."""
    __tablename__ = "scenario_session"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    
    # Accumulated perturbations as JSON
    perturbations = Column(JSON, default=list)
    
    # Session metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


# =========================
# TOOL RESULT CACHE
# =========================

class ToolResultCache(Base):
    """Cache for tool results to avoid redundant computations."""
    __tablename__ = "tool_result_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, nullable=False, index=True)
    tool_name = Column(String, nullable=False, index=True)
    
    # Cached result as JSON
    result = Column(JSON, nullable=False)
    
    # Cache management
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)














# from sqlalchemy import Column, Integer, String, Float, Boolean

# from core.database.session import Base


# class SKUMaster(Base):
#     __tablename__ = "sku_master"

#     id = Column(Integer, primary_key=True, index=True)

#     sku_id = Column(String, unique=True)
#     category = Column(String)
#     channel = Column(String)

#     is_core = Column(Boolean)

#     gross_margin_pct = Column(Float)

#     moq = Column(Integer)


# class Forecast(Base):
#     __tablename__ = "forecast"

#     id = Column(Integer, primary_key=True, index=True)

#     sku_id = Column(String)

#     category = Column(String)

#     channel = Column(String)

#     date = Column(String)

#     forecast_qty = Column(Float)

#     lower_ci = Column(Float)

#     upper_ci = Column(Float)


# class Inventory(Base):
#     __tablename__ = "inventory"

#     id = Column(Integer, primary_key=True, index=True)

#     sku_id = Column(String)

#     warehouse = Column(String)

#     on_hand_qty = Column(Float)

#     reserved_qty = Column(Float)


# class OTBPlan(Base):
#     __tablename__ = "otb_plan"

#     id = Column(Integer, primary_key=True, index=True)

#     category = Column(String)

#     budget = Column(Float)

#     committed_spend = Column(Float)


# class SalesActual(Base):

#     __tablename__ = "sales_actual"

#     id = Column(Integer, primary_key=True, index=True)

#     sku_id = Column(String)

#     category = Column(String)

#     channel = Column(String)

#     date = Column(String)

#     actual_sales_qty = Column(Float)