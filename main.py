from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.main import router as main_router

app = FastAPI(
    title="Smart Campus Management API",
    description="Backend API for Smart Campus Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main router
app.include_router(main_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Campus Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)