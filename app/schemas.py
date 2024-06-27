from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Union


# Для валидации приемов пищи
class FeedType(int, Enum):
    breakfast = 1
    lunch = 2
    dinner = 3


# Для валидации записей пользователя
class CampaignBase(BaseModel):
    startdate: date
    enddate: date
    firstfood: FeedType
    lastfood: FeedType


# Для валиации взаимодейтвия с пользователем и записи данных в бд
# (тута будем добавлять всякое)
class CampaignCreate(CampaignBase):
    pass


# Для доставания записей из campaign
class Campaign(CampaignBase):
    id: int


class UserReg(BaseModel):
    name: str
    password: str


# Для валидации данных для авторизации пользователей
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    tg_id: Union[int, None] = None
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str
