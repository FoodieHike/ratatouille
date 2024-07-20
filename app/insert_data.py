import datetime

from sqlalchemy.orm import Session

from app.config import HASHED_PASSWORD
from models import User, Product, People, Menu, Campaign


product_values = [
    {'id': 1, 'product': 'Овсяная каша'},
    {'id': 2, 'product': 'Сгущеное молоко'},
    {'id': 3, 'product': 'Курага'},
    {'id': 4, 'product': 'Джем'},
    {'id': 5, 'product': 'Хлеб (батон)'},
    {'id': 6, 'product': 'Сыр творожный'},
    {'id': 7, 'product': 'Конфета'},
    {'id': 8, 'product': 'Чай'},
    {'id': 9, 'product': 'Кофе'},
    {'id': 10, 'product': 'Сахар'},
    {'id': 11, 'product': 'Пшеная каша'},
    {'id': 12, 'product': 'Ковбаська'},
    {'id': 13, 'product': 'Печенька'},
    {'id': 14, 'product': 'Орехи'},
    {'id': 15, 'product': 'Сыр твердый'}
]


menu_values = [
    {'id': 1, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Овсяная каша', 'quantity': 60, 'units': 'гр', 'food_preferences': 'N', 'id_product': 1},
    {'id': 2, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Сгущеное молоко', 'quantity': 50, 'units': 'гр', 'food_preferences': 'N', 'id_product': 2},
    {'id': 3, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Курага', 'quantity': 20, 'units': 'гр', 'food_preferences': 'N', 'id_product': 3},
    {'id': 4, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Джем', 'quantity': 20, 'units': 'гр', 'food_preferences': 'N', 'id_product': 4},
    {'id': 5, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Хлеб (батон)', 'quantity': 40, 'units': 'гр', 'food_preferences': 'N', 'id_product': 5},
    {'id': 6, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Сыр творожный', 'quantity': 30, 'units': 'гр ', 'food_preferences': 'N', 'id_product': 6},
    {'id': 7, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Конфета', 'quantity': 4, 'units': 'шт', 'food_preferences': 'N', 'id_product': 7},
    {'id': 8, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Чай', 'quantity': 5, 'units': 'гр', 'food_preferences': 'N', 'id_product': 8},
    {'id': 9, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Кофе', 'quantity': 10, 'units': 'гр', 'food_preferences': 'N', 'id_product': 9},
    {'id': 10, 'feed_type': 'B1', 'feed_name': 'Овсянка с курагой,бутер с сыром', 'product_name': 'Сахар', 'quantity': 5, 'units': 'гр', 'food_preferences': 'N', 'id_product': 10},
    {'id': 11, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Пшеная каша', 'quantity': 60, 'units': 'гр', 'food_preferences': 'N', 'id_product': 11},
    {'id': 12, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Ковбаська', 'quantity': 30, 'units': 'гр', 'food_preferences': 'M', 'id_product': 12},
    {'id': 13, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Хлеб (батон)', 'quantity': 40, 'units': 'гр', 'food_preferences': 'N', 'id_product': 5},
    {'id': 14, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Печенька ', 'quantity': 2, 'units': 'шт', 'food_preferences': 'N', 'id_product': 13},
    {'id': 15, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Чай', 'quantity': 5, 'units': 'гр', 'food_preferences': 'N', 'id_product': 8},
    {'id': 16, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Кофе', 'quantity': 10, 'units': 'гр', 'food_preferences': 'N', 'id_product': 9},
    {'id': 17, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Сахар', 'quantity': 5, 'units': 'гр', 'food_preferences': 'N', 'id_product': 10},
    {'id': 18, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Сгущеное молоко', 'quantity': 50, 'units': 'гр', 'food_preferences': 'N', 'id_product': 2},
    {'id': 19, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Джем', 'quantity': 20, 'units': 'гр', 'food_preferences': 'N', 'id_product': 4},
    {'id': 20, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Орехи', 'quantity': 20, 'units': 'гр', 'food_preferences': 'N', 'id_product': 14},
    {'id': 21, 'feed_type': 'B2', 'feed_name': 'Пшенка с ковбаськой', 'product_name': 'Сыр твердый', 'quantity': 30, 'units': 'гр', 'food_preferences': 'V', 'id_product': 15}
]


users_values = [{'username': 'Admin', 'tg_id': 1, 'disabled': False, 'password': HASHED_PASSWORD}]


campaign_values = [{'startdate': datetime.date(2024, 12, 1), 'enddate': datetime.date(2024, 12, 31),'firstfood': 1, 'lastfood': 2, 'user_tg_id': 1}]

people_values = [
    {'id': 1, 'campaign_id': 1, 'fio': 'Алексей', 'food_preferences': 'M'},
    {'id': 2, 'campaign_id': 1, 'fio': 'Олег', 'food_preferences': 'V'},
    {'id': 3, 'campaign_id': 1, 'fio': 'Эндрю', 'food_preferences': 'M'},
    {'id': 4, 'campaign_id': 1, 'fio': 'Татьяна', 'food_preferences': 'V'}
]


values = [product_values, menu_values, users_values, campaign_values, people_values]
tables = [Product, Menu, User, Campaign, People]


def init_db(engine, values, table):
    for value in values:
        with Session(engine) as session:
            row = table(**value)
            session.add(row)
            session.commit()
