from pydantic import BaseModel

class ChangePinRequest(BaseModel):
    old_pin: str
    new_pin: str

class LoginRequest(BaseModel):
    pin: str  # 4 หลัก

class LoginResponse(BaseModel):
    access_token: str
    role: str
    name: str