from fastapi import FastAPI
import asyncio

# Import your routers
from routers.exam_routes import router as exam_router
from routers.assignment_routes import router as assignment_router
from rabbitMQ.schedule_consumer import schedule_consume

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(schedule_consume())

# Include routers
app.include_router(exam_router, prefix="/api")
app.include_router(assignment_router, prefix="/api")