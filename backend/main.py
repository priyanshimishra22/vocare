from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

app = FastAPI(title="VocaCare API")


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

    doctor_slots = AVAILABLE_SLOTS.get(request.doctor)

    if not doctor_slots:
        return {
            "available": False,
            "message": f"{request.doctor} is not available at VocaCare."
        }

    date_slots = doctor_slots.get(str(request.appointment_date), [])

    if request.preferred_time in date_slots:
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
        "available_slots": date_slots,
        "message": "The requested slot is not available."
    }

from uuid import uuid4


class BookingRequest(BaseModel):
    patient_name: str
    doctor: str
    appointment_date: date
    appointment_time: str


@app.post("/book")
async def book_appointment(request: BookingRequest):

    doctor_slots = AVAILABLE_SLOTS.get(request.doctor)

    if not doctor_slots:
        return {
            "success": False,
            "message": f"{request.doctor} is not available at VocaCare."
        }

    date_slots = doctor_slots.get(str(request.appointment_date), [])

    if request.appointment_time not in date_slots:
        return {
            "success": False,
            "message": "The requested appointment slot is not available.",
            "available_slots": date_slots
        }

    booking_id = f"VC-{uuid4().hex[:6].upper()}"

    return {
        "success": True,
        "booking_id": booking_id,
        "patient_name": request.patient_name,
        "doctor": request.doctor,
        "date": str(request.appointment_date),
        "time": request.appointment_time,
        "message": "Appointment booked successfully."
    }