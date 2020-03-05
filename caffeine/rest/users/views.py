from datetime import timedelta

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from caffeine.common.service.user.errors import UserExistError, UserNotExistError
from caffeine.common.service.user.schema import RegisterUserSchema, ResetPasswordRequestSchema, LoginSchema
from caffeine.common.service.user.service import UserService
from caffeine.rest.dependencies import get_recaptcha, get_user_service
from caffeine.rest.security import Token, fake_users_db, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, User, get_current_active_user
from caffeine.rest.users.models import RegisterRequest, ResetPasswordRequest, ChangePasswordRequest, \
    UserLoginRequest
from caffeine.rest.utils.captcha import Recaptcha

user_router = APIRouter()


@user_router.post("/register", responses={
    400: {
        "description": "Recaptcha incorrect"
    },
    409: {
        "description": "User already exists"
    },
})
async def register(register_req: RegisterRequest, recaptcha: Recaptcha = Depends(get_recaptcha),
                   user_service: UserService = Depends(get_user_service)):
    if not await recaptcha.check(register_req.captcha):
        raise HTTPException(status_code=400, detail="Recaptcha incorrect")
    try:
        schema = RegisterUserSchema(**register_req.dict())
        await user_service.register(schema)
        return True
    except UserExistError:
        raise HTTPException(status_code=409, detail="User already exists")


@user_router.get("/activate", responses={
    404: {
        "description": "Token not found"
    }
})
async def activate(token: str, user_service: UserService = Depends(get_user_service)):
    try:
        await user_service.activate(token)
        return True
    except UserNotExistError:
        raise HTTPException(status_code=404, detail="Token not found")


@user_router.post("/forget-password", responses={
    404: {
        "description": "Token not found"
    }
})
async def reset_password_request(reset_pass_req: ResetPasswordRequest, recaptcha: Recaptcha = Depends(get_recaptcha),
                                 user_service: UserService = Depends(get_user_service)):
    if not await recaptcha.check(reset_pass_req.captcha):
        raise HTTPException(status_code=400, detail="Recaptcha incorrect.")
    try:
        schema = ResetPasswordRequestSchema(**reset_pass_req.dict())
        await user_service.reset_password_request(schema)
        return True
    except UserNotExistError:
        raise HTTPException(status_code=404, detail="Token not found")


@user_router.get("/reset-password", responses={
    404: {
        "description": "Token not found"
    }
})
async def reset_password_check(token: str, user_service: UserService = Depends(get_user_service)):
    try:
        await user_service.get_by_reset_password_code(token)
        return True
    except UserNotExistError:
        raise HTTPException(status_code=404, detail="Token not found")


@user_router.post("/reset-password", responses={
    404: {
        "description": "Token not found"
    }
})
async def reset_password(change_pass_req: ChangePasswordRequest, token: str,
                         user_service: UserService = Depends(get_user_service)):
    try:
        user = await user_service.get_by_reset_password_code(token)
        await user_service.reset_password(user, change_pass_req.password)
        return True
    except UserNotExistError:
        raise HTTPException(status_code=404, detail="Token not found")



@user_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.get("/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
