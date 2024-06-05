from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import app.crud as crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str):
    hashed_password = crud.get_user(username)
    if not hashed_password or hashed_password != crud.hash_password(password):
        return False
    return True

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = crud.get_username_by_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username
