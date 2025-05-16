from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import uvicorn
import logging
import os
import asyncio
from dotenv import load_dotenv

from rabbitMQ.attendance_consumer import attendance_consume  # import your consumer
from rabbitMQ.realtime_consumer import consume_realtime


from routes.attendance_routes import router as attendance_router
#from routes.students_routes import router as student_router
from routes.realtime import router as realtime_router

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Attendance System API",
    description="API for facial recognition and attendance tracking",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "detail": str(exc)},
    )

# Include routers
app.include_router(attendance_router)
#app.include_router(student_router)
app.include_router(realtime_router)

# @app.get("/")
# async def health_check():
#     return {"status": "ok", "message": "Smart Attendance System API is running"}

# Mount static files directory
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to the face recognition UI"""
    # return RedirectResponse(url="/static/index.html")
    pass

# @app.on_event("startup")
# async def start_consumer():
#     loop = asyncio.get_event_loop()
#     loop.create_task(consume())  # Run the consumer in background

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(attendance_consume())
    asyncio.create_task(consume_realtime())


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 4000))
    reload = os.getenv("RELOAD", "False").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload)

# http://localhost:8000/
# uvicorn main:app --reload
# http://localhost:5173/
