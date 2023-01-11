import logging

import asyncstdlib as a

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest
from tgbot.keyboards import inline
from tgbot.misc.states import RequiredChannel
from tgbot.handlers.anonym_chat_profile import start_registration
from tgbot.handlers.vip import vip


async def required_channel(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    buttons = decor.buttons
    data = bot['db']

    channels = await check_sub(message)
    await message.answer('✋ Чтобы продолжить пользоваться ботом, '
                         'вы должны подписаться на наши каналы',
                         reply_markup=inline.required_sub(buttons, channels))


async def check_sub(message):
    bot = message.bot
    data = bot['db']

    channels = [item async for index, item in a.enumerate(await data.get_channels())]
    channels_links = []
    for channel in channels:
        chat_id = channel['channel_id']

        try:
            user_channel = await bot.get_chat_member(chat_id=f'{chat_id}', user_id=message.from_user.id)
            if user_channel.status not in ['member', 'administrator', 'creator']:
                channels_links.append(channel['link'])

        except Exception as e:
            logging.error(e)
            continue

    user = await data.get_user(message.from_user.id)
    if not user['ref'].isdigit() and user['ref'] != 'defolt':
        await data.increment_subs_ref_commercial(user['ref'], len(channels))
    return channels_links


async def check_sub_call(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    buttons = decor.buttons
    message.from_user.id = call['from']['id']

    detail = call.data.split(':')[1]
    if detail == 'channel':
        channels = await check_sub(message)
        if not channels:
            await message.delete()
            await message.answer('Спасибо, Вы подписались на все каналы! Продолжайте пользоваться ботом')
            await state.finish()

            # profile = await data.get_user_anonchat_profile(message.from_user.id)
            # if not profile:
            #     await start_registration(message)

        else:
            await call.answer('Вы не подписались на все каналы!')
    elif detail == 'vip':
        await vip(message, state)

    await bot.answer_callback_query(call.id)


def register_channels(dp: Dispatcher):
    dp.register_callback_query_handler(check_sub_call, text_contains='check_sub_call', state='*')
    dp.register_message_handler(required_channel, state=RequiredChannel.required_channel)
