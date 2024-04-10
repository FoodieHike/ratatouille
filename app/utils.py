from datetime import datetime, date

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import re
from collections import defaultdict



#Функции для календаря:
    
def calendar(year, month):      #функция для построения клавиатуры с календарем:
    year=int(year)
    month=int(month)
    row=[]
    rows=[]
    week=['пн', 'вт','ср','чт','пт','сб','вс']
    first_day=datetime(year,month,1)
    empty=first_day.weekday()
    #первая строка с днями недели:
    for day in week:
        row.append(InlineKeyboardButton(text=f'{day}', callback_data='weekday'))
    rows.append(row)
    row=[]
    #добавляем пустые кнопки в сетку календаря:
    for place in range(empty):
        row.append(InlineKeyboardButton(text=' ', callback_data='ignore'))
    #прописываем числа календаря:
    days_amount=(datetime(year,month+1,1) if month<12 else datetime(year+1,1,1)) -first_day
    days_amount=days_amount.days
    for day in range(1, days_amount+1):
        if month<10 and day<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-0{month}-0{day}'))
        elif month<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-0{month}-{day}'))
        elif day<10:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-{month}-0{day}'))
        else:
            row.append(InlineKeyboardButton(text=str(day), callback_data=f'{year}-{month}-{day}'))
        if len(row)==7:
            rows.append(row)
            row=[]
    #прописываем последнюю строку календаря, добавляя пустые кнопки
    if row:
        if len(row)<7:
            for i in range(len(row), 7):
                row.append(InlineKeyboardButton(text=' ', callback_data='ignore'))
        rows.append(row)
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows)    
    return mrkp





def months_creator(in_row):     #создает клавиатуру с месяцами
    months=['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
    row=[InlineKeyboardButton(text=day, callback_data=str(x)) for day, x in zip(months, range(1, len(months)+1))]
    rows=[]
    rows_fin=[]
    for i in row:
        rows.append(i)
        if len(rows)==in_row:
            rows_fin.append(rows)
            rows=[]
    mrkp=InlineKeyboardMarkup(inline_keyboard=rows_fin)
    return mrkp





def callback_date_converter(cb_date):       #конвертирует строку с датой в дату
    operand=date(int(cb_date[0:4]), int(cb_date[5:7]), int(cb_date[8:]))
    return operand


#_________________________________________________________________________________________
#Другие утилиты

def uid_creator(checker, conn, uid):        #вытаскивает tg_id из таблицы users (пока функциолнал не нужный, но может быть нужен потом, хз)
    table_row=checker(conn, uid).items()
    table_row=[list(x) for x in table_row]
    return table_row[3][1]


#утилита для распрдеделения типов приемов пищи по порядку
def meals_distributor(first_meal, meals_amount):
    day_meals=[1,2,3]
    meals_amount=[x for x in range(1, meals_amount+1)]
    result={}
    
    if first_meal==3:
        count=2
    elif first_meal==2:
        count=1
    else:
        count=0
        
    for meal in meals_amount:
        result[meal]=day_meals[count]
        count+=1
        if count>2:
            count=0
    return result


def bubble_sort(arr):
    n = len(arr)
    # Проходим по всем элементам массива
    for i in range(n):
        # Последние i элементов уже на месте
        for j in range(0, n-i-1):
            # Проходим по массиву от 0 до (n-i-1)
            # Свапаем, если элемент найден больше, чем следующий элемент
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


#для подсчета всех продуктов
def meal_total_count(data):
    if not isinstance(data, list):
        data=[data]
    product_groups = defaultdict(list)

    # шаблон для выделения строки с информацией по количеству определенного продукта
    #product_row=re.compile(r'(\d+ гр [^\n]+|\d+ шт [^\n]+)')
    product_row=re.compile(r'(\d+ [^\n]+)')

    #шаблон для выделния количества
    digits=re.compile(r'\d+')

    for item in data:
        # находим строку с продуктами и количеством по шаблону
        products=product_row.findall(item)
        for product in products:
            # выделяем только название продукта для ключа в словаре
            clean_product=re.sub(r'\d+ ', '', product)
            amount=digits.findall(product)

            #цикл для преобразования строчных значений массива amount в целые числа
            for index in range(len(amount)):
                amount[index]=int(amount[index])
            #закидываем все колличественные значения в словарь (ключ - наименование продукта)
            product_groups[clean_product].extend(amount)
        #складываем все значения в списках словаря продуктов
        for key in product_groups:
            x=0
            for amount in product_groups[key]:
                x+=amount
            product_groups[key]=x

    #конвертируем ключи и значения словаря в строки, послек чего соединяем их в одну строку
    converted=[' '.join([key, str(value)]) for key, value in product_groups.items()]
    temp_res='\n'.join(converted)

    #переносим единицы в конец строки 
    pattern=r"^(гр|шт)\s+(.*?)(?:\s+\1)?$"
    result=re.sub(pattern, r"\2 \1", temp_res, flags=re.MULTILINE)
    return result


