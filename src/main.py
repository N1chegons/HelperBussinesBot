from fastapi import FastAPI

from src.auth.router import router as user_router
from src.appointments.router import router as appointments_router

app = FastAPI()

app.include_router(user_router)
app.include_router(appointments_router)