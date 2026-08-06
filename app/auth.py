from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import traceback
from app.supabase_client import supabase

router = APIRouter()


# ==========================
# Pydantic Models
# ==========================

class SignUpRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ==========================
# Signup
# ==========================

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: SignUpRequest):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required."
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
            }
        )

        return {
            "message": "User created successfully.",
            "user": response.user
        }

    except Exception as e:
        traceback.print_exc()

    print(type(e))
    print(repr(e))

    raise HTTPException(
        status_code=400,
        detail=repr(e)
    )


# ==========================
# Login
# ==========================

@router.post("/login")
def login(user: LoginRequest):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required."
        )

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password,
            }
        )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "Bearer"
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials."
        )