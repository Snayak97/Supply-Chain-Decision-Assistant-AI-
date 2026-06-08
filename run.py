from apps.api.main import creat_app
import uvicorn

app = creat_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )   