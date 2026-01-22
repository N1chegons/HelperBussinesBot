import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from src.appointments.models import Status

class ViewAppointments(BaseModel):
    id: int
    phone: str
    status: Status
    appointment_datetime: datetime.datetime
    created_at: datetime.datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator('created_at')
    def custom(cls, v):
        return datetime.datetime.strftime(v, "%m.%d.%Y")


class CreateAppointments(BaseModel):
    phone: str
    title: str
    appointment_date: datetime.date
    appointment_time: str