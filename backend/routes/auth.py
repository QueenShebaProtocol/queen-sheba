import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from backend.services.auth import (
    register_user,
    authenticate_user,
    create_session,
    delete_session,
    get_current_user,
    security_bearer
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Full Name is required.")
        return v.strip()

    @field_validator("email")
    def valid_email(cls, v):
        pattern = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(pattern, v.strip()):
            raise ValueError("Please provide a valid email address.")
        return v.strip().lower()

    @field_validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values.data and v != values.data["password"]:
            raise ValueError("Passwords do not match.")
        return v


class SignInRequest(BaseModel):
    email: str
    password: str


@router.post("/signup", summary="User Registration")
def signup(payload: SignUpRequest):
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    user = register_user(
        name=payload.name,
        email=payload.email,
        password=payload.password
    )

    return {
        "success": True,
        "message": "Account created successfully. Please sign in.",
        "user": user
    }


@router.post("/signin", summary="User Sign In / Login")
def signin(payload: SignInRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password. Please try again."
        )

    token = create_session(user["id"])
    return {
        "token": token,
        "user": user,
        "message": f"Welcome back, {user['name']}!"
    }


@router.get("/me", summary="Get Current Authenticated User")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "user": current_user
    }


@router.post("/logout", summary="User Logout")
def logout(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)):
    if credentials and credentials.credentials:
        delete_session(credentials.credentials)
    return {"success": True, "message": "Signed out successfully."}
