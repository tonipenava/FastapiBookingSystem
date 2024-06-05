from fastapi import Depends
import app.auth as auth

def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    return auth.get_current_user(token)
