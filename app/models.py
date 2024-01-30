from pydantic import BaseModel
from datetime import date
from enum import Enum

class FeedType(str, Enum):      #Модель для валидации приемов пищи
    breakfast='1'
    lunch='2'
    dinner='3'


class CampaignBase(BaseModel):      #базовая модель для валидации записей пользователя
    startdate: date
    enddate: date
    firstfood: FeedType
    lastfood: FeedType

class CampaignCreate(CampaignBase):     #модель для валиации взаимодейтвия с пользователем и записи данных в бд (тута будем добавлять всякое)
    pass

class Campaign(CampaignBase):       #модель для доставания записей из campaign
    id: int
