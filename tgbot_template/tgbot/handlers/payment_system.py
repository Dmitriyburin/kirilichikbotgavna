from aiogram import Dispatcher
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ContentTypes
from aiogram.dispatcher import FSMContext

PRICES = [
    LabeledPrice(label='Ноутбук', amount=1000),
]


async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    bot = pre_checkout_query.bot
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    success_payment_message = f'Вы успешно просрали свои {pre_checkout_query.total_amount // 100} рублей и ' \
                              f'получили VIP status на {pre_checkout_query.invoice_payload} дней'
    bot[pre_checkout_query.from_user.id] = {'success_payment_message': success_payment_message,
                                            'payment_days': pre_checkout_query.invoice_payload}


async def buy_process(message: Message, days, markup):
    bot = message.bot
    decor = bot['decor']
    config = bot['config']
    prices = decor.prices

    price = [LabeledPrice(label=f'VIP', amount=(prices[days]['price']) * 100)]
    await message.delete()
    await bot.send_invoice(message.chat.id,
                           title=f'VIP status на дней: {days}',
                           provider_token=config.payment_token,
                           currency='rub',
                           prices=price,
                           start_parameter='example',
                           payload=days,
                           description='лютый топ описание')


async def successful_payment(message: Message):
    bot = message.bot
    data = bot['db']
    decor = bot['decor']
    texts = decor.texts

    await data.edit_premium(message.from_user.id, True, bot[message.from_user.id]['payment_days'])

    success_payment = bot[message.from_user.id]['success_payment_message']
    await message.answer(success_payment)


def register_payment(dp: Dispatcher):
    dp.register_pre_checkout_query_handler(checkout_process, lambda q: True)
    dp.register_message_handler(successful_payment, content_types=ContentTypes.SUCCESSFUL_PAYMENT)
