"""
Database initialization script.
Creates all tables from the defined models.
"""
from core.database.session import engine
from core.database.models import Base

print("Creating database tables...")
print("This will create the following tables:")
print("  - sku_master")
print("  - forecast")
print("  - inventory")
print("  - sales_actual")
print("  - purchase_order")
print("  - lead_time")
print("  - otb_plan")
print("  - scenario_session")
print("  - tool_result_cache")
print("")

Base.metadata.create_all(bind=engine)

print("Database created successfully.")
print("Database file: sc_ai.db (SQLite)")