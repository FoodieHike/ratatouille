from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from psycopg2.errors import InvalidTextRepresentation



from database import Database, BotCampaignTable
from utils import callback_date_converter
import utils


routerMenu=Router()


'''class MenuStates(StatesGroup):
    wait_for_people_amount=State()'''


class ChooseIDStates(StatesGroup):
    wait_for_id=State()
    wait_for_people_amount=State()




#хэндлеры для рассчета меню

#хэндлер для начала работы с меню
@routerMenu.callback_query(lambda cb:cb.data=='food_menu_button')
async def menu_handller(qry:CallbackQuery, state:FSMContext):
    row=[[InlineKeyboardButton(text='Выбрать по ID', callback_data='chooseID')], [InlineKeyboardButton(text='Последняя запись', callback_data='lastone')]]
    mrkp=InlineKeyboardMarkup(inline_keyboard=row)
    await qry.message.answer('Меню для конкретного похода, или Вашей последней записи?', reply_markup=mrkp)
    await state.clear()



    
    
    

#хэндлер для выбора записи по ID
@routerMenu.callback_query(lambda cb:cb.data=='chooseID')
async def id_for_meny_hsndler(qry:CallbackQuery, state:FSMContext):
    await state.clear()
    await qry.message.answer('Напишите ID записи похода:')
    await qry.message.edit_reply_markup(reply_markup=None)
    await state.set_state(ChooseIDStates.wait_for_id)

    
    
x=0
#хэндлер для выбора записи по ID (второй)
@routerMenu.message(ChooseIDStates.wait_for_id)
async def choose_id_handler(msg:Message, state:FSMContext):
    record=BotCampaignTable(Database.get_connection())
    record=record.get_campaign_by_id(uid=msg.from_user.id, record_id=msg.text)
    lenght=record['enddate']-record['startdate']
    await state.set_data({'days_amount':lenght.days+1})
    data=await state.get_data()
    data['first_meal']=int(record['firstfood'])

    #определяем количество дополнительных приемов пищи:
    if record['firstfood']=='1':
        firstday_feed_amount=3
    elif record['firstfood']=='2':
        firstday_feed_amount=2
    else:
        firstday_feed_amount=1

    if record['lastfood']=='1':
        lastday_feed_amount=1
    elif record['lastfood']=='2':
        lastday_feed_amount=2
    else:
        lastday_feed_amount=3
        
    extra_meal=firstday_feed_amount+lastday_feed_amount

    data['extra_meal']=extra_meal
    await state.set_data(data)

    await msg.answer('На сколько человек планируете поход?')
    await state.set_state(ChooseIDStates.wait_for_people_amount)

    
#Хэндлер рассчитывает количество всех приемов пищи
@routerMenu.message(ChooseIDStates.wait_for_people_amount)
async def menu_process(msg:Message, state:FSMContext):
    data=await state.get_data()
    data['people_amount']=int(msg.text)
    full_days=data['days_amount']-2 #определение дней с полным набором приемов пищи
    feeds=full_days*3        #количество приемов в полных днях

    meals_full_amount=feeds+data['extra_meal']
    res=meals_full_amount*data['people_amount']
    x=meals_full_amount

    await state.set_data(data)
    await msg.answer(f'У вас получается всего {meals_full_amount} приемов пищи.\nДавайте определим, что вы будете в них есть.')

    meal_per_day=utils.meals_distributor(data['first_meal'], meals_amount=meals_full_amount)
    for i in meal_per_day.keys():
        
    await msg.answer(f'result:\n{meal_per_day}\nstorage:{data}')
    '''while x:
        if first=='завтрак':
            row=[[InlineKeyboardButton(text='Овсянка и бутер с сыром', callback_data='B1')],[InlineKeyboardButton(text='Пшенка с ковбаськой', callback_data='B2')]]
            mrkp=InlineKeyboardMarkup(inline_keyboard=row)
            await msg.answer('')'''






#хэндлер для предоставления последней записи
@routerMenu.callback_query(lambda cb:cb.data=='lastone')
async def menu_last_writing_handler(qry:CallbackQuery, state:FSMContext):
    await state.clear()
    date=await state.get_data()
    try:
        record=BotCampaignTable(Database.get_connection())
        record=record.get_campaign_last(qry.from_user.id)
        firstfood=record['firstfood']
        lastfood=record['lastfood']
        lenght=record['enddate']-record['startdate']
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
        btn=[[InlineKeyboardButton(text='Выйти в меню', callback_data='menu_button')]]
        mrkp=InlineKeyboardMarkup(inline_keyboard=btn)
        await qry.message.answer(f"Ваша запись:\nдата начала похода - {record['startdate']}\nдата окончания похода -  {record['enddate']}\nпервый прием пищи - {res}\nпоследний прием пищи - {res_s}\nдлительность- {lenght.days}\nхранилище состояний - {date}",
                         reply_markup=mrkp)
    except TypeError:
        await qry.message.answer('Такой в ваших записях нет. Попробуйте другой id')
    except ValueError:
        await qry.message.answer('Неправильная форма записи!\nВведите пожалуйста корректный id (натуральное число):')
    except InvalidTextRepresentation:
        await qry.message.answer('Неправильная форма записи!\nВведите, пожалуйста, корректный ID (натуральное число).')
    else:
        await state.clear()
        await qry.message.edit_reply_markup(reply_markup=None)








