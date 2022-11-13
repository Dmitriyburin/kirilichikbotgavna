import asyncio
import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from tgbot.keyboards import inline
from tgbot.handlers.payment_system import buy_process

from tgbot_template.tgbot.misc import anypay


async def vip(message: Message, state: FSMContext, back_to_profile=None):
    bot = message.bot
    decor = bot['decor']
    data = bot['db']
    texts = decor.texts
    buttons = decor.buttons
    prices: dict = decor.prices

    user = await data.get_user_anonchat_profile(message.from_user.id)
    if user['premium']:

        if back_to_profile:
            markup = inline.back(buttons, 'back_to:profile')
        else:
            markup = None

        vip_days = user['vip_days'] - (datetime.datetime.now() - user['vip_date']).days
        await message.edit_caption(f'У вас уже есть подписка, она заканчивается через {vip_days} дней',
                                   reply_markup=markup)

        return

    urls = {}
    for key, value in prices.items():
        price = value['price']
        anypay_secret, anypay_shop = bot['config'].anypay.secret, bot['config'].anypay.shop
        payment_id = await data.get_anypay_payment_id()
        sign, secret = anypay.gen_hash(price, payment_id, anypay_secret=anypay_secret, anypay_shop=anypay_shop)
        url = anypay.gen_url(price, payment_id, 'топ', sign, anypay_shop=anypay_shop)
        urls[key] = url

        await data.add_anypay_payment_no_discount(message.from_user.id, sign, secret, payment_id, days=key, price=price)
    markup = inline.vip_privileges(prices, urls)
    if back_to_profile:
        markup.add(inline.back_button('back_to:profile'))
        await message.edit_caption(texts['vip_privileges'],
                                   reply_markup=markup)
    else:
        await message.answer(texts['vip_privileges'], reply_markup=markup)


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


async def free_vip(message: Message):
    bot = message.bot
    decor = bot['decor']
    texts = decor.texts

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

                if profile['premium'] and (
                        profile['vip_date'] + datetime.timedelta(days=profile['vip_days'])) < cur_time:
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


def register_vip(dp: Dispatcher):
    dp.register_callback_query_handler(buy_vip, text_contains='buy_vip:')
    dp.register_callback_query_handler(extend_vip, text_contains='extend_vip')
    dp.register_message_handler(vip, commands=['vip'])
    dp.register_message_handler(free_vip, commands=["freevip"], state='*')
