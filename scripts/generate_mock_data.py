

"""
Enhanced sample data generation script with realistic business data.
Generates mock data for all database models to support scenario simulation.
"""
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session

from core.database.session import SessionLocal
from core.database.models import (
    SKUMaster,
    Forecast,
    Inventory,
    SalesActual,
    PurchaseOrder,
    LeadTime,
    OTBPlan
)

fake = Faker()

db: Session = SessionLocal()

# =========================
# MASTER DATA CONFIGURATION
# =========================

categories = ["Apparel", "Shoes", "Accessories"]
channels = ["DTC", "Wholesale"]
warehouses = ["MUM_WH1", "DEL_WH1", "BLR_WH1"]
suppliers = ["Supplier_A", "Supplier_B", "Supplier_C", "Supplier_D"]

SKU_COUNT = 100
FORECAST_HORIZON_DAYS = 90
BASE_DATE = datetime(2026, 6, 1)

# =========================
# SKU MASTER
# =========================

print("Generating SKU master data...")

for i in range(SKU_COUNT):
    # ✅ Skip if already exists
    if db.query(SKUMaster).filter_by(sku_id=f"SKU{i:03}").first():
        continue

    category = random.choice(categories)
    channel = random.choice(channels)
    is_core = random.random() < 0.3

    if is_core:
        gross_margin = random.uniform(45, 65)
        moq = random.randint(50, 200)
        unit_cost = random.uniform(30, 80)
    else:
        gross_margin = random.uniform(20, 45)
        moq = random.randint(100, 500)
        unit_cost = random.uniform(15, 60)

    sku = SKUMaster(
        sku_id=f"SKU{i:03}",
        category=category,
        channel=channel,
        supplier=random.choice(suppliers),
        is_core=is_core,
        gross_margin_pct=gross_margin,
        moq=moq,
        unit_cost=unit_cost
    )
    db.add(sku)

db.commit()
print("SKU master data done.")

# =========================
# FORECAST WITH CI
# =========================

print("Generating forecast data with confidence intervals...")

