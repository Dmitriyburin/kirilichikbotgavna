import asyncio
import logging

import aioschedule
import datetime
import random
import string

from captcha.image import ImageCaptcha
from aiogram.types import InputFile
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from tgbot.keyboards import inline
from tgbot.misc import anypay
from tgbot.handlers.channels import check_sub, required_channel
from tgbot.handlers.anonym_chat_profile import start_registration
from tgbot.handlers.anonym_chat import estimate_companion


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_pre_process_update(self, update: types.Update, data: dict):
        bot = update.bot
        if update.message:
            message = update.message
        elif update.callback_query:
            message = update.callback_query.message
            if message.from_user:
                message.from_user.id = update.callback_query['from']['id']
                call_data = update['callback_query']['data']
                if 'estimate_companion:' in call_data:
                    await estimate_companion(update.callback_query, None, call_data.split(':')[1])
                    raise CancelHandler()
            else:
                return
        else:
            return

        bot_data = bot['db']
        decor = bot['decor']
        texts = decor.texts

        # Проверка на бан
        banned_users = await bot_data.get_ban_users()
        for banned_user in banned_users:
            if banned_user['user_id'] == message.from_user.id:
                if 'hours' in banned_user:
                    seconds = (datetime.datetime.now() - banned_user['time_mute']).seconds
                    hours = seconds // 3600
                    minutes = (seconds - (hours * 3600)) // 60
                    if hours >= banned_user['hours']:
                        await bot_data.unban_user(message.from_user.id)
                    else:
                        remained_seconds = banned_user['hours'] * 3600 - seconds
                        remained_hours = remained_seconds // 3600
                        remained_minutes = (remained_seconds - (remained_hours * 3600)) // 60
                        await message.answer(texts['you_are_banned_time'].format(remained_hours, remained_minutes))
                        raise CancelHandler()
                else:
                    decor = bot['decor']
                    prices: dict = decor.prices
                    value = prices['unban']

                    price = value['price']
                    anypay_secret, anypay_shop = bot['config'].anypay.secret, bot['config'].anypay.shop
                    payment_id = await bot_data.get_anypay_payment_id()
                    sign, secret = anypay.gen_hash(price, payment_id, anypay_secret=anypay_secret,
                                                   anypay_shop=anypay_shop)
                    url = anypay.gen_url(price, payment_id, value['description'], sign, anypay_shop=anypay_shop)

                    await bot_data.add_anypay_payment_no_discount(message.from_user.id, sign, secret, payment_id,
                                                                  price=price, unban=True)

                    await message.answer(texts['you_are_banned'], reply_markup=inline.unban(url))
                    raise CancelHandler()

        # Captcha
        if bot.get(message.from_user.id) and bot[message.from_user.id].get('captcha_text'):
            if message.text == bot[message.from_user.id].get('captcha_text'):
                await message.answer('Вы разблокированы!')
                bot[message.from_user.id] = {}
            else:
                await generate_captcha(bot, message)
            raise CancelHandler()

        black_words = [word['word'] for word in await bot_data.get_black_words()]
        moderators_ids = [moder['user_id'] for moder in (await bot_data.get_moderators())]
        if message.text in black_words and (
                message.from_user.id not in moderators_ids + bot['config'].tg_bot.admin_ids):
            await generate_captcha(bot, message)
            raise CancelHandler()

        # Channels
        if update.callback_query:
            return

        white_list = await bot_data.get_premium_users() + bot['config'].tg_bot.admin_ids
        user = await bot_data.get_user(message.from_user.id)
        if message.from_user.id not in white_list and user:
            channels = await check_sub(message)
            if channels:
                await required_channel(message, None)
                raise CancelHandler()

        # Проверка на регистрацию
        user_anonchat = await bot_data.get_user_anonchat_profile(message.from_user.id)
        if not user_anonchat and not message.text.startswith('/start'):
            await start_registration(message)

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message
        :param message:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()

        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

            # Cancel current handler
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed and notify about unlocking only on last exceed
        :param message:
        :param throttled:
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta
        bot = message.bot

        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await generate_captcha(bot, message)

        # Sleep.
        await asyncio.sleep(delta)

        # Check lock status
        thr = await dispatcher.check_key(key)

        # If current message is not last with current key - do not send message
        if thr.exceeded_count == throttled.exceeded_count:
            print('время прошло')


def wrap_media(bytesio, **kwargs):
    """Wraps plain BytesIO objects into InputMediaPhoto"""
    bytesio.seek(0)
    return types.InputMediaPhoto(types.InputFile(bytesio), **kwargs)


async def generate_captcha(bot, message, edit=False):
    print('asdfas')
    image = ImageCaptcha(width=250, height=100)
    nums = list([str(i) for i in range(0, 10)])
    random.shuffle(nums)
    captcha_text = ''.join(nums[:4])
    data = image.generate(captcha_text)
    bot[message.from_user.id] = {'captcha_text': ''.join(captcha_text)}

    await message.answer_photo(data, caption='Введите текст с картинки')


async def reset_reports(data):
    await data.reset_reports_count()


async def reset_reports_count(data):
    aioschedule.every().monday.at("06:00").do(reset_reports, data)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(data):
    asyncio.create_task(reset_reports_count(data))
