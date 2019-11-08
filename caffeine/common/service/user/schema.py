from pydantic import BaseModel, EmailStr

from caffeine.common.schema import PasswordStr


class RegisterUserSchema(BaseModel):
    email: EmailStr
    password: PasswordStr


class ActivationSchema(BaseModel):
    token: str


class ResetPasswordRequestSchema(BaseModel):
    email: EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: PasswordStr
