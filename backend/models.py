from sqlalchemy import Column, Integer, String, Date, UniqueConstraint

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, unique=True, index=True, nullable=False)

    patient_name = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "doctor",
            "appointment_date",
            "appointment_time",
            name="unique_doctor_slot"
        ),
    )