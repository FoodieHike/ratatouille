from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from datetime import datetime
from aiogram.enums.parse_mode import ParseMode

from utils import calendar, months_creator, callback_date_converter
import models
import database
from camp_bot_models import DBGetContext, DBCreateContext, DateValidation, Menu
from config import BOT_API



#глобальные переменные:
today=datetime.now()
today=today.strftime('%Y-%m-%d')


last_bot_msg={}     #сообщение для удаления


#объекты для функционирования бота:

router=Router()

bot=Bot(token=BOT_API, parse_mode=ParseMode.HTML)



#хэндлеры


#стартовый хэндлер:

@router.message(Command('start'))
async def start_handler(msg:Message, state:FSMContext):
    await state.clear()
    chat_id=msg.chat.id
    btn_create=InlineKeyboardButton(text='Создать запись', callback_data='create')
    btn_show=InlineKeyboardButton(text='Показать запись', callback_data='show')
    row=[btn_create, btn_show]
    rows=[row]
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
    greetings=await msg.answer(text='Привет. Я буду работать с базой данных. Пока ограничимся записью в таблицу походов и просмотром записей. Предлагаю перейти к командам:',
                     reply_markup=mrkp)
    last_bot_msg[chat_id]=greetings.message_id
    




#хэндлеры для команды create:
    

#альтернативный обработчик под встроенную кнопку:
@router.callback_query(lambda cb:cb.data=='create')
async def create_inline_handler(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')
    await qry.answer('Будет создана новая запись')
    mrkp=months_creator(4)
    answer_msg = await qry.message.answer('Выберите месяц для похода:', reply_markup=mrkp)
    last_bot_msg[chat_id]=answer_msg.message_id
    await state.set_state(DBCreateContext.wait_for_startdate_one)






# Обработчик начальной команды для взаимодействий с таблицей походов
@router.message(Command('create'))
async def create_camp_handler(msg:Message, state:FSMContext):
    await state.clear()
    chat_id=msg.chat.id
    await msg.answer('Будет создана новая запись')
    mrkp=months_creator(4)
    answer_msg=await msg.answer('Выберите месяц для похода:', reply_markup=mrkp)
    await state.set_state(DBCreateContext.wait_for_startdate_one)
    last_bot_msg[chat_id]=answer_msg.message_id


# Обработчик для ввода startdate  первый
@router.callback_query(DBCreateContext.wait_for_startdate_one)
async def process_startdate(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')    
    try:
        month=int(qry.data)
        year=datetime.now()
        year=year.strftime('%Y')
        markup=calendar(year, month)
        answer_msg=await qry.message.answer(text='Выберите дату:', reply_markup=markup)
        last_bot_msg[chat_id]=answer_msg.message_id
    except Exception as e:
        await qry.message.answer(f'Произошла чудовищная ошибка!\n{e}')
    else:
        await state.set_state(DBCreateContext.wait_for_startdate_two)


# Обработчик для ввода startdate второй
@router.callback_query(DBCreateContext.wait_for_startdate_two)
async def process_startdate_second(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}') 
    try:
        #валидируем дату и закидываем в хранилище данных состояний
        if qry.data<today:
            raise ValueError
        else:
            await qry.message.answer(f'Дата начала похода:\n{qry.data}')
            valid_data=DateValidation(date=qry.data)
            await state.set_data({'startdate': qry.data})

        #открываем новый календарь для следующей даты
            mrkp=months_creator(4)
            answer_msg=await qry.message.answer('Выберите месяц окончания похода:', reply_markup=mrkp)
            last_bot_msg[chat_id]=answer_msg.message_id

    #Обработчики ошибок
    except ValueError:
        if last_bot_msg:
            chat_id=qry.message.chat.id
            try:
                await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
            except Exception as e:
                await qry.message.answer(f'We got an exception:\n{e}') 
        mrkp=months_creator(4)
        answer_msg_second=await qry.message.answer('Введенная дата должна быть не ранее сегодняшнего дня!\nВведите корректную дату:', reply_markup=mrkp)
        last_bot_msg[chat_id]=answer_msg_second.message_id
        await state.set_state(DBCreateContext.wait_for_startdate_one)
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_one)

#обработчик для enddate первый    
@router.callback_query(DBCreateContext.wait_for_enddate_one)
async def process_enddate(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')
    try:
        month=int(qry.data)
        year=datetime.now()
        year=year.strftime('%Y')
        markup=calendar(year, month)
        answer_msg=await qry.message.answer(text='Выберите дату окончания похода:', reply_markup=markup)
        last_bot_msg[chat_id]=answer_msg.message_id
    except Exception as e:
        await qry.message.answer(f'Произошла чудовищная ошибка!\n{e}')
    else:
        await state.set_state(DBCreateContext.wait_for_enddate_two)


#обработчик для enddate второй
@router.callback_query(DBCreateContext.wait_for_enddate_two)
async def process_enddate_second(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')
    try:
        data = await state.get_data()
        if data['startdate'] >qry.data:
            raise ValueError
        else:
            await qry.message.answer(f'Дата окончания:\n{qry.data}')
            valid_data=DateValidation(date=qry.data)
            data = await state.get_data()
            data['enddate'] = qry.data
            await state.set_data(data)
    except ValueError:
        mrkp=months_creator(4)
        answer_msg=await qry.message.answer('Введенная дата должна быть позже введенной даты начала похода!\nВведите корректную дату:', reply_markup=mrkp)
        last_bot_msg[chat_id]=answer_msg.message_id
        await state.set_state(DBCreateContext.wait_for_enddate_one)
    else:
        row=[InlineKeyboardButton(text='Завтрак', callback_data='1'), InlineKeyboardButton(text='Обед', callback_data='2'), InlineKeyboardButton(text='Ужин', callback_data='3')]
        rows=[row]
        mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
        answer_msg_second=await qry.message.answer('Введите первый прием пищи:', reply_markup=mrkp)
        last_bot_msg[chat_id]=answer_msg_second.message_id
        await state.set_state(DBCreateContext.wait_for_firstfood)


# Обработчик для ввода firstfood
@router.callback_query(DBCreateContext.wait_for_firstfood)
async def process_firstfood(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')
    try:
        models.FeedType(qry.data)
    except Exception as e:
        await qry.message.answer(f'We got an exception here:\n{e}')
    else:
            # Получаем текущие данные
        data = await state.get_data()
        data['firstfood'] = qry.data
        await state.set_data(data)
        row=[InlineKeyboardButton(text='Завтрак', callback_data='1'), InlineKeyboardButton(text='Обед', callback_data='2'), InlineKeyboardButton(text='Ужин', callback_data='3')]
        rows=[row]
        mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
        answer_msg=await qry.message.answer('Введите последний прием пищи:', reply_markup=mrkp)
        last_bot_msg[chat_id]=answer_msg.message_id
        await state.set_state(DBCreateContext.wait_for_lastfood)


# Обработчик для ввода lastfood
@router.callback_query(DBCreateContext.wait_for_lastfood)
async def process_lastfood(qry:CallbackQuery, state:FSMContext):
    if last_bot_msg:
        chat_id=qry.message.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
        except Exception as e:
            await qry.message.answer(f'We got an exception:\n{e}')
    try:
        models.FeedType(qry.data)
    except Exception as e:
        await qry.message.answer(f'We got an exception here:\n{e}')
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
        btn=[[InlineKeyboardButton(text='Выйти в меню', callback_data='menu_button')]]
        mrkp=InlineKeyboardMarkup(inline_keyboard=btn)
        if str(lenght.days).endswith('1'):
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} день.\nID Вашей записи - {response["id"]}', reply_markup=mrkp)
        elif str(lenght.days).endswith('2') or str(lenght.days).endswith('3') or str(lenght.days).endswith('4'):
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} дня.\nID Вашей записи - {response["id"]}', reply_markup=mrkp)
        else:
            await qry.message.answer(f'Спасибо, данные у меня.\nДлительность похода составляет {lenght.days} дней.\nID Вашей записи - {response["id"]}', reply_markup=mrkp)
        await state.clear()





#Обработчики команды show для просмотра данных из бд:
        

#альтернативный обработчик под встроенную кнопку:
@router.callback_query(lambda cb:cb.data=='show')
async def create_inline_handler(qry:CallbackQuery, state:FSMContext):
    chat_id=qry.message.chat.id
    answer_msg=await qry.message.answer(f'Введите id записи:')
    last_bot_msg[chat_id]=answer_msg.message_id
    await state.set_state(DBGetContext.get_id)



#первый хэндлер для начала работы
@router.message(Command('show'))
async def get_camp_handler(msg:Message, state:FSMContext):
    await state.clear()
    chat_id=msg.chat.id
    answer_msg=await msg.answer(f'Введите id записи:')
    last_bot_msg[chat_id]=answer_msg.message_id
    await state.set_state(DBGetContext.get_id)

#хэндлер для предоставления записи из БД
@router.message(DBGetContext.get_id)
async def process_get_id(msg:Message, state:FSMContext):
    try:
        if last_bot_msg:
            chat_id=msg.chat.id
            try:
                await bot.delete_message(chat_id=chat_id, message_id=last_bot_msg[chat_id])
            except Exception as e:
                await msg.answer(f'We got an exception:\n{e}')
        response=database.get_campaign(conn=database.get_connection(), campaign_id=int(msg.text))
    except ValueError:
        await msg.answer(f'Неправильная форма записи!\nВведите пожалуйста корректный id (натуральное число):')
    except TypeError:
        await msg.answer('Такого id нет в таблице, введите, пожалуйста существующий id:')
    else:
        btn=[[InlineKeyboardButton(text='Выйти в меню', callback_data='menu_button')]]
        mrkp=InlineKeyboardMarkup(inline_keyboard=btn)
        firstfood=response['firstfood']
        lastfood=response['lastfood']
        if firstfood=='1':
            res='завтрак'
        elif firstfood=='2':
            res='обед'
        else:
            res='ужин' 

        if lastfood=='1':
            res_s='завтрак'
        elif lastfood=='2':
            res_s='обед'
        else:
            res_s='ужин' 
        
        await msg.answer(f"Ваша запись: \nДата начала-{response['startdate']}\nДата окончания-{response['enddate']}\nПервый прием пищи - {res}\nКонечный прием пищи - {res_s}",
                         reply_markup=mrkp)
        await state.clear()



#хэндлер для обработки Меню:

@router.callback_query(lambda cb:cb.data=='menu_button')
async def menu_handler(qry:CallbackQuery):
    chat_id=qry.message.chat.id
    btn_create=InlineKeyboardButton(text='Создать запись', callback_data='create')
    btn_show=InlineKeyboardButton(text='Показать запись', callback_data='show')
    row=[btn_create, btn_show]
    rows=[row]
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows)
    menu=await qry.message.answer(text='Что будем делать дальше?', reply_markup=mrkp)
    last_bot_msg[chat_id]=menu.message_id
    

#хэндлер-заглушка для help:


@router.message(Command('help'))
async def help_handler(msg:Message, state:FSMContext):
    state.clear()
    await msg.answer('Здесь пока ничего нет, опция в разработке...')
    
