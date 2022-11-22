import asyncstdlib as a

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest
from tgbot.keyboards import inline
from tgbot.keyboards import reply
from tgbot.handlers.anonym_chat_profile import start_registration
from tgbot.middlewares.throttling import generate_captcha
from tgbot.misc.states import RequiredChannel
from tgbot.handlers.channels import check_sub, required_channel


async def user_start(message: Message, state=FSMContext):
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    user = await data.get_user(message.chat.id)
    profile = await data.get_user_anonchat_profile(message.from_user.id)

    ref = 'defolt' if message.text == '/start' else message.text.split()[1]
    if not user:
        ref_commercial = None
        if ref.isdigit() and int(ref) != message.from_user.id:
            ref_user_id = int(ref)
            
            ref_user = await data.get_user_anonchat_profile(ref_user_id)
            if ref_user and not ref_user['premium']:
                await data.edit_premium(ref_user_id, True, days=0, hours=1)
                await bot.send_message(ref_user_id, texts['get_free_vip'])

        elif not ref.isdigit() and ref != 'defolt':
            ref_commercial = f'https://t.me/{bot["config"].tg_bot.name}?start={ref}'
            ref = ref_commercial

        await data.add_user(message.chat.id, ref, ref_commercial=ref_commercial)

    if not profile:
        await data.add_user_anonchat_profile(message.from_user.id, None, None, ref)
    else:
        if profile['gender'] or profile['age']:
            await message.answer('Здравствуй! Кажется, мы с тобой уже виделись)',
                                 reply_markup=reply.main(buttons, profile['premium']))

            if not ref.isdigit() and ref != 'defolt':
                ref_commercial = f'https://t.me/{bot["config"].tg_bot.name}?start={ref}'
                await data.increment_ref_transition(ref_commercial)
            return

    bot[message.from_user.id] = {"is_registration": False}

    channels = await check_sub(message)
    if channels:
        await required_channel(message, None)
        return

    photo = InputFile('tgbot/data/images/start.jpg')
    await message.answer_photo(photo,
                               caption='Привет, это крутой бот, для начала нужно зарегистрироваться')
    await start_registration(message)

async def captcha_generate(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    data = bot['db']

    # костыль, чтобы в message был id пользователя, а не бота
    message.from_user.id = call['from']['id']
    await generate_captcha(bot, message, edit=True)

    await bot.answer_callback_query(call.id)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_callback_query_handler(captcha_generate, text_contains='generate_captcha')
