# Troubleshooting Guide

This guide provides detailed solutions to common issues you may encounter while setting up and running the SC AI Assistant MVP.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Ollama Issues](#ollama-issues)
4. [API Server Issues](#api-server-issues)
5. [Performance Issues](#performance-issues)
6. [Data Issues](#data-issues)
7. [Logging & Debugging](#logging--debugging)
8. [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Issue: uv command not found

**Symptoms:**
```
'uv' is not recognized as an internal or external command
```

**Cause:** uv package manager is not installed or not in PATH.

**Solutions:**

**Option 1: Install uv**
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Option 2: Use pip instead**
```bash
pip install -r requirements.txt
```

**Option 3: Add uv to PATH (Windows)**
1. Open System Properties → Advanced → Environment Variables
2. Add `%USERPROFILE%\.local\bin` to PATH
3. Restart terminal

---

### Issue: Python version incompatible

**Symptoms:**
```
ERROR: Python 3.13+ required, but you have Python 3.11
```

**Cause:** Python version is too old.

**Solutions:**

**Option 1: Use uv to install Python**
```bash
uv python install 3.13
uv python pin 3.13
```

**Option 2: Install Python 3.13 manually**
1. Download from https://www.python.org/downloads/
2. Install Python 3.13
3. Update PATH to point to new Python installation

**Option 3: Use pyenv (Linux/Mac)**
```bash
pyenv install 3.13
pyenv global 3.13
```

---

### Issue: Dependency conflicts

**Symptoms:**
```
ERROR: Could not resolve dependencies
```

**Cause:** Conflicting package versions.

**Solutions:**

**Option 1: Clean install**
```bash
# Remove virtual environment
rm -rf .venv

# Re-run setup
uv sync
```

**Option 2: Force reinstall**
```bash
uv sync --reinstall
```

**Option 3: Check pyproject.toml**
- Verify all dependencies are compatible
- Check for version conflicts

---

## Database Issues

### Issue: Database locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Another process is accessing the database.

**Solutions:**

**Option 1: Close other processes**
- Close any database viewers (DB Browser for SQLite)
- Stop any other Python processes using the database

**Option 2: Delete and recreate**
```bash
# Delete database file
rm sc_ai.db

# Reinitialize
python scripts/init_db.py
```

**Option 3: Use WAL mode (advanced)**
```python
# In core/database/session.py, add:
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

---

### Issue: Table not found

**Symptoms:**
```
sqlite3.OperationalError: no such table: sku_master
```

**Cause:** Database tables were not created.

**Solutions:**

**Option 1: Run initialization script**
```bash
python scripts/init_db.py
```

**Option 2: Check database file exists**
```bash
ls -la sc_ai.db
```

**Option 3: Verify models are imported**
- Ensure all models in `core/database/models.py` are imported
- Check that `Base.metadata.create_all()` is called

---

### Issue: Foreign key constraint failed

**Symptoms:**
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Cause:** Referenced record doesn't exist.

**Solutions:**

**Option 1: Regenerate data in correct order**
```bash
# The generate_mock_data.py script handles this automatically
python scripts/generate_mock_data.py
```

**Option 2: Check data integrity**
```bash
# Open database in DB Browser for SQLite
# Check that referenced records exist
```

**Option 3: Disable foreign keys (for testing only)**
```python
# In core/database/session.py:
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "foreign_keys": False})
```

---

## Ollama Issues

### Issue: Ollama not found

**Symptoms:**
```
Connection refused to Ollama at http://localhost:11434
```

**Cause:** Ollama is not installed or not running.

**Solutions:**

**Option 1: Install Ollama**
1. Download from https://ollama.com
2. Install for your OS
3. Start Ollama: `ollama serve`

**Option 2: Verify Ollama is running**
```bash
# Check if Ollama is running
curl http://localhost:11434

# Should return: "Ollama is running"
```

**Option 3: Start Ollama as service**
```bash
# Linux/Mac
ollama serve &

# Windows
# Ollama should start automatically on install
```

---

### Issue: Model not found

**Symptoms:**
```
Error: model 'llama3' not found
```

**Cause:** Llama3 model is not downloaded.

**Solutions:**

**Option 1: Pull the model**
```bash
ollama pull llama3
```

**Option 2: List available models**
```bash
ollama list
```

**Option 3: Use a different model**
```bash
# In .env file, change:
OLLAMA_MODEL=llama2
# Then pull it:
ollama pull llama2
```

---

### Issue: Ollama slow response

**Symptoms:**
```
Ollama takes > 30 seconds to respond
```

**Cause:** Insufficient hardware resources.

**Solutions:**

**Option 1: Use smaller model**
```bash
ollama pull llama3:8b  # Smaller than default
# Update .env: OLLAMA_MODEL=llama3:8b
```

**Option 2: Increase Ollama memory**
```bash
# Set environment variable (Linux/Mac)
export OLLAMA_NUM_THREAD=8

# Windows (PowerShell)
$env:OLLAMA_NUM_THREAD=8
```

**Option 3: Check system resources**
- Ensure at least 8GB RAM available
- Close other applications
- Check CPU usage

---

## API Server Issues

### Issue: Port already in use

**Symptoms:**
```
ERROR: [Errno 48] Address already in use: port 8000
```

**Cause:** Another process is using port 8000.

**Solutions:**

**Option 1: Use different port**
```bash
uvicorn apps.api.main:app --reload --port 8001
```

**Option 2: Kill process on port 8000**
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Option 3: Find and kill process**
```bash
# Linux/Mac
ps aux | grep uvicorn

# Windows
tasklist | findstr python
```

---

### Issue: Module not found

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed.

**Solutions:**

**Option 1: Install dependencies**
```bash
uv sync
```

**Option 2: Activate virtual environment**
```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**Option 3: Check PYTHONPATH**
```bash
# Ensure project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### Issue: CORS errors

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Cause:** API doesn't allow cross-origin requests.

**Solutions:**

**Option 1: Add CORS middleware**
```python
# In apps/api/main.py:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Option 2: Use same origin**
- Serve frontend from same domain as API
- Or use reverse proxy

---

## Performance Issues

### Issue: Slow API responses

**Symptoms:**
```
API responses take > 10 seconds
```

**Cause:** Large data volume or inefficient queries.

**Solutions:**

**Option 1: Use filters**
```bash
# Filter by category to reduce data volume
curl -X POST "http://localhost:8000/scenario/simulate" \
  -d '{"query": "...", "scope": {"category": "Apparel"}}'
```

**Option 2: Enable caching**
```python
# Cache is enabled by default
# Check cache_manager.py for TTL settings
```

**Option 3: Optimize database queries**
```python
# Add indexes to frequently queried columns
# In core/database/models.py:
class Forecast(Base):
    __tablename__ = "forecast"
    sku_id = Column(String, index=True)  # Add index
    category = Column(String, index=True)  # Add index
```

---

### Issue: Memory usage high

**Symptoms:**
```
Python process using > 2GB RAM
```

**Cause:** Loading too much data into memory.

**Solutions:**

**Option 1: Use pagination**
```python
# In tools, limit query results:
query = query.limit(100)
```

**Option 2: Process in batches**
```python
# Process data in chunks instead of all at once
for batch in get_data_in_batches(batch_size=100):
    process_batch(batch)
```

**Option 3: Clear cache periodically**
```python
from core.cache.cache_manager import CacheManager
CacheManager.cleanup_expired_cache()
```

---

## Data Issues

### Issue: No data returned

**Symptoms:**
```
API returns empty results
```

**Cause:** Sample data not generated or filters too restrictive.

**Solutions:**

**Option 1: Regenerate data**
```bash
python scripts/generate_mock_data.py
```

**Option 2: Check database**
```bash
# Open sc_ai.db in DB Browser for SQLite
# Verify tables have data
```

**Option 3: Relax filters**
```bash
# Remove scope filters
curl -X POST "http://localhost:8000/scenario/simulate" \
  -d '{"query": "...", "scope": {}}'
```

---

### Issue: Incorrect calculations

**Symptoms:**
```
Forecast values don't match expectations
```

**Cause:** Data generation or calculation logic issues.

**Solutions:**

**Option 1: Verify data generation**
```bash
# Check generate_mock_data.py logic
# Ensure realistic parameters
```

**Option 2: Check tool logic**
```python
# Add debug logging in tools
# Verify calculations are correct
```

**Option 3: Validate with known values**
```bash
# Test with simple scenario
# Verify 25% increase = 1.25x multiplier
```

---

## Logging & Debugging

### Enable Debug Logging

**Option 1: Change log level**
```python
# In core/logging/logger.py:
logger.add(
    sys.stdout,
    level="DEBUG"  # Change from INFO to DEBUG
)
```

**Option 2: Set environment variable**
```bash
export LOG_LEVEL=DEBUG
```

**Option 3: Use verbose mode**
```bash
uvicorn apps.api.main:app --reload --log-level debug
```

---

### View Logs

**Option 1: Console output**
```bash
# Logs appear in terminal when running uvicorn
```

**Option 2: Log files**
```bash
# View application log
tail -f logs/app.log

# View error log
tail -f logs/error.log
```

**Option 3: JSON logs**
```python
# Logs are in JSON format for parsing
# Use jq to filter:
cat logs/app.log | jq '.event_type == "tool_call"'
```

---

### Debug Tool Calls

**Option 1: Check tool_calls in response**
```bash
# API response includes tool_calls array
# Shows all tools called with arguments and results
```

**Option 2: Add print statements**
```python
# In tool functions:
print(f"DEBUG: Called with args: {kwargs}")
print(f"DEBUG: Result: {result}")
```

**Option 3: Use Python debugger**
```python
import pdb; pdb.set_trace()
# Or use breakpoint()
```

---

## Common Error Messages

### `AttributeError: 'NoneType' object has no attribute 'xxx'`

**Cause:** Expected value is None.

**Solutions:**
- Add null checks: `if value is not None:`
- Provide default values: `value = data.get('key', default)`
- Validate input before use

---

### `KeyError: 'xxx'`

**Cause:** Dictionary key doesn't exist.

**Solutions:**
- Use `.get()` method: `data.get('key', default)`
- Check if key exists: `if 'key' in data:`
- Validate schema with Pydantic

---

### `ValueError: invalid literal for int()`

**Cause:** String cannot be converted to int.

**Solutions:**
- Validate input type: `int(value) if value.isdigit() else default`
- Use try/except: `try: int(value) except ValueError:`
- Use Pydantic models for validation

---

### `TypeError: 'xxx' object is not callable`

**Cause:** Trying to call a non-callable object.

**Solutions:**
- Check variable names don't shadow functions
- Verify function is defined before use
- Import functions correctly

---

## Getting Help

If you're still stuck after trying these solutions:

1. **Check the logs:** Look at `logs/app.log` and `logs/error.log`
2. **Verify setup:** Run the setup script again
3. **Check dependencies:** Run `uv sync`
4. **Restart services:** Stop and restart API server and Ollama
5. **Search online:** Search error messages on Stack Overflow or GitHub issues

---

## Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **LangGraph Documentation:** https://langchain-ai.github.io/langgraph
- **Ollama Documentation:** https://ollama.com/docs
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org
- **Pydantic Documentation:** https://docs.pydantic.dev

---

**Last Updated:** June 2026
