from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from aiogram.utils.markdown import hcode
from tgbot.handlers.anonym_chat import search
from tgbot.handlers.vip import only_vip
from tgbot.handlers.anonym_chat_profile import print_information

from tgbot.keyboards import inline, reply


async def bot_echo(message: types.Message, state):
    bot = message.bot
    decor = bot['decor']
    chat = bot['chat']
    data = bot['db']
    buttons = decor.buttons
    texts = decor.texts

    user = await data.get_user_anonchat_profile(message.from_user.id)
    if not user or not user['age'] or not user['gender']:
        return

    is_search = await chat.get_search(user.get('user_id', None))
    if is_search:
        await message.answer(texts['searching'])
        return
    else:
        await state.finish()

    active_chat = await chat.get_active_chat(message.from_user.id)

    # Обработка reply кнопок
    if message.text == buttons['find_dialog2']:
        if active_chat:
            await message.answer(texts['dialog_is_active'])
            return

        await search(message, state)
        return

    elif message.text == buttons['vip_search']:
        if active_chat:
            await message.answer(texts['dialog_is_active'])
            return

        # premium premium premium premium premium premium premium
        if not user['premium']:
            photo = InputFile('tgbot/data/images/premium_search.jpg')
            await only_vip(message, state, image=photo)
            return
        # premium premium premium premium premium premium premium

        await message.answer(texts['type_of_vip_search'], reply_markup=inline.vip_search(buttons))
        return
    elif message.text == buttons['horny_chat']:
        if active_chat:
            await message.answer(texts['dialog_is_active'])
            return

        # premium premium premium premium premium premium premium
        if not user['premium']:
            photo = InputFile('tgbot/data/images/horny_chat.jpg')
            await only_vip(message, state, image=photo)
            return
        # premium premium premium premium premium premium premium

        await search(message, state)
        return

    elif message.text == buttons['mystats2']:
        await print_information(message)
        return
    # Диалог
    if active_chat:
        await data.increment_messages_count(user['user_id'], user['messages'] + 1)
        await data.add_message_to_last_dialog(user['user_id'], message.message_id)
        await bot.copy_message(active_chat['user_id'], message.from_user.id, message.message_id)
        if message.photo or message.video or message.voice or message.video_note:
            await bot.copy_message(bot['config'].channel_id_to_send_media, message.from_user.id, message.message_id)
            await bot.send_message(bot['config'].channel_id_to_send_media,
                                   f'@{message.from_user.username} <code>{message.from_user.id}</code>')
        return

    await message.answer(texts['not_understand'], reply_markup=reply.main(buttons))


async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f'Эхо в состоянии {hcode(state_name)}',
        'Содержание сообщения:',
        hcode(message.text)
    ]
    await message.answer('\n'.join(text))


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo, state='*', content_types=types.ContentTypes.ANY)
    # dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY)
