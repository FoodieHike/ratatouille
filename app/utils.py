from collections import defaultdict
from typing import Union

from aiogram.types import Message, CallbackQuery

from schemas import FeedTypes


def syntax_specifier(lenght):
    lenght = str(lenght)[-1]
    return {
        '1': 'день', '2': 'дня', '3': 'дня', '4': 'дня'
    }.get(lenght, 'дней')


# формирует словарь день: [список приемов пищи]
# для отправки сообщений пользователю
def meal_counter(
        first_meal: int,
        last_day: int,
        last_meal: int
) -> defaultdict:
    meals_list = defaultdict(list)
    marker = False
    for day in range(1, last_day+1):
        if day == last_day:
            for meal in FeedTypes:
                if meal.num == last_meal:
                    meals_list[day].append(meal.meal_name)
                    break
                meals_list[day].append(meal.meal_name)
        else:
            for meal in FeedTypes:
                if meal.num == first_meal:
                    marker = True
                if marker:
                    meals_list[day].append(meal.meal_name)
    return meals_list


# для определения дополнительных приемов пищи
def extra_meal_counter(record: dict) -> int:
    return {
        1: 3, 2: 2, 3: 1
    }.get(record['firstfood'], '') + record['lastfood']


# Создает инфу о сообщении и отсылает сообщение со списком блюд пользователю
def put_message_into_state(
    day: Union[int, str],
    meal_message: Message,
    data: dict,
    feed_type: Union[int, str]
) -> None:
    message_value = f"{day}${feed_type}"
    # прописываем в соловарь состояний
    # номер сообщения с привязанным к нему приемом пищи
    data[f"message_id{meal_message.message_id}"] = message_value


def data_from_db_converter(record_from_db: dict) -> str:
    converted_data = '\n'.join(
        [f'{row["productname"]} {row["quantity"]} {row["units"]}'
         for row in record_from_db]
    )
    return converted_data


# формирует текст с заголовком и меню на день
def get_daily_menu_titled(
        record: dict,
        data: dict,
        query: CallbackQuery
) -> tuple:
    daily_menu = data_from_db_converter(record)
    feed_name = record[0]['feedname']
    # достаем из хранилища состояний сообщение о приеме пищи и дне
    # и разделяем их
    day_meal_per_message = data[f'message_id{query.message.message_id}']
    day, meal = day_meal_per_message.split('$')
    meal_products = (f'День похода - {day}, '
                     f'прием пищи - {meal}.'
                     f'\n({feed_name}):\n{daily_menu}')
    return (meal_products, meal, day)


# для подсчета всех дневных меню
def total_by_feedtype(data: dict, feedtypes: list) -> None:
    inner_data = defaultdict(int)
    for i in feedtypes:
        if i not in inner_data.keys():
            inner_data[i] = 1
        else:
            inner_data[i] += 1
    data['feedtypes_amount'] = inner_data


# создает данные для формирования pdf
def sort_daily_menu(data: dict) -> list:
    # здесь повезло, что сорртировка лексически
    # распределит слова в правильном порядке,
    # нет необходимости нагружать лишней логикой
    daily_menu_keys = sorted(
        [key for key in data.keys()
         if key.startswith('daily_menu')]
    )
    daily_menu_list = [data[key] for key in daily_menu_keys]

    # конвертируем данные для общего подсчета и считаем
    # total = '\n'.join(daily_menu_list)
    return daily_menu_list


# создает из списка менюшек словарь
# с ключем feedtype значением количеством этих приемов пищи
def feedtypes_counter(data: dict, feedtypes: list) -> None:
    inner_data = defaultdict(int)
    for i in feedtypes:
        if i not in inner_data.keys():
            inner_data[i] = 1
        else:
            inner_data[i] += 1
    data['feedtypes_amount'] = inner_data
