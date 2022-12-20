import asyncio
import datetime
import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher import FSMContext

from tgbot.keyboards import inline
from tgbot.misc.states import Search
from tgbot.handlers.admin import sent_ban_to_channel


async def search(message: Message, state: FSMContext, companion_gender=None, companion_age=None):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    data = bot['db']
    buttons = decor.buttons
    texts = decor.texts

    user = await data.get_user_anonchat_profile(message.from_user.id)

    if user['last_companion_age'] or user['last_companion_gender']:
        if not companion_age and not companion_gender:
            await data.set_last_companion_age(message.from_user.id, None)
            await data.set_last_companion_gender(message.from_user.id, None)

    companion = await chat.get_suitable_companion(message.from_user.id,
                                                  user['gender'], user['age'],
                                                  companion_gender, companion_age)
    if companion:
        if bot.get(message.from_user.id, False):
            bot[message.from_user.id]['is_report_companion'] = False
            bot[message.from_user.id]['is_react_companion'] = False
        else:
            bot[message.from_user.id] = {'is_report_companion': False}
            bot[message.from_user.id]['is_react_companion'] = False

        if bot.get(companion['user_id'], False):
            bot[companion['user_id']]['is_report_companion'] = False
            bot[companion['user_id']]['is_react_companion'] = False
        else:
            bot[companion['user_id']] = {'is_report_companion': False}
            bot[companion['user_id']]['is_react_companion'] = False

        companion = await data.get_user_anonchat_profile(companion['user_id'])

        await data.add_new_last_dialog(user['user_id'])
        await data.add_new_last_dialog(companion['user_id'])
        await data.increment_dialogs_count(user['user_id'], user['dialogs'] + 1)
        await data.increment_dialogs_count(companion['user_id'], companion['dialogs'] + 1)

        await chat.chat_found(message.from_user.id, companion['user_id'])

        if companion['premium']:
            gender = 'мужской' if user['gender'] == 'male' else 'женский'
            await bot.send_message(companion['user_id'], texts['dialog_found_vip'].format(
                user['likes'], user['dislikes'], gender, user['age']))
        else:
            await bot.send_message(companion['user_id'], texts['dialog_found'].format(
                user['likes'], user['dislikes']
            ))

        if user['premium']:
            gender = 'мужской' if companion['gender'] == 'male' else 'женский'
            await message.answer(texts['dialog_found_vip'].format(
                companion['likes'], companion['dislikes'], gender, companion['age']))
        else:
            await message.answer(texts['dialog_found'].format(
                companion['likes'], companion['dislikes']))

    else:
        photo = InputFile('tgbot/data/images/search.jpg')
        await Search.search.set()
        await message.answer_photo(photo, caption=texts['searching'])
        await chat.add_to_search(message.from_user.id, user['gender'], user['age'],
                                 companion_gender, companion_age)


async def stop_chat(message: Message, state: FSMContext, skip=False):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons

    active_chat = await chat.get_active_chat(message.from_user.id)
    companion_id = active_chat['user_id']

    time_dialog = await chat.stop_chat(message.from_user.id, companion_id)
    time_dialog = time_dialog.seconds

    await data.edit_total_time(message.from_user.id, time_dialog)
    await data.edit_total_time(companion_id, time_dialog)

    await data.set_last_companion_id(message.from_user.id, companion_id)
    await data.set_last_companion_id(companion_id, message.from_user.id)

    is_admin = False
    is_companion_admin = False
    admin_ids = bot['config'].tg_bot.admin_ids
    moderators_ids = [moder['user_id'] for moder in (await data.get_moderators())]
    for admin_id in admin_ids + moderators_ids:
        if admin_id == message.from_user.id:
            is_admin = True
        if admin_id == companion_id:
            is_companion_admin = True

    if skip:
        await message.answer(texts['dialog_stopped_skip'].format(str(time_dialog)))

        photo = InputFile('tgbot/data/images/end_dialog.jpg')
        await bot.send_photo(companion_id, photo, caption=texts['companion_stopped_dialog'].format(time_dialog))

        await bot.send_message(companion_id, texts['estimate_companion'],
                               reply_markup=inline.estimate_companion(buttons, is_admin=is_companion_admin))

        await send_advertising(message, companion_id)
        return

    photo = InputFile('tgbot/data/images/end_dialog.jpg')
    await message.answer_photo(photo, caption=texts['dialog_stopped'].format(str(time_dialog)))
    photo = InputFile('tgbot/data/images/end_dialog.jpg')

    await bot.send_photo(companion_id, photo, caption=texts['companion_stopped_dialog'].format(time_dialog))

    await message.answer(texts['estimate_companion'],
                         reply_markup=inline.estimate_companion(buttons, is_admin=is_admin))
    await bot.send_message(companion_id, texts['estimate_companion'],
                           reply_markup=inline.estimate_companion(buttons, is_admin=is_companion_admin))

    await send_advertising(message, companion_id)


