import os, sys, subprocess

env = {**os.environ, "PYTHONPATH": "/app"}

print("=== Init DB ===")
subprocess.run(["python", "scripts/init_db.py"], env=env, cwd="/app", check=True)

print("=== Check Data ===")
r = subprocess.run(["python", "-c",
    "import sys; sys.path.insert(0,'/app');"
    "from core.database.session import SessionLocal;"
    "from core.database.models import SKUMaster, OTBPlan;"
    "db=SessionLocal();"
    "sku=db.query(SKUMaster).count();"
    "otb=db.query(OTBPlan).count();"
    "print(sku, otb);"
    "db.close()"
], env=env, cwd="/app", capture_output=True, text=True)

output = r.stdout.strip().split()
sku_count = int(output[0] if len(output) > 0 else "0")
otb_count = int(output[1] if len(output) > 1 else "0")
print(f"Found {sku_count} SKUs, {otb_count} OTB records")

if sku_count == 0 or otb_count == 0:
    print("=== Generate Mock Data ===")
    subprocess.run(["python", "scripts/generate_mock_data.py"], env=env, cwd="/app", check=True)
else:
    print("=== Data exists. Skipping ===")

print("=== Starting Server ===")
os.chdir("/app")
os.execvpe("uvicorn", ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"], env)