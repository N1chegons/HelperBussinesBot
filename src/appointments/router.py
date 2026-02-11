from fastapi import APIRouter, HTTPException, Query

from src.appointments.repository import AppointmentsRepository
from src.appointments.schemas import CreateAppointments

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.get("/get_my_appointments")
async def get_appointments(telegram_id: int):
    appointments_list = await AppointmentsRepository.get_user_appointments_all_repository(telegram_id)
    if not appointments_list:
        raise HTTPException(status_code=404, detail="You don't have any appointment")
    return appointments_list

@router.get("/get_my_appointments_by_date")
async def get_appointments_by_date(telegram_id: int, user_timezone: str,  date_apps: str = Query(min_length=10, max_length=10,  description="Date in format YYYY-MM-DD")):
    appointments_sort_date_list = await AppointmentsRepository.get_user_appointments_by_datetime_repository(telegram_id, date_apps, user_timezone)
    if not appointments_sort_date_list:
        raise HTTPException(status_code=404, detail=f"You don't have any appointment with time: {date_apps}")
    return appointments_sort_date_list

@router.post("/create_appointment")
async def create_appointment(appointment_data: CreateAppointments):
    new_appointments = await AppointmentsRepository.create_user_appointment_repository(appointment_data)
    return new_appointments

@router.delete("/delete_appointment")
async def delete_appointment(telegram_id: int, appointment_id: int):
    deleted_appointment = await AppointmentsRepository.delete_user_appointment_repository(telegram_id, appointment_id)
    return deleted_appointment