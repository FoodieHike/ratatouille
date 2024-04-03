#!/bin/sh

# Запуск Uvicorn сервера в фоновом режиме
uvicorn main:app --host 0.0.0.0 --port 80 --reload &

# Запуск бота
python3 bot_main.py --reload

# Ждем завершения фоновых процессов
wait
