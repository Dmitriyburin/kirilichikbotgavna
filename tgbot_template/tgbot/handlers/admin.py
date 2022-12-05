import json
import random
import datetime
import asyncstdlib as a
import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link, decode_payload
from tgbot.misc.states import AddChannel, DeleteChannel, AddRef, DeleteRef, BanUser, AddModerator, DeleteModerator
from tgbot.misc.states import StatsRef, DeleteBlackWord, AddBlackWord, AddVip, AddAdvertising
from tgbot.keyboards import inline


async def admin_main(message: Message):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

    await message.answer(texts['admin'])


async def add_channel_start(message: Message):
    await message.answer('Перешлите сюда id канала, который хотите добавить')
    await AddChannel.channel.set()


async def add_channel(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    try:
        bot['channel_id'] = int(message.text)
        await message.answer('Скиньте ссылку на канал, по которой будут переходить пользователи')
        await AddChannel.link.set()
    except Exception as e:
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

    percent_male = round((male_anonchat_users / total_anonchat_users) * 100, 1)
    percent_female = round((female_anonchat_users / total_anonchat_users) * 100, 1)

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

    await message.answer(f'Введите дату в формате день.месяц.год (Пример: 20.11.2022)')
    await AddRef.date.set()


async def add_ref_date(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    try:
        date = datetime.datetime.strptime(message.text, "%d.%m.%Y")

        await message.answer(f'Введите число - цену реферальной ссылки (в рублях)')
        await AddRef.price.set()
        await state.update_data(date=date)
    except Exception as e:
        print(e)
        await message.answer(f'Неверно заданное время, попробуйте еще раз: /add_ref')
        await state.finish()


async def add_ref(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    price = message.text.replace(' ', '')
    if not price.isdigit():
        await message.answer('В цене должны присутствовать только цифры, попробуйте еще раз /add_ref')
        await state.finish()
        return
    await state.update_data(price=price)
    await message.answer(f'Введите контакт (пример: @anyone)')
    await AddRef.contact.set()


async def add_ref_contact(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    contact = message.text
    link = await get_start_link(str(random.randint(10000, 10000000)), encode=True)
    price = (await state.get_data())['price']
    date = (await state.get_data())['date']
    print(contact, price, link)
    await message.answer(f'Реферальная ссылка добавлена: <code>{link}</code>')
    await data.add_ref(link, int(price), contact, date)
    await state.finish()


async def get_refs(message: Message):
    bot = message.bot
    data = bot['db']

    channels_text = []
    channels = list(sorted([i async for i in (await data.get_refs())], key=lambda x: x['date']))
    for index, item in enumerate(channels):

        if item['transitions'] != 0:
            price_transitions = round(item['price'] / item['transitions'], 3)
        else:
            price_transitions = 0

        channels_text.append(
            f"{index + 1}) <code>{item['link']}</code>\n<b>Дата:</b>"
            f" {item['date'].date()}\n<b>Цена:</b> {item['price']} руб \n<b>Контакт:</b> {item['contact']}\n"
            f"<b>Цена перехода:</b> {price_transitions}\n")
    if channels_text:
        await message.answer('\n'.join(channels_text))
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
        ref_stat = await data.ref_stats_online(ref['link'])
        male = ref_stat['male']
        female = ref_stat['female']
        anonchat_users = ref_stat['all_anonchat_users']
        users = ref_stat['all_users']
        average_age = int(ref_stat['average_age'])

        if ref['transitions'] != 0:
            price_transitions = round(ref['price'] / ref['transitions'], 3)
        else:
            price_transitions = 0

        if users != 0:
            price_user = round(ref['price'] / users, 3)
        else:
            price_user = 0

        if anonchat_users != 0:
            price_reg = round(ref['price'] / anonchat_users, 3)
        else:
            price_reg = 0
            average_age = 0

        await message.answer(texts['link_stats'].format(users, anonchat_users, male, female,
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


async def ban_user_start(message: Message, state: FSMContext):
    await message.answer('Введите id пользователя, которого хотите забанить')
    await BanUser.user_id.set()


async def ban_user(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    user_id = message.text
    if not user_id.isdigit():
        await message.answer('Id должен быть числом, попробуйте еще раз: /ban')
        await state.finish()
        return

    await data.ban_user(int(user_id))
    await message.answer('Пользователь забанен')
    await state.finish()


async def get_moderators(message: Message):
    bot = message.bot
    data = bot['db']

    text = []
    moderators = await data.get_moderators()
    for index, item in enumerate(moderators):
        user_id = item['user_id']
        username = (await bot.get_chat(user_id)).username
        text.append(
            f"{index + 1}) <code>{user_id}</code> - @{username}")
    if text:
        await message.answer('\n'.join(text))
    else:
        await message.answer('Модераторов нет, воспользуйтесь /add_moder, чтобы добавить нового')


async def add_moderator_start(message: Message, state: FSMContext):
    await message.answer('Введите id пользователя, которого хотите сделать модератором')
    await AddModerator.user_id.set()


async def add_moderator(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    user_id = message.text
    if not user_id.isdigit():
        await message.answer('Id должен быть числом, попробуйте еще раз: /add_moder')
        await state.finish()
        return

    await data.add_moderator(int(user_id))
    await message.answer('Модератор добавлен')
    await state.finish()


async def delete_moderator_start(message: Message, state: FSMContext):
    await message.answer('Введите id пользователя, которого хотите удалить из модераторов')
    await DeleteModerator.user_id.set()


async def delete_moderator(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    user_id = message.text
    if not user_id.isdigit():
        await message.answer('Id должен быть числом, попробуйте еще раз: /del_moder')
        await state.finish()
        return

    await data.delete_moderator(int(user_id))
    await message.answer('Модератор удален')
    await state.finish()


async def get_black_words(message: Message):
    bot = message.bot
    data = bot['db']

    text = []
    black_words = await data.get_black_words()
    for index, item in enumerate(black_words):
        text.append(
            f"{index + 1}) <code>{item['word']}</code>")
    if text:
        await message.answer('\n'.join(text))
    else:
        await message.answer('Слов в черном списке нет, воспользуйтесь /add_word, чтобы добавить нового')


async def add_black_word_start(message: Message, state: FSMContext):
    await message.answer('Введите слово/фразу, которую хотите добавить в черный список')
    await AddBlackWord.word.set()


async def add_black_word(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    word = message.text
    await data.add_black_word(word)
    await message.answer('Слово/фраза занесена в черный список')
    await state.finish()


async def delete_black_word_start(message: Message, state: FSMContext):
    await message.answer('Введите слово/фразу, которую хотите удалить из черного списка')
    await DeleteBlackWord.word.set()


async def delete_black_word(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']

    word = message.text
    await data.delete_black_word(word)

    await message.answer('Слово/фраза удалена')
    await state.finish()


async def add_vip_start(message: Message, state: FSMContext):
    await message.answer('Введите id пользователя, которому хотите выдать VIP')
    await AddVip.user_id.set()


async def add_vip_days(message: Message, state: FSMContext):
    user_id = message.text
    if not user_id.isdigit():
        await message.answer('Id должен быть числом, попробуйте еще раз: /give_vip')
        await state.finish()
        return
    await state.update_data(user_id=user_id)
    await message.answer('Введите количество дней')
    await AddVip.days.set()


async def add_vip(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    days = message.text
    if not days.isdigit():
        await message.answer('Количество дней должно быть числом, попробуйте еще раз: /give_vip')
        await state.finish()
        return

    user_id = (await state.get_data())['user_id']
    await data.edit_premium(int(user_id), True, days=days)
    await message.answer('VIP выдан')
    await state.finish()


async def add_advertising_start(message: Message, state: FSMContext):
    await message.answer('Скиньте пост, который хотите добавить в систему показов')
    await AddAdvertising.message_id.set()


async def add_advertising(message: Message, state: FSMContext):
    markup = None
    if message.reply_markup:
        markup = message.reply_markup.to_python()['inline_keyboard']
    await state.update_data(message_id=message.message_id, markup=markup)
    await message.answer('Введите количество показов (число)')
    await AddAdvertising.views.set()


async def add_advertising_views(message: Message, state: FSMContext):
    bot = message.bot

    views = message.text
    if not views.isdigit():
        await message.answer('Количество показов должно быть числом, попробуйте еще раз: /add_adv')
        await state.finish()
        return

    await state.update_data(views=int(views))
    await bot.copy_message(message.from_user.id, message.from_user.id, (await state.get_data())['message_id'],
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=(await state.get_data())['markup']))

    await message.answer('Вы уверены, что хотите добавить данный пост в систему показов?',
                         reply_markup=inline.yes_or_not('add_advertising_callback'))
    await AddAdvertising.accept.set()


async def add_advertising_callback(call: CallbackQuery, state: FSMContext):
    bot = call.bot
    data = bot['db']

    detail = call.data.split(':')[1]
    if detail == 'yes':
        answer = (await state.get_data('message_id'))
        await data.add_advertising(answer['message_id'], markup=answer['markup'],
                                   from_chat_id=call.message.chat.id, views=answer['views'])
        await call.message.answer('Пост добавлен в систему показов')
    elif detail == 'no':
        await call.message.answer('Отменено')
    await call.message.delete()
    await state.finish()
    await bot.answer_callback_query(call.id)


async def get_advertising(message: Message):
    bot = message.bot
    data = bot['db']

    advertising = (await data.get_advertising())
    if len(advertising):
        await message.answer('Система показов: ')
    else:
        await message.answer('Ни одной рекламы не добавлено, воспользуйтесь /add_adv')

    count = 0
    for adv in advertising:
        count += 1
        await bot.copy_message(message.from_user.id, adv['from_chat_id'], adv['message_id'],
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=adv['markup']))
        await message.answer(f'Количество показов: {adv["count"]}/{adv["views"]}\n\nУдалить рекламу сверху',
                             reply_markup=inline.delete(f'advertising:{adv["message_id"]}'))
        if count < len(advertising):
            await message.answer('-' * 100)


async def delete(call: CallbackQuery, state: FSMContext):
    bot = call.bot
    data = bot['db']

    detail = call.data.split(':')[1]
    if detail == 'advertising':
        message_id = call.data.split(':')[2]
        await data.delete_advertising(int(message_id))
        await call.message.delete()
    await bot.answer_callback_query(call.id)


async def get_user_id(message: Message):
    bot = message.bot
    chat = bot['chat']

    active_chat = await chat.get_active_chat(message.from_user.id)
    if active_chat:
        companion = await bot.get_chat(active_chat['user_id'])
        await message.answer(f'@{companion.username} <code>{companion.id}</code>')
    else:
        await message.answer('У вас нет активного диалога, попробуйте еще раз')


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
    dp.register_message_handler(add_ref_date, state=AddRef.date, is_admin=True)
    dp.register_message_handler(add_ref_contact, state=AddRef.contact, is_admin=True)
    dp.register_message_handler(add_ref, state=AddRef.price, is_admin=True)
    dp.register_message_handler(del_ref_start, commands=["del_ref"], state="*", is_admin=True)
    dp.register_message_handler(del_ref, state=DeleteRef.ref, is_admin=True)
    dp.register_message_handler(get_refs, commands=["refs"], state="*", is_admin=True)
    dp.register_message_handler(ref_stats_start, commands=["ref_stats"], state="*", is_admin=True)
    dp.register_message_handler(ref_stats, state=StatsRef.ref, is_admin=True)

    dp.register_message_handler(ban_user_start, commands=["ban"], state="*", is_admin=True)
    dp.register_message_handler(ban_user_start, commands=["ban"], state="*", is_moderator=True)
    dp.register_message_handler(ban_user, state=BanUser.user_id, is_admin=True)
    dp.register_message_handler(ban_user, state=BanUser.user_id, is_moderator=True)

    dp.register_message_handler(add_moderator_start, commands=["add_moder"], state="*", is_admin=True)
    dp.register_message_handler(add_moderator, state=AddModerator.user_id, is_admin=True)
    dp.register_message_handler(delete_moderator_start, commands=["del_moder"], state="*", is_admin=True)
    dp.register_message_handler(delete_moderator, state=DeleteModerator.user_id, is_admin=True)
    dp.register_message_handler(get_moderators, commands=["moders"], state="*", is_admin=True)

    dp.register_message_handler(add_black_word_start, commands=["add_word"], state="*", is_admin=True)
    dp.register_message_handler(add_black_word, state=AddBlackWord.word, is_admin=True)
    dp.register_message_handler(delete_black_word_start, commands=["del_word"], state="*", is_admin=True)
    dp.register_message_handler(delete_black_word, state=DeleteBlackWord.word, is_admin=True)
    dp.register_message_handler(get_black_words, commands=["words"], state="*", is_admin=True)

    dp.register_message_handler(add_vip_start, commands=["give_vip"], state="*", is_admin=True)
    dp.register_message_handler(add_vip_days, state=AddVip.user_id, is_admin=True)
    dp.register_message_handler(add_vip, state=AddVip.days, is_admin=True)

    dp.register_message_handler(add_advertising_start, commands=["add_adv"], state="*", is_admin=True)
    dp.register_message_handler(add_advertising, state=AddAdvertising.message_id, is_admin=True)
    dp.register_message_handler(add_advertising_views, state=AddAdvertising.views, is_admin=True)
    dp.register_callback_query_handler(add_advertising_callback, state=AddAdvertising.accept,
                                       text_contains='add_advertising_callback:',
                                       is_admin=True)
    dp.register_message_handler(get_advertising, commands=["get_adv"], state="*", is_admin=True)
    dp.register_callback_query_handler(delete,
                                       text_contains='delete:',
                                       is_admin=True)

    dp.register_message_handler(get_user_id, commands=["id"], state="*", is_admin=True)
