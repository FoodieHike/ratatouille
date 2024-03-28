from aiogram.fsm.state import StatesGroup, State
from datetime import date
from pydantic import BaseModel



#Модели для FSM контекста бота:
class DBCreateContext(StatesGroup):
    wait_for_startdate_one=State()
    wait_for_startdate_two=State()
    wait_for_enddate_one=State()
    wait_for_enddate_two=State()
    wait_for_firstfood=State()
    wait_for_lastfood=State()


class Menu(StatesGroup):
    get_to_menu=State()

class UserRegistration(StatesGroup):
    register=State()

class ShowStates(StatesGroup):      #для записи id
    putID=State()

#Модели для валидации данных:
class DateValidation(BaseModel):
    date:date


#Для ошибок и исключений:
