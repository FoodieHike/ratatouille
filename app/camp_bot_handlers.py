from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from datetime import datetime

from utils import calendar, months_creator, callback_date_converter
import models
import database
from camp_bot_models import DBGetContext, DBCreateContext, DateValidation, DateLimitError


today=datetime.now()
today=today.strftime('%Y-%m-%d')
datelimit='2100-01-01'

router=Router()

@router.message(Command('start'))
async def start_handler(msg:Message):
    btn_create=InlineKeyboardButton(text='Создать запись', callback_data='create')
    btn_show=InlineKeyboardButton(text='Показать запись', callback_data='show')
    row=[btn_create, btn_show]
    rows=[row]
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
    await msg.answer(text='Привет. Я буду работать с базой данных. Пока ограничимся записью в таблицу походов и просмотром записей. Предлагаю перейти к командам:',
                     reply_markup=mrkp)




#хэндлеры для команды create:
    

#альтернативный обработчик под встроенную кнопку:
@router.callback_query(lambda cb:cb.data=='create')
async def create_inline_handler(qry:CallbackQuery, state:FSMContext):
    await qry.answer('Будет создана новая запись')
    mrkp=months_creator(4)
    await qry.message.answer('Выберите месяц для похода:', reply_markup=mrkp)
    await state.set_state(DBCreateContext.wait_for_startdate_one)





# Обработчик начальной команды для взаимодействий с таблицей походов
@router.message(Command('create'))
async def create_camp_handler(msg:Message, state:FSMContext):
    await msg.answer('Будет создана новая запись')
    mrkp=months_creator(4)
    await msg.answer('Выберите месяц для похода:', reply_markup=mrkp)
    await state.set_state(DBCreateContext.wait_for_startdate_one)


# Обработчик для ввода startdate  первый
@router.callback_query(DBCreateContext.wait_for_startdate_one)
async def process_startdate(qry:CallbackQuery, state:FSMContext):    
    try:
        month=int(qry.data)
        year=datetime.now()
        year=year.strftime('%Y')
        markup=calendar(year, month)
        await qry.message.answer(text='Выберите дату:', reply_markup=markup)
    except Exception as e:
        await qry.message.answer(f'Произошла чудовищная ошибка!\n{e}')
    else:
        await state.set_state(DBCreateContext.wait_for_startdate_two)


# Обработчик для ввода startdate второй
@router.callback_query(DBCreateContext.wait_for_startdate_two)
async def process_startdate_second(qry:CallbackQuery, state:FSMContext):
    try:
        #валидируем дату и закидываем в хранилище данных состояний
        if qry.data<today:
            raise ValueError
        else:
            await qry.message.answer(f'Выбранная дата:\n{qry.data}')
            valid_data=DateValidation(date=qry.data)
            await state.set_data({'startdate': qry.data})

        #открываем новый календарь для следующей даты
            mrkp=months_creator(4)
            await qry.message.answer('Выберите месяц окончания похода:', reply_markup=mrkp)

    #Обработчики ошибок
    except ValueError:
        mrkp=months_creator(4)
        await qry.message.answer('Введенная дата должна быть не ранее сегодняшнего дня!\nВведите корректную дату:', reply_markup=mrkp)
        await state.set_state(DBCreateContext.wait_for_startdate_one)
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_one)

#обработчик для enddate первый    
@router.callback_query(DBCreateContext.wait_for_enddate_one)
async def process_enddate(qry:CallbackQuery, state:FSMContext):
    try:
        month=int(qry.data)
        year=datetime.now()
        year=year.strftime('%Y')
        markup=calendar(year, month)
        await qry.message.answer(text='Выберите дату окончания похода:', reply_markup=markup)
    except Exception as e:
        await qry.message.answer(f'Произошла чудовищная ошибка!\n{e}')
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_two)


