import random

import asyncstdlib as a
import os

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link, decode_payload
from tgbot.misc.states import AddChannel, DeleteChannel, AddRef, DeleteRef

from tgbot_template.tgbot.misc.states import StatsRef


async def admin_main(message: Message):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

    await message.answer(texts['admin'])


async def add_channel_start(message: Message):
    await message.answer('Перешлите сюда сообщение с канала, который хотите добавить')
    await AddChannel.channel.set()


async def add_channel(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    try:
        channel_id = message.forward_from_chat.id
        bot['channel_id'] = channel_id
        await message.answer('Скиньте ссылку на канал, по которой будут переходить пользователи')
        await AddChannel.link.set()
    except AttributeError as e:
        await message.answer('Cообщение неккоректное, проверьте сообщение и попробуйте еще раз: /add_sub')
        await state.finish()


async def add_link_channel(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    await message.answer('Канал добавлен')
    await data.add_channel(bot['channel_id'], message.text)

    await state.finish()


async def get_channels(message: Message):
    bot = message.bot
    data = bot['db']

    channels = []
    async for index, item in a.enumerate(await data.get_channels()):
        channels.append(f"{index + 1}) <code>{item['link']}</code>")
    if channels:
        await message.answer('\n'.join(channels))
    else:
        await message.answer('Каналов нет, воспользуйтесь /add_sub, чтобы добавить новый канал')


async def del_channel_start(message: Message):
    await message.answer('Скиньте ссылку канала, который хотите удалить')
    await DeleteChannel.channel.set()


async def del_channel(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    if await data.get_channel(message.text):
        await data.del_channel(message.text)
        await message.answer('Канал удален')
        await state.finish()
    else:
        await message.answer('Такого канала нет в ОП.\nИспользуйте /channels, чтобы посмотреть все каналы')
        await state.finish()


async def users_file(message: Message):
    bot = message.bot
    data = bot['db']

    fname = 'users.txt'
    with open(fname, 'w') as file:
        async for user in await data.get_users():
            file.write(str(user['user_id']) + '\n')

    await message.answer_document(open(fname, 'rb'))
    os.remove(fname)


async def stats(message: Message):
    bot = message.bot
    data = bot['db']
    chat = bot['chat']
    decor = bot['decor']
    texts = decor.texts

    user_stats = await data.users_count()
    messages_stats = await data.get_messages_stats()
    total_anonchat_users, male_anonchat_users, female_anonchat_users = await data.get_anonchat_users_stats()
    users_online_ids = await chat.get_anonchat_online()
    stats_all = await data.get_stats()
    price = stats_all['all_price']
    male_in_chat, female_in_chat = 0, 0
    users_in_chat = len(users_online_ids)
    dialogs_count = users_in_chat // 2

    for user_id in users_online_ids:
        user = await data.get_user_anonchat_profile(int(user_id))
        if user['gender'] == 'male':
            male_in_chat += 1
        else:
            female_in_chat += 1

    percent_male = round((male_anonchat_users / user_stats) * 100, 1)
    percent_female = round((female_anonchat_users / user_stats) * 100, 1)

    male_text = f'{male_anonchat_users} ({percent_male}%)'
    female_text = f'{female_anonchat_users} ({percent_female}%)'

    premium_users = await data.get_premium_users_count()
    average_age = stats_all['sum_average_age'] // total_anonchat_users

    await message.answer(texts['stats'].format(user_stats, total_anonchat_users, male_text,
                                               female_text, average_age, premium_users, price, dialogs_count,
                                               users_in_chat,
                                               male_in_chat, female_in_chat, messages_stats['total'],
                                               messages_stats['today']))


async def add_ref_start(message: Message):
    bot = message.bot
    data = bot['db']

    await message.answer(f'Введите число - цену реферальной ссылки (в рублях)')
    await AddRef.price.set()


async def add_ref(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    price = message.text.replace(' ', '')
    if not price.isdigit():
        await message.answer('В цене должны присутствовать только цифры, попробуйте еще раз /add_ref')
        return
    link = await get_start_link(str(random.randint(10000, 10000000)), encode=True)
    await message.answer(f'Реферальная ссылка добавлена: <code>{link}</code>')
    await data.add_ref(link, int(price))
    await state.finish()


async def get_refs(message: Message):
    bot = message.bot
    data = bot['db']

    channels = []
    async for index, item in a.enumerate(await data.get_refs()):
        channels.append(f"{index + 1}) <code>{item['link']}</code>")
    if channels:
        await message.answer('\n'.join(channels))
    else:
        await message.answer('Реферальных ссылок нет, воспользуйтесь /add_ref, чтобы добавить новую')


async def ref_stats_start(message: Message):
    await message.answer('Скиньте реферальную ссылку, статистику которой хотите получить')
    await StatsRef.ref.set()


async def ref_stats(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts

    ref = await data.get_ref(message.text)
    if ref:
        if ref['transitions'] != 0:
            price_transitions = round(ref['price'] / ref['transitions'], 3)
        else:
            price_transitions = 0

        if ref['users'] != 0:
            price_user = round(ref['price'] / ref['users'], 3)
        else:
            price_user = 0

        if ref['anonchat_users'] != 0:
            price_reg = round(ref['price'] / ref['anonchat_users'], 3)
        else:
            price_reg = 0

        average_age = ref['sum_average_age'] // ref['anonchat_users']

        await message.answer(texts['link_stats'].format(ref['users'], ref['anonchat_users'], ref['female'], ref['male'],
                                                        average_age, ref['transitions'], ref['price'],
                                                        price_transitions, price_user,
                                                        price_reg,
                                                        ref['donaters'],
                                                        ref['all_price'], ))
    else:
        await message.answer('Такой ссылки не существует')
    await state.finish()


async def del_ref_start(message: Message, state: FSMContext):
    await message.answer('Скиньте реферальную ссылку, который хотите удалить')
    await DeleteRef.ref.set()


async def del_ref(message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    if await data.get_ref(message.text):
        await data.delete_ref(message.text)
        await message.answer('Реферальная ссылка удалена')
        await state.finish()
    else:
        await message.answer('Такого реферальной ссылки нет.\nИспользуйте /refs, чтобы посмотреть все ссылки')
        await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_main, commands=["admin"], state="*", is_admin=True)
    dp.register_message_handler(add_channel_start, commands=["add_sub"], state="*", is_admin=True)
    dp.register_message_handler(add_channel, state=AddChannel.channel, is_admin=True)
    dp.register_message_handler(add_link_channel, state=AddChannel.link, is_admin=True)

    dp.register_message_handler(del_channel_start, commands=["del_sub"], state="*", is_admin=True)
    dp.register_message_handler(del_channel, state=DeleteChannel.channel, is_admin=True)

    dp.register_message_handler(get_channels, commands=["channels"], state="*", is_admin=True)
    dp.register_message_handler(users_file, commands=["users"], state="*", is_admin=True)
    dp.register_message_handler(stats, commands=["stats"], state="*", is_admin=True)

    dp.register_message_handler(add_ref_start, commands=["add_ref"], state="*", is_admin=True)
    dp.register_message_handler(add_ref, state=AddRef.price, is_admin=True)
    dp.register_message_handler(del_ref_start, commands=["del_ref"], state="*", is_admin=True)
    dp.register_message_handler(del_ref, state=DeleteRef.ref, is_admin=True)
    dp.register_message_handler(get_refs, commands=["refs"], state="*", is_admin=True)
    dp.register_message_handler(ref_stats_start, commands=["ref_stats"], state="*", is_admin=True)
    dp.register_message_handler(ref_stats, state=StatsRef.ref, is_admin=True)
