from fastapi import FastAPI
from .database import Base, engine
from .auth import router as auth_router
from .routes import router as routes_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include authentication and main routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(routes_router, prefix="/api", tags=["Routes"])

@app.get("/")
def root():
    return {"message": "FastAPI Metadata Scraper is running!"}
