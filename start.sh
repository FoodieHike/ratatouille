#!/bin/sh

# Запуск Uvicorn сервера в фоновом режиме
uvicorn main:app --host 0.0.0.0 --port 80 --reload &

# Запуск бота
python3 camp_bot.py --reload

# Ждем завершения фоновых процессов
wait
