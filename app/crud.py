import redis
import hashlib
import uuid
from datetime import datetime
import json

r = redis.Redis(host='redis', port=6379, decode_responses=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str):
    hashed_password = hash_password(password)
    r.hset("users", username, hashed_password)

def get_user(username: str):
    return r.hget("users", username)

def create_token(username: str):
    token = str(uuid.uuid4())
    r.set(token, username)
    return token

def get_username_by_token(token: str):
    return r.get(token)

def create_apartment(name: str, description: str, owner: str):
    apartment_id = str(uuid.uuid4())
    r.hset(f"apartments:{apartment_id}", mapping={
        "name": name,
        "description": description,
        "owner": owner
    })
    return apartment_id

def get_apartment(apartment_id: str):
    return r.hgetall(f"apartments:{apartment_id}")

def create_booking(apartment_id: str, username: str, start_date: datetime, end_date: datetime):
    booking_id = str(uuid.uuid4())
    r.rpush(f"bookings:{apartment_id}", json.dumps({
        "id": booking_id,
        "user": username,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }))
    return booking_id
def get_bookings(apartment_id: str):
    return r.lrange(f"bookings:{apartment_id}", 0, -1)

def get_booking_by_id(booking_id: str):
    for key in r.scan_iter("bookings:*"):
        bookings = r.lrange(key, 0, -1)
        for booking_entry in bookings:
            b = json.loads(booking_entry)
            if b["id"] == booking_id:
                return b, key.split(":")[1]  # Return the booking and the apartment ID
    return None, None

def get_bookings_formatted(apartment_id: str):
    bookings = get_bookings(apartment_id)
    formatted_bookings = []
    for booking_entry in bookings:
        try:
            b = json.loads(booking_entry)
            formatted_bookings.append({
                "user": b["user"],
                "start_date": datetime.fromisoformat(b["start_date"]),
                "end_date": datetime.fromisoformat(b["end_date"])
            })
        except Exception as e:
            print(f"Error parsing booking entry: {e}")
            continue
    return formatted_bookings


def update_booking(apartment_id: str, booking_id: str, username: str, start_date: datetime, end_date: datetime):
    bookings = get_bookings(apartment_id)
    updated = False
    for i, booking_entry in enumerate(bookings):
        b = json.loads(booking_entry)
        if b["id"] == booking_id:
            bookings[i] = json.dumps({
                "id": booking_id,
                "user": username,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            })
            updated = True
            break

    if updated:
        r.delete(f"bookings:{apartment_id}")
        for booking_entry in bookings:
            r.rpush(f"bookings:{apartment_id}", booking_entry)
    else:
        raise ValueError("Booking not found")


def delete_booking(apartment_id: str, booking_id: str):
    bookings = get_bookings(apartment_id)
    bookings = [booking_entry for booking_entry in bookings if json.loads(booking_entry)["id"] != booking_id]
    r.delete(f"bookings:{apartment_id}")
    for booking_entry in bookings:
        r.rpush(f"bookings:{apartment_id}", booking_entry)