#обработчик для enddate второй
@router.callback_query(DBCreateContext.wait_for_enddate_two)
async def process_enddate_second(qry:CallbackQuery, state:FSMContext):
    try:
        data = await state.get_data()
        if data['startdate'] >qry.data:
            raise ValueError
        else:
            await qry.message.answer(f'Выбранная дата:\n{qry.data}')
            valid_data=DateValidation(date=qry.data)
            data = await state.get_data()
            data['enddate'] = qry.data
            await state.set_data(data)
    except ValueError:
        mrkp=months_creator(4)
        await qry.message.answer('Введенная дата должна быть позже введенной даты начала похода!\nВведите корректную дату:', reply_markup=mrkp)
        await state.set_state(DBCreateContext.wait_for_enddate_one)
    else:
        row=[InlineKeyboardButton(text='Завтрак', callback_data='1'), InlineKeyboardButton(text='Обед', callback_data='2'), InlineKeyboardButton(text='Ужин', callback_data='3')]
        rows=[row]
        mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
        await qry.message.answer('Введите первый прием пищи:', reply_markup=mrkp)
        await state.set_state(DBCreateContext.wait_for_firstfood)


# Обработчик для ввода firstfood
@router.callback_query(DBCreateContext.wait_for_firstfood)
async def process_firstfood(qry:CallbackQuery, state:FSMContext):
    try:
        models.FeedType(qry.data)
    except ValueError:
        await qry.message.answer('Неверный формат ввода. Введите, пожалуйста, один из предложенных вариантов:\n1 - если хотите указать завтрак;\n2 - указать обед;\n3 - ужин')
    else:
            # Получаем текущие данные
        data = await state.get_data()
        data['firstfood'] = qry.data
        await state.set_data(data)
        row=[InlineKeyboardButton(text='Завтрак', callback_data='1'), InlineKeyboardButton(text='Обед', callback_data='2'), InlineKeyboardButton(text='Ужин', callback_data='3')]
        rows=[row]
        mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
        await qry.message.answer('Введите последний прием пищи:', reply_markup=mrkp)
        await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@router.callback_query(DBCreateContext.wait_for_lastfood)
async def process_lastfood(qry:CallbackQuery, state:FSMContext):
    try:
        models.FeedType(qry.data)
    except ValueError:
        await qry.message.answer('Неверный формат ввода. Введите, пожалуйста, один из предложенных вариантов:\n1 - если хотите указать завтрак;\n2 - указать обед;\n3 - ужин')
    else:
                # Получаем текущие данные
        data = await state.get_data()
        data['lastfood'] = qry.data
        await state.set_data(data)
        conn=database.get_connection()
        database.create_campaign_for_bot(conn, data)
        response=database.get_campaign_bot_demo(conn)
        
        #определяем длину похода
        lenght=callback_date_converter(data['enddate'])-callback_date_converter(data['startdate'])
        if str(lenght.days).endswith('1'):
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} день.\nID Вашей записи - {response["id"]}')
        elif str(lenght.days).endswith('2') or str(lenght.days).endswith('3') or str(lenght.days).endswith('4'):
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} дня.\nID Вашей записи - {response["id"]}')
        else:
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} дней.\nID Вашей записи - {response["id"]}')
        await state.clear()





#Обработчики команды show_db для просмотра данных из бд:
        

#альтернативный обработчик под встроенную кнопку:
@router.callback_query(lambda cb:cb.data=='show')
async def create_inline_handler(qry:CallbackQuery, state:FSMContext):
    await qry.message.answer(f'Введите id записи:')
    await state.set_state(DBGetContext.get_id)



#первый хэндлер для начала работы
@router.message(Command('show'))
async def get_camp_handler(msg:Message, state:FSMContext):
    await msg.answer(f'Введите id записи:')
    await state.set_state(DBGetContext.get_id)

#хэндлер для предоставления записи из БД
@router.message(DBGetContext.get_id)
async def process_get_id(msg:Message, state:FSMContext):
    try:
        response=database.get_campaign(conn=database.get_connection(), campaign_id=int(msg.text))
        await msg.answer(f"Ваша запись: \nдата начала-{response['startdate']}\nдата окончания-{response['enddate']}\nпервый прием пищи-{response['firstfood']}\nконечный прием пищи-{response['lastfood']}")
    except ValueError:
        await msg.answer(f'Неправильная форма записи!\nВведите пожалуйста корректный id (натуральное число):')
    except TypeError:
        await msg.answer('Такого id нет в таблице, введите, пожалуйста существующий id:')
    else:
        await state.clear()


