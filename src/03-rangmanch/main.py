from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_tables
from routes.reviews import router as reviews_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    print("Starting up the Rangmanch API...")
    create_tables()  # Create database tables on startup
    yield
    # Perform any shutdown tasks here
    print("Shutting down the Rangmanch API...")


app = FastAPI(
    title="Rangmanch API",
    description="Rangmanch is a platform for managing and organizing events, performances, and cultural activities. This API allows you to interact with the Rangmanch platform programmatically.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include the reviews router
app.include_router(reviews_router)

  

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
    