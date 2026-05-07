from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.actions.auth import authenticate_user
# from api.actions.security import create_access_token
from api.models import Token
from db.session import get_db

register_router = APIRouter()

login_router = APIRouter()

@login_router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
    #     expires_delta=access_token_expires,
    # )
    access_token = "123"
    return {"access_token": access_token, "token_type": "bearer"}