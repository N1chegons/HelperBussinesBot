import datetime

from pydantic import BaseModel, field_validator, ConfigDict, Field


class UserView(BaseModel):
    id: int
    telegram_id: int
    nickname: str
    phone: str
    registered_at: datetime.datetime

    @field_validator('registered_at')
    def custom(cls, v):
        return datetime.datetime.strftime(v, "%m.%d.%Y")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    telegram_id: int
    nickname: str