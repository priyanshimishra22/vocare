from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from sqlalchemy.orm import Session
from .database import engine,Base, SessionLocal
from .models import Appointment

app = FastAPI(title="VocaCare API")
Base.metadata.create_all(bind=engine)

# -------------------------
# Request models
# -------------------------

class AvailabilityRequest(BaseModel):
    doctor: str
    appointment_date: date
    preferred_time: str


# -------------------------
# Mock appointment data
# -------------------------

AVAILABLE_SLOTS = {
    "Dr. Sharma": {
        "2026-09-27": ["10:00 AM", "11:30 AM", "3:30 PM", "5:00 PM"],
        "2026-09-28": ["9:30 AM", "12:00 PM", "3:30 PM", "4:30 PM"],
    },
    "Dr. Mehta": {
        "2026-09-27": ["9:00 AM", "1:00 PM", "4:00 PM"],
        "2026-09-28": ["10:30 AM", "2:00 PM", "5:30 PM"],
    },
}


# -------------------------
# Health check
# -------------------------

@app.get("/")
async def root():
    return {
        "message": "VocaCare API is running"
    }


# -------------------------
# Check appointment availability
# -------------------------

@app.post("/availability")
async def check_availability(request: AvailabilityRequest):

    db = SessionLocal()

    try:
        booked_slots = db.query(Appointment).filter(
            Appointment.doctor == request.doctor,
            Appointment.appointment_date == request.appointment_date
        ).all()

        booked_times = {
            appointment.appointment_time
            for appointment in booked_slots
        }

        # Temporary clinic schedule
        clinic_slots = [
            "9:00 AM",
            "10:00 AM",
            "11:30 AM",
            "12:00 PM",
            "1:00 PM",
            "2:00 PM",
            "3:00 PM",
            "3:30 PM",
            "4:00 PM",
            "5:00 PM"
        ]

        available_slots = [
            slot for slot in clinic_slots
            if slot not in booked_times
        ]

        if request.preferred_time in available_slots:
            return {
                "available": True,
                "doctor": request.doctor,
                "date": str(request.appointment_date),
                "time": request.preferred_time,
                "message": "The requested appointment slot is available."
            }

        return {
            "available": False,
            "doctor": request.doctor,
            "date": str(request.appointment_date),
            "requested_time": request.preferred_time,
            "available_slots": available_slots,
            "message": "The requested slot is not available."
        }

    finally:
        db.close()

from uuid import uuid4


class BookingRequest(BaseModel):
    patient_name: str
    doctor: str
    appointment_date: date
    appointment_time: str


@app.post("/book")
async def book_appointment(request: BookingRequest):

    db = SessionLocal()

    try:
        # Check whether this exact slot is already booked
        existing_booking = db.query(Appointment).filter(
            Appointment.doctor == request.doctor,
            Appointment.appointment_date == request.appointment_date,
            Appointment.appointment_time == request.appointment_time
        ).first()

        if existing_booking:
            return {
                "success": False,
                "message": "This appointment slot has already been booked."
            }

        # Check whether the doctor exists in our clinic
        if request.doctor not in ["Dr. Sharma", "Dr. Mehta"]:
            return {
                "success": False,
                "message": f"{request.doctor} is not available at VocaCare."
            }

        # Generate booking ID
        booking_id = f"VC-{uuid4().hex[:6].upper()}"

        # Create appointment
        appointment = Appointment(
            booking_id=booking_id,
            patient_name=request.patient_name,
            doctor=request.doctor,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return {
            "success": True,
            "booking_id": appointment.booking_id,
            "patient_name": appointment.patient_name,
            "doctor": appointment.doctor,
            "date": str(appointment.appointment_date),
            "time": appointment.appointment_time,
            "message": "Appointment booked successfully."
        }

    finally:
        db.close()