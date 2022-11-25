import datetime
import random

import asyncstdlib as a
import os

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext


async def moderator_main(message: Message):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

    await message.answer(texts['moderator'])


def register_moderator(dp: Dispatcher):
    dp.register_message_handler(moderator_main, commands=["moder"], state="*", is_moderator=True)

