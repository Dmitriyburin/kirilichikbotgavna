import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
from tgbot.misc.states import Profile, SetAge, RequiredChannel
from tgbot.keyboards import inline
from tgbot.keyboards import reply
from tgbot.handlers.payment_system import buy_process
from tgbot.handlers.vip import vip, only_vip


async def start_registration(message: Message):
    bot = message.bot
    decor = bot['decor']
    buttons = decor.buttons
    texts = decor.texts

    await message.answer(texts['select_gender'],
                         reply_markup=inline.select_gender(buttons))


async def registration_step2_age(message: Message, state: FSMContext):
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    if message.text.isdigit() and int(message.text) in range(10, 100):
        state_data = await state.get_data()
        await state.finish()
        gender = state_data['gender']
        age = int(message.text)

        user = await data.get_user(message.from_user.id)
        ref_commercial = None
        if not user['ref'].isdigit() and user['ref'] != 'defolt':
            ref_commercial = user['ref']

        profile = await data.get_user_anonchat_profile(message.from_user.id)
        await data.edit_user_anonchat_profile(message.from_user.id, gender, age, ref_commercial, first=True)
        await message.answer(texts['profile_updated'] + '\nВыберите действие из меню:',
                             reply_markup=reply.main(buttons, profile['premium']))

    else:
        await message.answer(texts['enter_valid_age'])


async def registration_step1_gender(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

    gender = call.data.split(':')[1]
    await state.update_data(gender=gender)
    await Profile.age.set()
    await message.answer(texts['enter_age'])

    await bot.answer_callback_query(call.id)


async def set_profile(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    action = call.data.split(':')[1]
    if action == 'gender':
        await message.edit_caption(texts['select_gender'],
                                   reply_markup=inline.set_gender(buttons))
        return
    elif action == 'age':
        await message.edit_caption(texts['enter_age'])
        await SetAge.age.set()
        return


async def set_gender(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    gender = call.data.split(':')[1]

    user = await data.get_user_anonchat_profile(call['from']['id'])
    await data.edit_user_anonchat_profile(call['from']['id'], gender, user['age'])
    await call.answer('Данные сохранены')

    # костыль, чтобы в message был id пользователя, а не бота
    message.from_user.id = call['from']['id']
    await print_about_me(message, edit=True, call=call)

    await bot.answer_callback_query(call.id)


async def set_age(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons

    if message.text.isdigit() and int(message.text) in range(7, 99):
        await state.finish()

        user = await data.get_user_anonchat_profile(message.from_user.id)
        await data.edit_user_anonchat_profile(message.from_user.id, user['gender'], message.text)

        await print_about_me(message)
    else:
        await message.answer(texts['enter_valid_age'])


async def print_information(message: Message, edit=None):
    bot = message.bot
    decor = bot['decor']
    buttons = decor.buttons

    if edit:
        await message.edit_caption('', reply_markup=inline.profile(buttons))
    else:
        photo = InputFile('tgbot/data/images/profile.jpg')
        await message.answer_photo(photo, caption='', reply_markup=inline.profile(buttons))


async def print_about_me(message: Message, edit=None, call=None):
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    buttons = decor.buttons
    texts = decor.texts

    user = await data.get_user_anonchat_profile(message.from_user.id)
    gender = 'M' if user['gender'] == 'male' else 'Ж'
    vip_text = texts['no']
    if user['premium']:
        date: datetime.datetime = user['vip_date'] + datetime.timedelta(days=user['vip_days'])
        vip_text = 'до ' + date.strftime('%d.%m.%y')
    text = texts['mystats'].format(message.from_user.first_name, gender, user['age'],
                                   user['likes'], user['dislikes'], vip_text)

    if edit:
        await message.edit_caption(text, reply_markup=inline.set_profile(buttons))
        if call:
            await bot.answer_callback_query(call.id)

    else:
        photo = InputFile('tgbot/data/images/profile.jpg')
        await message.answer_photo(photo, caption=text, reply_markup=inline.set_profile(buttons))


async def print_profile(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    detail = call.data.split(':')[1]
    message.from_user.id = call['from']['id']
    message.from_user.first_name = call['from']['first_name']

    if detail == 'about_me':
        await print_about_me(message, edit=True)
    elif detail == 'buy_vip':
        await vip(message, state, back_to_profile=True)
    elif detail == 'mystats':
        user = await data.get_user_anonchat_profile(message.from_user.id)
        seconds = user['time']
        hours = seconds // 3600
        minutes = (seconds - (hours * 3600)) // 60

        date_registration_string = user['date_registration'].strftime("%d.%m.%Y, %H:%M")
        await message.edit_caption(texts['mystats2'].format(
            str(user['messages']), str(user['dialogs']), hours, minutes, date_registration_string),
            reply_markup=inline.back(buttons, 'back_to:profile'))
    await bot.answer_callback_query(call.id)


async def back_to(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = call.bot

    detail = call.data.split(':')[1]
    message.from_user.id = call['from']['id']
    message.from_user.first_name = call['from']['first_name']

    if detail == 'vip':
        await vip(message, state)

    elif detail == 'profile':
        await print_information(message, edit=True)

    elif detail == 'search':
        await only_vip(message, state, edit=True, image=True)

    await bot.answer_callback_query(call.id)


def register_anonym_chat_profile(dp: Dispatcher):
    dp.register_message_handler(start_registration, commands=["registration"], state='*')
    dp.register_callback_query_handler(registration_step1_gender, text_contains='registration')
    dp.register_message_handler(registration_step2_age, state=Profile.age)

    dp.register_callback_query_handler(set_profile, text_contains='set_profile:')
    dp.register_callback_query_handler(set_gender, text_contains='set_gender:')
    dp.register_callback_query_handler(print_profile, text_contains='print_profile:')
    dp.register_callback_query_handler(back_to, text_contains='back_to:')

    dp.register_message_handler(set_age, state=SetAge.age)
