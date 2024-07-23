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
        raise ValueError(f"No matching feed type for entity: {meal_name}")


# Для валидации записей пользователя
class CampaignBase(BaseModel):
    startdate: date
    enddate: date
    firstfood: int
    lastfood: int


# Для валиации взаимодейтвия с пользователем и записи данных в бд
# (тута будем добавлять всякое)
class CampaignCreate(CampaignBase):
    user_tg_id: int


# Для доставания записей из campaign
class Campaign(CampaignBase):
    id: int


# Для валидации данных для авторизации пользователей
# (пока нет необходимости, возможно позже модернизирую регистрацию)
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    id: int
    username: str
    password: str
    tg_id: int
    disabled: bool


class UserInDB(User):
    hashed_password: str
