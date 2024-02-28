from aiogram.fsm.state import StatesGroup, State


class DBCreateContext(StatesGroup):
    wait_for_startdate=State()
    wait_for_enddate=State()
    wait_for_firstfood=State()
    wait_for_lastfood=State()

class DBGetContext(StatesGroup):
    get_id=State()