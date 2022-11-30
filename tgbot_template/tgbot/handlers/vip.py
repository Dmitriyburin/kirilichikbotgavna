import asyncio
import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from tgbot.keyboards import inline
from tgbot.handlers.payment_system import buy_process

from tgbot.misc import anypay


async def vip(message: Message, state: FSMContext, back_to_profile=None, back_to_search=False, edit=False,
              companion_id=None):
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons
    prices: dict = decor.prices

    user = await data.get_user_anonchat_profile(message.from_user.id)
    if user['premium'] and not companion_id:

        if back_to_profile:
            markup = inline.back(buttons, 'back_to:profile')
        else:
            markup = None

        if user['vip_days'] == 'forever':
            vip_text = '🏆 У вас уже есть вечная подписка'
        else:
            date: datetime.datetime = user['vip_date'] + datetime.timedelta(days=user['vip_days'])
            vip_text = f'🏆 У вас уже есть подписка, она заканчивается {date.strftime("%d.%m.%y")}'

        if back_to_profile or back_to_search:
            await message.edit_caption(vip_text,
                                       reply_markup=markup)
        else:
            await message.answer(vip_text,
                                 reply_markup=markup)

        return

    urls = {}
    for key, value in prices.items():
        if key == 'reset_react':
            continue

        price = value['price']
        anypay_secret, anypay_shop = bot['config'].anypay.secret, bot['config'].anypay.shop
        payment_id = await data.get_anypay_payment_id()
        sign, secret = anypay.gen_hash(price, payment_id, anypay_secret=anypay_secret, anypay_shop=anypay_shop)
        url = anypay.gen_url(price, payment_id, 'топ', sign, anypay_shop=anypay_shop)
        urls[key] = url

        if companion_id:
            await data.add_anypay_payment_no_discount(message.from_user.id, sign, secret, payment_id, days=key,
                                                      price=price, companion_id=companion_id)
        else:
            await data.add_anypay_payment_no_discount(message.from_user.id, sign, secret, payment_id, days=key,
                                                      price=price)
    markup = inline.vip_privileges(prices, urls)

    time_mid = time_to_midnight()
    if companion_id:
        message_text = texts['vip_privileges_companion'].format(time_mid['hours'], time_mid['minutes'],
                                                                time_mid['seconds'])
    else:
        message_text = texts['vip_privileges'].format(time_mid['hours'], time_mid['minutes'], time_mid['seconds'])

    if back_to_profile:
        markup.add(inline.back_button('back_to:profile'))
        await message.edit_caption(message_text,
                                   reply_markup=markup)
    elif back_to_search:
        markup.add(inline.back_button('back_to:search'))
        await message.edit_caption(message_text,
                                   reply_markup=markup)
    else:
        await message.answer(message_text, reply_markup=markup)


async def buy_vip(call: CallbackQuery, state: FSMContext):
    message = call.message
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons
    prices = decor.prices

    days = int(call.data.split(':')[1])

    await buy_process(message, days, markup=inline.back(buttons, 'back_to:vip'))

    await bot.answer_callback_query(call.id)


async def free_vip(message: Message, back_to_search=False, edit=False):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

    if edit:
        await message.edit_text(texts['free_vip'].format(f'https://t.me/{bot["config"].tg_bot.name}'
                                                         f'?start={message.from_user.id}'))
    elif back_to_search:
        markup = InlineKeyboardMarkup()
        markup.add(inline.back_button('back_to:search'))
        await message.edit_caption(texts['free_vip'].format(f'https://t.me/{bot["config"].tg_bot.name}'
                                                            f'?start={message.from_user.id}'), reply_markup=markup)
    else:
        await message.answer(texts['free_vip'].format(f'https://t.me/{bot["config"].tg_bot.name}'
                                                      f'?start={message.from_user.id}'))


