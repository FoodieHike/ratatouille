import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage


from config import BOT_API
from camp_bot_handlers import router


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)
async def main():
    logger.info('бот запускается...')
    bot=Bot(token=BOT_API, parse_mode=ParseMode.HTML)
    dp=Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())





if __name__=='__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception('Неожиданое исключение:', e)
        raise