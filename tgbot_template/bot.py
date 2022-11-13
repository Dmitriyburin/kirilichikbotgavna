#!/usr/bin/python
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from tgbot.models.database import Database
from tgbot.models.anonym_redis import AnonymChat

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter

from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.handlers.anonym_chat_profile import register_anonym_chat_profile
from tgbot.handlers.anonym_chat import register_anonym_chat
from tgbot.handlers.mailing import register_mailing
from tgbot.handlers.payment_system import register_payment
from tgbot.handlers.vip import register_vip
from tgbot.handlers.channels import register_channels

from tgbot.handlers.mailing import mailing_controller
from tgbot.handlers.vip import premium_controller

from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware, reset_reports
from tgbot.keyboards import keyboards

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_channels(dp)
    register_mailing(dp)
    register_payment(dp)
    register_vip(dp)
    register_user(dp)
    register_anonym_chat_profile(dp)
    register_anonym_chat(dp)
    register_echo(dp)


def create_database(config_db):
    database = Database(config_db.test_localhost_string_mongodb)
    return database


def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        filename="logs.log", filemode="w"
    )
    logger.info("Starting bot")
    config = load_config(".env")

    loop = asyncio.get_event_loop()

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage, loop=loop)
    bot['config'] = config
    bot['db'] = create_database(config.db)
    bot['chat'] = AnonymChat()
    bot['decor'] = config.decoration
    bot['keyboard'] = keyboards
    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    dp.loop.create_task(mailing_controller(bot, 1))
    dp.loop.create_task(premium_controller(bot, 10))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reset_reports, 'cron', day_of_week='fri', hour=6, minute=30, args=(bot['db'],))
    scheduler.start()
    executor.start_polling(dp)
    return bot


if __name__ == '__main__':
    try:
        bot = main()
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
    except Exception as e:
        logger.error(e, exc_info=True)
