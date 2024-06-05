from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    username: str
    password: str

class Apartment(BaseModel):
    name: str
    description: str

class Booking(BaseModel):
    apartment_id: str
    start_date: datetime
    end_date: datetime
