from datetime import timedelta, datetime, timezone
from typing import Annotated, Union
from fastapi import Depends, HTTPException, status, Request
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import TokenData, User, UserInDB
import database


# Create a PassLib "context".
# This is what will be used to hash and verify passwords.
pwd_context = CryptContext(schemes=['bcrypt'])


# And another utility to verify if a received password matches the hash stored.
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Create a utility function to hash a password coming from the user.
def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        user = dict(await database.get_user_by_name(username))
        if user:
            if 'password' in user:
                user['hashed_password'] = user.pop('password')
            return UserInDB(**user)
    except TypeError:
        raise credential_exception


# And another one to authenticate and return a user.
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Create a utility function to generate a new access token.
def create_access_token(
        data: dict,
        expires_delta: Union[timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Update get_current_user to receive the same token as before,
# but this time, using JWT tokens.
async def get_current_user(token: str):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credential_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


class AdminAuth(AuthenticationBackend):
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("access_token")
        if not token:
            return False
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username:
                return True
        except InvalidTokenError:
            return False
        return False

    async def login(self, request: Request) -> Union[RedirectResponse, bool]:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        user = await authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        request.session.update({'access_token': access_token})
        return RedirectResponse(url='/admin')

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
