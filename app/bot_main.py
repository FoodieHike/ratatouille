import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from camp_bot_handlers import routerCampaign, bot
from menu_bot_handlers import routerMenu


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info('бот запускается...')
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(routerCampaign, routerMenu)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception('Неожиданое исключение:', e)

