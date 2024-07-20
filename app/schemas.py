from pydantic import BaseModel
from datetime import date
from enum import Enum


# Для валидации приемов пищи
class FeedTypes(Enum):
    BREAKFAST = (1, 'завтрак')
    LUNCH = (2, 'обед')
    DINNER = (3, 'ужин')

    def __init__(self, num, meal_name):
        self.num = num
        self.meal_name = meal_name

    @classmethod
    def from_num(cls, num):
        for item in cls:
            if item.num == num:
                return item.meal_name
        raise ValueError(f"No matching feed type for num: {num}")

    @classmethod
    def from_string(cls, meal_name):
        for item in cls:
            if item.meal_name == meal_name:
                return item.num
        raise ValueError(f"No matching feed type for num: {meal_name}")


# Для валидации записей пользователя
class CampaignBase(BaseModel):
    startdate: date
    enddate: date
    firstfood: FeedTypes
    lastfood: FeedTypes


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
    username: str = None


class User(BaseModel):
    username: str
    tg_id: int = None
    email: str = None
    full_name: str = None
    disabled: bool = None


class UserInDB(User):
    hashed_password: str
