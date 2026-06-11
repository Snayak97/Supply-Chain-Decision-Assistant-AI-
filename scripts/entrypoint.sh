# # #!/bin/bash
# # set -e

# # echo "Initializing database..."
# # PYTHONPATH=/app python scripts/init_db.py

# # echo "Generating mock data..."
# # PYTHONPATH=/app python scripts/generate_mock_data.py

# # echo "Starting API server..."
# # exec uvicorn run:app --host 0.0.0.0 --port 8000



# #!/bin/bash
# set -e

# echo "Initializing database..."
# PYTHONPATH=/app python scripts/init_db.py

# echo "Checking if mock data needed..."
# COUNT=$(PYTHONPATH=/app python -c "
# from core.database.session import SessionLocal
# from core.database.models import SKUMaster
# db = SessionLocal()
# print(db.query(SKUMaster).count())
# db.close()
# ")

# if [ "$COUNT" -eq "0" ]; then
#     echo "No data found. Generating mock data..."
#     PYTHONPATH=/app python scripts/generate_mock_data.py
#     echo "Mock data generated successfully!"
# else
#     echo "Data already exists ($COUNT SKUs). Skipping..."
# fi

# echo "Starting API server..."
# exec uvicorn run:app --host 0.0.0.0 --port 8000