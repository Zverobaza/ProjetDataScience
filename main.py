import uvicorn
from backend.routes import router
from fastapi import FastAPI

app = FastAPI()

# Ajouter les routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

