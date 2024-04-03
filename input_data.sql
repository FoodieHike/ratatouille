INSERT INTO people (ID, campaign_ID, FIO, foodpreferences)
VALUES 
('1', '1', 'Алексей', 'M'),
('2', '1', 'Олег', 'V'),
('3', '1', 'Эндрю', 'M'),
('4', '1', 'Татьяна', 'V');

INSERT INTO product (ID, PRODUCT)
VALUES ('1', 'Овсяная каша'),
       ('2', 'Сгущеное молоко'),
       ('3', 'Курага'),
       ('4', 'Джем'),
       ('5', 'Хлеб (батон)'),
       ('6', 'Сыр творожный'),
       ('7', 'Конфета'),
       ('8', 'Чай'),
       ('9', 'Кофе'),
       ('10', 'Сахар'),
       ('11', 'Пшеная каша'),
       ('12', 'Ковбаська'),
       ('13', 'Печенька'),
       ('14', 'Орехи'),
       ('15', 'Сыр твердый');
	   
INSERT INTO menu (ID, FeedType, FeedName, ProductName, Quantity, Units, FoodPreferences, ID_PRODUCT)
VALUES ('1', 'B1', 'Овсянка с курагой,бутер с сыром', 'Овсяная каша', 60, 'гр', 'N', '1'),
       ('2', 'B1', 'Овсянка с курагой,бутер с сыром', 'Сгущеное молоко', 50, 'гр', 'N', '2'),
       ('3', 'B1', 'Овсянка с курагой,бутер с сыром', 'Курага', 20, 'гр', 'N', '3'),
       ('4', 'B1', 'Овсянка с курагой,бутер с сыром', 'Джем', 20, 'гр', 'N', '4'),
       ('5', 'B1', 'Овсянка с курагой,бутер с сыром', 'Хлеб (батон)', 40, 'гр', 'N', '5'),
       ('6', 'B1', 'Овсянка с курагой,бутер с сыром', 'Сыр творожный', 30, 'гр ', 'N', '6'),
       ('7', 'B1', 'Овсянка с курагой,бутер с сыром', 'Конфета', 4, 'шт', 'N', '7'),
       ('8', 'B1', 'Овсянка с курагой,бутер с сыром', 'Чай', 5, 'гр', 'N', '8'),
       ('9', 'B1', 'Овсянка с курагой,бутер с сыром', 'Кофе', 10, 'гр', 'N', '9'),
       ('10', 'B1', 'Овсянка с курагой,бутер с сыром', 'Сахар', 5, 'гр', 'N', '10'),
       ('11', 'B2', 'Пшенка с ковбаськой', 'Пшеная каша', 60, 'гр', 'N', '11'),
       ('12', 'B2', 'Пшенка с ковбаськой', 'Ковбаська', 30, 'гр', 'M', '12'),
       ('13', 'B2', 'Пшенка с ковбаськой', 'Хлеб (батон)', 40, 'гр', 'N', '5'),
       ('14', 'B2', 'Пшенка с ковбаськой', 'Печенька ', 2, 'шт', 'N', '13'),
       ('15', 'B2', 'Пшенка с ковбаськой', 'Чай', 5, 'гр', 'N', '8'),
       ('16', 'B2', 'Пшенка с ковбаськой', 'Кофе', 10, 'гр', 'N', '9'),
       ('17', 'B2', 'Пшенка с ковбаськой', 'Сахар', 5, 'гр', 'N', '10'),
       ('18', 'B2', 'Пшенка с ковбаськой', 'Сгущеное молоко', 50, 'гр', 'N', '2'),
       ('19', 'B2', 'Пшенка с ковбаськой', 'Джем', 20, 'гр', 'N', '4'),
       ('20', 'B2', 'Пшенка с ковбаськой', 'Орехи', 20, 'гр', 'N', '14'),
       ('21', 'B2', 'Пшенка с ковбаськой', 'Сыр твердый', 30, 'гр', 'V', '15');

