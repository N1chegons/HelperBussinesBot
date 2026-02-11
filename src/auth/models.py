import datetime
from typing import List

from sqlalchemy import text, BigInteger
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from src.appointments.models import Appointment
from src.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    timezone: Mapped[str] = mapped_column(default=None, nullable=True)
    registered_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="user"
    )
