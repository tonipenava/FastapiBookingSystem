import uuid

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from typing import List
import app.schemas as schemas
import app.crud as crud
import app.auth as auth
from app.dependencies import get_current_user
import json

app = FastAPI()


@app.post("/register")
def register(user: schemas.User):
    if crud.get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    crud.create_user(user.username, user.password)
    return {"msg": "User registered successfully"}


@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not auth.authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = crud.create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


@app.post("/apartments")
def create_apartment(apartment: schemas.Apartment, current_user: str = Depends(get_current_user)):
    apartment_id = crud.create_apartment(apartment.name, apartment.description, current_user)
    return {"apartment_id": apartment_id, "msg": "Apartment created successfully"}


@app.post("/book")
def book_apartment(booking: schemas.Booking, current_user: str = Depends(get_current_user)):
    try:
        apartment_data = crud.get_apartment(booking.apartment_id)
        if not apartment_data:
            raise HTTPException(status_code=404, detail="Apartment not found")

        existing_bookings = crud.get_bookings(booking.apartment_id)
        for booking_entry in existing_bookings:
            b = json.loads(booking_entry)
            if (booking.start_date <= datetime.fromisoformat(b["end_date"]) and
                    booking.end_date >= datetime.fromisoformat(b["start_date"])):
                raise HTTPException(status_code=400, detail="Apartment is already booked for the selected dates")

        booking_id = str(uuid.uuid4())
        crud.create_booking(booking.apartment_id, current_user, booking.start_date, booking.end_date)
        return {"msg": "Booking successful", "booking_id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking apartment: {e}")


@app.put("/bookings/{booking_id}")
def update_booking(booking_id: str, booking: schemas.UpdateBooking, current_user: str = Depends(get_current_user)):
    try:
        existing_booking, apartment_id = crud.get_booking_by_id(booking_id)
        if not existing_booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        crud.update_booking(apartment_id, booking_id, current_user, booking.start_date, booking.end_date)
        return {"msg": "Booking updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating booking: {e}")

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: str, apartment_id: str, current_user: str = Depends(get_current_user)):
    try:
        crud.delete_booking(apartment_id, booking_id)
        return {"msg": "Booking deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting booking: {e}")