for i in range(SKU_COUNT):
    sku_id = f"SKU{i:03}"
    category = random.choice(categories)
    channel = random.choice(channels)

    for day_offset in range(FORECAST_HORIZON_DAYS):
        forecast_date = (BASE_DATE + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        # ✅ Skip if already exists
        if db.query(Forecast).filter_by(sku_id=sku_id, date=forecast_date, channel=channel).first():
            continue

        base_qty = random.randint(50, 300)
        if day_offset < 30:
            base_qty = int(base_qty * 1.2)

        campaign_multiplier = random.uniform(1.0, 1.3)
        adjusted_qty = int(base_qty * campaign_multiplier)

        ci_width = random.uniform(0.2, 0.4)
        lower_80 = int(adjusted_qty * (1 - ci_width))
        upper_80 = int(adjusted_qty * (1 + ci_width))
        lower_95 = int(adjusted_qty * (1 - ci_width * 1.5))
        upper_95 = int(adjusted_qty * (1 + ci_width * 1.5))

        forecast = Forecast(
            sku_id=sku_id,
            category=category,
            channel=channel,
            date=forecast_date,
            base_forecast_qty=base_qty,
            adjusted_forecast_qty=adjusted_qty,
            lower_ci_80=lower_80,
            upper_ci_80=upper_80,
            lower_ci_95=lower_95,
            upper_ci_95=upper_95,
            ci_width_80=ci_width
        )
        db.add(forecast)

db.commit()
print("Forecast data done.")

# =========================
# INVENTORY POSITION
# =========================

print("Generating inventory position data...")

for i in range(SKU_COUNT):
    sku_id = f"SKU{i:03}"

    for warehouse in warehouses:
        for channel in channels:
            # ✅ Skip if already exists
            if db.query(Inventory).filter_by(sku_id=sku_id, warehouse=warehouse, channel=channel).first():
                continue

            on_hand = random.randint(100, 800)
            in_transit = random.randint(0, 200)
            reserved = random.randint(10, 100)
            net_available = on_hand + in_transit - reserved

            inventory = Inventory(
                sku_id=sku_id,
                warehouse=warehouse,
                channel=channel,
                on_hand_qty=on_hand,
                in_transit_qty=in_transit,
                reserved_qty=reserved,
                net_available_qty=net_available
            )
            db.add(inventory)

db.commit()
print("Inventory data done.")

# =========================
# SALES ACTUALS
# =========================

print("Generating historical sales actuals...")

for day_offset in range(30, 0, -1):
    sales_date = (BASE_DATE - timedelta(days=day_offset)).strftime("%Y-%m-%d")

    for i in range(SKU_COUNT):
        sku_id = f"SKU{i:03}"
        category = random.choice(categories)
        channel = random.choice(channels)

        # ✅ Skip if already exists
        if db.query(SalesActual).filter_by(sku_id=sku_id, date=sales_date, channel=channel).first():
            continue

        actual_qty = random.randint(40, 350)
        revenue = actual_qty * random.uniform(40, 100)

        sales = SalesActual(
            sku_id=sku_id,
            category=category,
            channel=channel,
            date=sales_date,
            actual_sales_qty=actual_qty,
            revenue=revenue
        )
        db.add(sales)

db.commit()
print("Sales actuals done.")

# =========================
# PURCHASE ORDERS
# =========================

print("Generating open purchase orders...")

PO_COUNT = 50

for i in range(PO_COUNT):
    po_number = f"PO{i:04}"

    # ✅ Skip if already exists
    if db.query(PurchaseOrder).filter_by(po_number=po_number).first():
        continue

    sku_id = f"SKU{random.randint(0, SKU_COUNT-1):03}"
    category = random.choice(categories)
    supplier = random.choice(suppliers)

    ordered_qty = random.randint(100, 1000)
    unit_cost = random.uniform(30, 80)
    total_value = ordered_qty * unit_cost

    delivery_days = random.randint(14, 56)
    expected_delivery = (BASE_DATE + timedelta(days=delivery_days)).strftime("%Y-%m-%d")

    is_cancelable = delivery_days > 14
    cancelable_until = (BASE_DATE + timedelta(days=14)).strftime("%Y-%m-%d") if is_cancelable else None

    status = random.choice(["OPEN", "IN_TRANSIT"])
    if delivery_days < 21:
        status = "IN_TRANSIT"

    po = PurchaseOrder(
        po_number=po_number,
        sku_id=sku_id,
        category=category,
        supplier=supplier,
        ordered_qty=ordered_qty,
        unit_cost=unit_cost,
        total_value=total_value,
        expected_delivery_date=expected_delivery,
        cancelable_until_date=cancelable_until,
        status=status,
        is_cancelable=is_cancelable,
        cancel_penalty_pct=random.uniform(5, 15),
        priority=random.choice(["HIGH", "MEDIUM", "LOW"])
    )
    db.add(po)

db.commit()
print("Purchase orders done.")

# =========================
# LEAD TIMES
# =========================

print("Generating lead time distributions...")

for supplier in suppliers:
    for category in categories:
        # ✅ Skip if already exists
        if db.query(LeadTime).filter_by(supplier=supplier, category=category).first():
            continue

        base_lead = random.randint(14, 35)
        std_dev = random.uniform(3, 7)

        lead = LeadTime(
            supplier=supplier,
            category=category,
            lead_time_days=base_lead,
            lead_time_std_dev=std_dev,
            min_lead_time=max(7, base_lead - int(std_dev * 2)),
            max_lead_time=base_lead + int(std_dev * 2)
        )
        db.add(lead)

db.commit()
print("Lead times done.")

# =========================
# OTB PLAN
# =========================

print("Generating OTB budget plans...")

periods = ["2026-Q2", "2026-Q3"]

for category in categories:
    for period in periods:
        # ✅ Skip if already exists
        if db.query(OTBPlan).filter_by(category=category, period=period).first():
            continue

        if category == "Apparel":
            budget = random.randint(400000, 600000)
        elif category == "Shoes":
            budget = random.randint(300000, 500000)
        else:
            budget = random.randint(200000, 400000)

        committed = int(budget * random.uniform(0.6, 0.9))
        available = budget - committed
        utilization = (committed / budget) * 100

        is_overcommitted = random.random() < 0.2
        if is_overcommitted:
            committed = int(budget * random.uniform(1.05, 1.2))
            available = budget - committed
            utilization = (committed / budget) * 100

        otb = OTBPlan(
            category=category,
            period=period,
            budget=budget,
            committed_spend=committed,
            available_otb=available,
            utilization_pct=utilization,
            is_overcommitted=is_overcommitted
        )
        db.add(otb)

db.commit()
print("OTB plans done.")

db.close()

print("\n" + "="*50)
print("Mock data generation complete!")
print("="*50)
print(f"  - {SKU_COUNT} SKUs across {len(categories)} categories")
print(f"  - {SKU_COUNT * FORECAST_HORIZON_DAYS} forecast records")
print(f"  - {SKU_COUNT * len(warehouses) * len(channels)} inventory records")
print(f"  - {PO_COUNT} purchase orders")
print(f"  - {len(suppliers) * len(categories)} lead time records")
print(f"  - {len(categories) * len(periods)} OTB plan records")
print("="*50)