async def premium_controller(bot, delay):
    decor = bot['decor']
    texts = decor.texts
    data = bot['db']
    buttons = decor.buttons

    while True:
        try:
            cur_time = datetime.datetime.now()
            premium_users = await data.get_premium_users()

            for i in premium_users:
                profile = await data.get_user_anonchat_profile(i)

                if profile['premium']:
                    if profile.get('vip_days', False) == 'forever' or profile.get('vip_hours', False) == 'forever':
                        continue
                    if profile['vip_date']:
                        if not (profile['vip_date'] + datetime.timedelta(days=profile['vip_days'])) < cur_time:
                            continue
                    if profile.get('vip_hours', False):
                        if not (profile['vip_date'] + datetime.timedelta(hours=profile['vip_hours'])) < cur_time:
                            continue
                    try:
                        await bot.send_message(i, texts['bell'])
                        await bot.send_message(i, texts['premium_ended'], reply_markup=inline.extend_vip(buttons))
                        await data.edit_premium(profile['user_id'], None)
                    except Exception as e:
                        print(e)

            await asyncio.sleep(delay)
        except Exception as e:
            print(e)


async def extend_vip(call: CallbackQuery, state):
    message = call.message
    bot = message.bot
    message.from_user.id = call['from']['id']

    await vip(message, state)
    await bot.answer_callback_query(call.id)


async def vip_callback(call: CallbackQuery, state):
    message = call.message
    bot = message.bot
    message.from_user.id = call['from']['id']

    detail = call.data.split(':')[1]
    if detail == 'vip':
        await vip(message, state, back_to_search=True)
    elif detail == 'freevip':
        await free_vip(message, back_to_search=True)
    await bot.answer_callback_query(call.id)


async def only_vip(message: Message, call: FSMContext, edit=False, image=False):
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts
    buttons = decor.buttons

    time_mid = time_to_midnight()
    message_text = texts['vip_required'].format(time_mid['hours'], time_mid['minutes'], time_mid['seconds'])
    if edit:
        if image:
            await message.edit_caption(message_text, reply_markup=inline.vip(buttons))
        else:
            await message.edit_text(message_text, reply_markup=inline.vip(buttons))
    else:
        if image:
            await message.answer_photo(image, message_text, reply_markup=inline.vip(buttons))
        else:
            await message.answer(message_text, reply_markup=inline.vip(buttons))


async def gift_vip(message: Message, state: FSMContext):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts
    chat = bot['chat']
    buttons = decor.buttons

    active_chat = await chat.get_active_chat(message.from_user.id)
    if active_chat:
        companion_id = active_chat['user_id']
        await vip(message, state, companion_id=companion_id)


def time_to_midnight():
    datetime_now = datetime.datetime.now()
    midnight = datetime.datetime(day=datetime_now.day, month=datetime_now.month, year=datetime_now.year, hour=0)

    seconds_midnight = (midnight - datetime_now).seconds
    hours_midnight = seconds_midnight // 3600
    minutes_midnight = (seconds_midnight - (hours_midnight * 3600)) // 60
    seconds = seconds_midnight - (hours_midnight * 3600) - (minutes_midnight * 60)
    if len(str(seconds)) == 1:
        seconds = f'0{seconds}'
    if len(str(minutes_midnight)) == 1:
        minutes_midnight = f'0{minutes_midnight}'
    return {'hours': hours_midnight, 'minutes': minutes_midnight, 'seconds': seconds}


def register_vip(dp: Dispatcher):
    dp.register_callback_query_handler(buy_vip, text_contains='buy_vip:')
    dp.register_callback_query_handler(extend_vip, text_contains='extend_vip')
    dp.register_callback_query_handler(vip_callback, text_contains='vip:')

    dp.register_message_handler(vip, commands=["vip"], state="*")
    dp.register_message_handler(free_vip, commands=["freevip"], state="*")
    dp.register_message_handler(gift_vip, commands=["gift"], state="*")
