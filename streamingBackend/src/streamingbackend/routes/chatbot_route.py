from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from streamingbackend.services.chatbot_service import chatbotService, getChatHistory
from streamingbackend.services.visitor_auth_service import (
    build_access_status,
    submit_lead,
    verify_otp,
)

chatbot_router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)


class LeadRequest(BaseModel):
    session_id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=160)
    company: str = Field(min_length=1, max_length=160)
    designation: str = Field(min_length=1, max_length=160)


class VerifyOtpRequest(BaseModel):
    session_id: str | None = None
    otp: str = Field(min_length=4, max_length=8)


@chatbot_router.get("/health")
async def health():
    return {"message": "Chatbot route is healthy"}


@chatbot_router.get("/access")
async def access(session_id: str | None = Query(default=None)):
    return {"access": build_access_status(session_id)}


@chatbot_router.get("/history")
async def history(session_id: str | None = Query(default=None)):
    return {
        "chat_history": getChatHistory(session_id),
        "access": build_access_status(session_id),
    }


@chatbot_router.post("/lead")
async def lead(request: LeadRequest):
    try:
        result = submit_lead(
            session_id=request.session_id,
            name=request.name,
            email=str(request.email),
            company=request.company,
            designation=request.designation,
        )
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@chatbot_router.post("/verify-otp")
async def verify(request: VerifyOtpRequest):
    try:
        result = verify_otp(session_id=request.session_id, otp=request.otp)
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@chatbot_router.post("/")
async def chat(request: Request):
    request_data = await request.json()
    user_message = request_data.get("user_message", "")
    session_id = request_data.get("session_id")

    try:
        result = chatbotService(user_message=user_message, session_id=session_id)
    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail={
                "message": str(error),
                "access": build_access_status(session_id),
            },
        ) from error

    return {
        "message": result["response"],
        "chat_history": result["chat_history"],
        "access": result["access"],
    }
