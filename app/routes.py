from fastapi import APIRouter, Header, HTTPException

router = APIRouter()


# ==========================
# Public Route
# ==========================

@router.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# ==========================
# Protected Route
# ==========================

@router.get("/protected/profile")
def protected_profile(authorization: str = Header(None)):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    token = authorization.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    return {
        "message": "Bearer token received.",
        "token": token
    }