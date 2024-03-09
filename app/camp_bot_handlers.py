from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from datetime import datetime

import models
import database
from camp_bot_models import DBGetContext, DBCreateContext, DateValidation, DateLimitError


today=datetime.now()
today=today.strftime('%Y-%m-%d')
datelimit='2100-01-01'

router=Router()

@router.message(Command('start'))
async def start_handler(msg:Message):
    await msg.answer('Привет. Я буду работать с базой данных. Пока ограничимся записью в таблицу походов и просмотром записей. Предлагаю перейти к командам:\n/create_db\n/show_db.')




#хэндлеры для команды create_db:

# Обработчик начальной команды для взаимодействий с таблицей походов
@router.message(Command('create_db'))
async def create_camp_handler(msg:Message, state:FSMContext):
    await msg.answer('Введите дату начала похода (в формате гггг-мм-дд):')
    await state.set_state(DBCreateContext.wait_for_startdate)


# Обработчик для ввода startdate 
@router.message(DBCreateContext.wait_for_startdate)
async def process_startdate(msg:Message, state:FSMContext):
    if msg.text.startswith('/'):
                await state.clear()
                await msg.answer('Повторите команду, пожалуйста')
    else:
        try:
            valid_data=DateValidation(date=msg.text)
            if msg.text<today:
                raise ValueError
            elif msg.text>datelimit:
                raise DateLimitError
            else:
                await state.set_data({'startdate': msg.text})
                await msg.answer('Введите дату окончания похода (в формате гггг-мм-дд):')
                await state.set_state(DBCreateContext.wait_for_enddate)
        except ValidationError:
            await msg.answer(f'Ошибка корректности даты\nВведите дату в корректном формате гггг-мм-дд!')
        except ValueError:
            await msg.answer('Введенная дата должна быть не ранее сегодняшнего дня!\nВведите корректную дату:')
        except DateLimitError:
            await msg.answer('Вы врядли доживете до начала похода\nПопробуйте более близкую дату:')

# Обработчик для ввода enddate
@router.message(DBCreateContext.wait_for_enddate)
async def process_enddate(msg:Message, state:FSMContext):
    if msg.text.startswith('/'):
        await state.clear()
        await msg.answer('Повторите команду, пожалуйста')
    else:
        try:
            valid_data=DateValidation(date=msg.text)
            startdate=await state.get_data()
            startdate=startdate['startdate']
            if msg.text<startdate:
                raise ValueError
            elif msg.text>datelimit:
                raise DateLimitError
            else:
                data = await state.get_data()
                data['enddate'] = msg.text
                await state.set_data(data)  # Сохраняем обновлённый словарь обратно в состояние
                await msg.answer('Введите, какой прием пищи будет первым (ответ введите цифрами 1, 2 или 3, где: завтрак-1, обед-2, ужин-3):')
                await state.set_state(DBCreateContext.wait_for_firstfood)
        except ValidationError:
            await msg.answer(f'Ошибка корректности даты.\nВведите дату в корректном формате гггг-мм-дд!')
        except ValueError:
            await msg.answer('Введенная дата должна быть позже введенной даты начала похода!\nВведите корректную дату:')
        except DateLimitError:
            await msg.answer('Вы врядли доживете до конца похода\nПопробуйте более близкую дату:')
    



# Обработчик для ввода firstfood
@router.message(DBCreateContext.wait_for_firstfood)
async def process_firstfood(msg:Message, state:FSMContext):
    try:
        models.FeedType(msg.text)
    except ValueError:
        await msg.answer('Неверный формат ввода. Введите, пожалуйста, один из предложенных вариантов:\n1 - если хотите указать завтрак;\n2 - указать обед;\n3 - ужин')
    else:
            # Получаем текущие данные
        data = await state.get_data()
        data['firstfood'] = msg.text
        await state.set_data(data)
        await msg.answer('Введите, какой прием пищи будет последним (ответ введите цифрами 1, 2 или 3, где: завтрак-1, обед-2, ужин-3):')
        await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@router.message(DBCreateContext.wait_for_lastfood)
async def process_lastfood(msg:Message, state:FSMContext):
    try:
        models.FeedType(msg.text)
    except ValueError:
        await msg.answer('Неверный формат ввода. Введите, пожалуйста, один из предложенных вариантов:\n1 - если хотите указать завтрак;\n2 - указать обед;\n3 - ужин')
    else:
                # Получаем текущие данные
        data = await state.get_data()
        data['lastfood'] = msg.text
        await state.set_data(data)
        conn=database.get_connection()
        database.create_campaign_for_bot(conn, data)
        response=database.get_campaign_bot_demo(conn)
        await msg.answer(f'Спасибо, данные у меня. ID Вашей записи - {response["id"]}')
        await state.clear()





#Обработчики команды show_db для просмотра данных из бд:

#первый хэндлер для начала работы
@router.message(Command('show_db'))
async def get_camp_handler(msg:Message, state:FSMContext):
    await msg.answer(f'Введите id записи:')
    await state.set_state(DBGetContext.get_id)

#хэндлер для предоставления записи из БД
@router.message(DBGetContext.get_id)
async def process_get_id(msg:Message, state:FSMContext):
    response=database.get_campaign(conn=database.get_connection(), campaign_id=int(msg.text))
    await msg.answer(f"Ваша запись: \nдата начала-{response['startdate']}\nдата окончания-{response['enddate']}\nпервый прием пищи-{response['firstfood']}\nконечный прием пищи-{response['lastfood']}")
    await state.clear()


