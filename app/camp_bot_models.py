from aiogram.fsm.state import StatesGroup, State
from datetime import date
from pydantic import BaseModel


# Модели для FSM контекста бота:
class DBCreateContext(StatesGroup):
    wait_for_startdate = State()
    wait_for_enddate = State()
    wait_for_firstfood = State()
    wait_for_lastfood = State()


class Menu(StatesGroup):
    get_to_menu = State()


class UserRegistration(StatesGroup):
    register = State()


# для записи id
class ShowStates(StatesGroup):
    putID = State()


# Модели для валидации данных:
class DateValidation(BaseModel):
    date: date
