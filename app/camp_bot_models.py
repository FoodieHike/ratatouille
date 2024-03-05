from aiogram.fsm.state import StatesGroup, State
from datetime import date
from pydantic import BaseModel



#Модели для FSM контекста бота:
class DBCreateContext(StatesGroup):
    wait_for_startdate=State()
    wait_for_enddate=State()
    wait_for_firstfood=State()
    wait_for_lastfood=State()

class DBGetContext(StatesGroup):
    get_id=State()



#Модели для валидации данных:
class DateValidation(BaseModel):
    date:date


#Для ошибок и исключений:
class DateLimitError(Exception):
    pass