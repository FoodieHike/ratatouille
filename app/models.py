from pydantic import BaseModel
from datetime import date
from enum import Enum


# Модель для валидации приемов пищи
class FeedType(str, Enum):
    breakfast = '1'
    lunch = '2'
    dinner = '3'


# базовая модель для валидации записей пользователя
class CampaignBase(BaseModel):
    startdate: date
    enddate: date
    firstfood: FeedType
    lastfood: FeedType


# модель для валиации взаимодейтвия с пользователем и записи данных в бд
# (тута будем добавлять всякое)
class CampaignCreate(CampaignBase):
    pass


# модель для доставания записей из campaign
class Campaign(CampaignBase):
    id: int


class UserReg(BaseModel):
    name: str
    password: str