async def send_advertising(message, companion_id):
    bot = message.bot
    data = bot['db']

    user = await data.get_user_anonchat_profile(message.from_user.id)
    companion = await data.get_user_anonchat_profile(companion_id)
    white_list = await data.get_premium_users() + bot['config'].tg_bot.admin_ids
    advertising = await data.get_advertising()
    for adv in advertising:
        count = 0
        if adv['count'] >= adv['views']:
            continue

        if user['user_id'] not in white_list and user['dialogs'] % adv['between_adv'] == 0:
            await bot.copy_message(message.from_user.id, adv['from_chat_id'], adv['message_id'],
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=adv['markup']))
            await data.increment_count_advertising(adv['message_id'], 1)
            count += 1

        if adv['count'] + count >= adv['views']:
            continue

        if companion['user_id'] not in white_list and companion['dialogs'] % adv['between_adv'] == 0:
            await bot.copy_message(companion_id, adv['from_chat_id'], adv['message_id'],
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=adv['markup']))
            await data.increment_count_advertising(adv['message_id'], 1)


async def stop_search(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    texts = decor.texts
    buttons = decor.buttons

    search = await chat.get_search(message.from_user.id)
    if search:
        await state.finish()
        await chat.remove_from_search(message.from_user.id)
        await message.answer(texts['searching_stopped'])


async def stop(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    texts = decor.texts

    active_chat = await chat.get_active_chat(message.from_user.id)
    if active_chat:
        await stop_chat(message, state)
        return

    search = await chat.get_search(message.from_user.id)
    if search:
        await stop_search(message, state)
        return


async def next_chat(message: Message, state):
    bot = message.bot
    chat = bot['chat']
    data = bot['db']
    active_chat = await chat.get_active_chat(message.from_user.id)
    if active_chat:
        await stop_chat(message, state, skip=True)
    user = await data.get_user_anonchat_profile(message.from_user.id)
    if user['last_companion_age']:
        await search(message, state, companion_age=user['last_companion_age'])
    elif user['last_companion_gender']:
        await search(message, state, companion_gender=user['last_companion_gender'])
    else:
        await search(message, state)


async def select_companion_details(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    data = bot['db']

    detail = call.data.split(':')[1]

    # костыль, чтобы в message был id пользователя, а не бота
    message.from_user.id = call['from']['id']
    if 'male' in detail:
        await data.set_last_companion_gender(message.from_user.id, detail)
        await data.set_last_companion_age(message.from_user.id, None)
        await search(message, state, companion_gender=detail)
    else:
        await data.set_last_companion_age(message.from_user.id, detail)
        await data.set_last_companion_gender(message.from_user.id, None)
        await search(message, state, companion_age=detail)

    await bot.answer_callback_query(call.id)


async def select_vip_search(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons

    detail = call.data.split(':')[1]
    message.from_user.id = call['from']['id']
    if detail == 'age':
        await message.edit_text(texts['select_vip_search'], reply_markup=inline.select_companion_age(buttons))
    elif detail == 'gender':
        await message.edit_text(texts['select_vip_search'], reply_markup=inline.select_companion_gender(buttons))

    await bot.answer_callback_query(call.id)


async def estimate_companion(call: CallbackQuery, state: FSMContext, detail):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons

    # detail = call.data.split(':')[1]
    message.from_user.id = call['from']['id']
    message.from_user.username = call['from']['username']

    user = await data.get_user_anonchat_profile(call['from']['id'])
    companion = await data.get_user_anonchat_profile(user['last_companion_id'])

    is_admin = False
    admin_ids = bot['config'].tg_bot.admin_ids
    moderators_ids = [moder['user_id'] for moder in (await data.get_moderators())]
    for admin_id in admin_ids + moderators_ids:
        if admin_id == message.from_user.id:
            is_admin = True

    if detail == 'like':
        bot[message.from_user.id]['is_react_companion'] = True
        await data.increment_likes(companion['user_id'], companion['likes'] + 1)
        print(bot[message.from_user.id])
        if bot[message.from_user.id]['is_report_companion']:
            await message.delete()
        else:
            await message.edit_reply_markup(reply_markup=inline.estimate_companion_short_only_report(buttons, is_admin))

    elif detail == 'dislike':
        bot[message.from_user.id]['is_react_companion'] = True
        await data.increment_dislikes(companion['user_id'], companion['dislikes'] + 1)
        if bot[message.from_user.id]['is_report_companion']:
            await message.delete()
        else:
            await message.edit_reply_markup(reply_markup=inline.estimate_companion_short_only_report(buttons, is_admin))

    elif detail == 'report':
        if is_admin:
            await data.ban_user(companion['user_id'])
            await bot.answer_callback_query(call.id)
            await message.answer(texts['user_banned'])
            await sent_ban_to_channel(bot, message, companion['user_id'])

            return

        await message.answer(texts['report_sent'])
        await bot.answer_callback_query(call.id)

        bot[message.from_user.id]['is_report_companion'] = True
        await data.increment_reports_count(companion['user_id'], companion['reports_count'] + 1)
        await send_report_file(bot, user, companion['user_id'], bot['config'].channel_id_to_send_ban)
        # if companion['reports_count'] + 1 == 30:
        #     await data.ban_user(companion['user_id'], hours=2, time_mute=datetime.datetime.now())
        # elif companion['reports_count'] + 1 >= 50:
        #     await data.ban_user(companion['user_id'])
        if bot[message.from_user.id]['is_react_companion']:
            await message.delete()
        else:
            await message.edit_reply_markup(reply_markup=inline.estimate_companion_short_only_react(buttons))

    await bot.answer_callback_query(call.id)


async def send_report_file(bot, user, companion_id, channel_id):
    if not len(user['last_dialogs'][-1]):
        return

    fname = f'dialogue_{companion_id}.txt'
    with open(fname, 'w', encoding="utf-8") as file:
        for message in user['last_dialogs'][-1]:
            file.write(f'{message}\n')

    await bot.send_document(channel_id, open(fname, 'rb'))
    os.remove(fname)


async def ban_user(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    data = bot['db']

    message.from_user.id = call['from']['id']
    user_id = call.data.split(':')[1]
    await data.ban_user(user_id)
    await bot.answer_callback_query(call.id)


async def mailing_admins_to_ban(message: Message, companion, user, count_reports):
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons

    admin_ids = bot['config'].tg_bot.admin_ids
    for admin_id in admin_ids:
        await bot.send_message(admin_id, f'Пользователь {companion["user_id"]} получил более {count_reports} жалоб',
                               reply_markup=inline.ban_user(buttons, companion['user_id']))
        await bot.send_message(admin_id, '----------Appellant:----------')
        count = 0
        for dialog in user['last_dialogs'][1:]:
            count += 1
            for message_id in dialog:
                await bot.copy_message(admin_id, message.from_user.id, message_id)
            if len(dialog) and count != len(user['last_dialogs'][1:]):
                await bot.send_message(admin_id, 'Next dialog:')

        await bot.send_message(admin_id, '----------Suspect:----------')
        count = 0
        for dialog in companion['last_dialogs'][1:]:
            count += 1
            for message_id in dialog:
                await bot.copy_message(admin_id, companion['user_id'], message_id)
            print(count, len(companion['last_dialogs'][1:]))
            if len(dialog) and count != len(companion['last_dialogs'][1:]):
                await bot.send_message(admin_id, 'Next dialog:')

        print(await data.get_last_dialogs(companion['user_id']))


async def link(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    texts = decor.texts
    active_chat = await chat.get_active_chat(message.from_user.id)
    if active_chat:
        companion_id = active_chat['user_id']
        if not message.from_user.username:
            await message.answer(texts['not_username'])
            return
        await message.answer(texts['share_to_companion_username'])
        await bot.send_message(companion_id, texts['get_username_from_companion'].format(message.from_user.username))


def register_anonym_chat(dp: Dispatcher):
    # dp.register_message_handler(stop_chat, commands=["stop_dialog"], state='*')
    # dp.register_message_handler(stop_search, commands=["stop_search"], state='*')
    dp.register_message_handler(stop, commands=["stop"], state='*')
    dp.register_message_handler(next_chat, commands=["next"], state='*')
    dp.register_message_handler(link, commands=["link"], state='*')

    dp.register_callback_query_handler(select_companion_details, text_contains='companion_details')
    dp.register_callback_query_handler(select_vip_search, text_contains='search_by')
    dp.register_callback_query_handler(estimate_companion, text_contains='estimate_companion:')
    dp.register_callback_query_handler(ban_user, text_contains='ban_user:')
