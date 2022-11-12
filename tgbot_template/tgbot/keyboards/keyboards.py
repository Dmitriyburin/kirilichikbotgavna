from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, ForceReply
import time
import asyncstdlib


def return_to_dialog(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['accept'], callback_data='return_dialog:' + str(user_id)))
    return markup


def return_dialog_try_again(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['try_again'],
                                    callback_data='return_dialog_try_again:' + str(user_id) + ':' + str(time.time())))
    return markup


def enter_age():
    return ForceReply(input_field_placeholder=btns['your_age'])


def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text=btns['menu']))
    return markup


def share_bot():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['bot_channel'], url=bot_channel))
    markup.add(InlineKeyboardButton(text=btns['share'], switch_inline_query=texts['share']))
    return None


def share_anon():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['share'], url=share_mobile))
    return markup


def send_another(ref):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['send_another'], callback_data='send:' + str(ref)))
    return markup


def answer(ref):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['answer'], callback_data='send:' + str(ref)))
    return markup


def top_ref():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['top_ref'], callback_data='top_ref'))
    return markup


def main(btns, premium=None, return_dialog=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text=btns['find_dialog2']))
    markup.add(KeyboardButton(text=btns['vip_search']), KeyboardButton(text=btns['horny_chat']))

    if not premium:
        # markup.add(KeyboardButton(text=btns['premium_search']))
        # markup.add(KeyboardButton(text=btns['mystats2']), KeyboardButton(text=btns['horny_chat']))
        markup.add(KeyboardButton(text=btns['mystats2']), KeyboardButton(text=btns['premium2']))
    else:
        # markup.add(KeyboardButton(text=btns['search_by_gender2']), KeyboardButton(text=btns['horny_chat']))
        if not return_dialog:
            markup.add(KeyboardButton(text=btns['mystats2']))  # , KeyboardButton(text=btns['begin_receive_messages']))
        else:
            markup.add(KeyboardButton(text=btns['mystats2']), KeyboardButton(text=btns['return_dialog']))
    return markup


def dialog_stopped(premium, gender):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text=btns['find_dialog2']))
    markup.add(KeyboardButton(text=btns['report']))
    markup.add(KeyboardButton(text=btns['return_dialog']))

    if not premium:
        markup.add(KeyboardButton(text=btns['search_by_gender_for_' + gender]), KeyboardButton(text=btns['horny_chat']))
    else:
        markup.add(KeyboardButton(text=btns['search_by_gender2']), KeyboardButton(text=btns['horny_chat']))

    markup.add(KeyboardButton(text=btns['menu']))
    return markup


def unblock():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['buy_vip2'], callback_data='vip'))
    return markup


def stop_dialog():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text=btns['stop_dialog']))
    return markup


def top_ref_type():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['followings'], callback_data='top_ref_followings'))
    markup.add(InlineKeyboardButton(text=btns['messages'], callback_data='top_ref_messages'))
    markup.add(InlineKeyboardButton(text=btns['back'], callback_data='top_ref_back'))
    return markup


def del_link(name):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(btns['confirm'], callback_data='del_' + name))
    markup.add(InlineKeyboardButton(btns['cancel'], callback_data='cancel'))

    return markup


def cancel_sending():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['cancel_sending'], callback_data='cancel_sending'))
    return markup


def get_link():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['get_link'], callback_data='get_link'))
    return markup


def select_gender():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['male'], callback_data='male'))
    markup.add(InlineKeyboardButton(btns['female'], callback_data='female'))
    return markup


def select_companion_gender():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['male_companion'], callback_data='companion_gender:male'))
    markup.add(InlineKeyboardButton(btns['female_companion'], callback_data='companion_gender:female'))
    return markup


async def sub_sponsors(channels, data, ref=None, remove_ads=True):
    markup = InlineKeyboardMarkup()
    channel_btns = []

    # markup.add(InlineKeyboardButton(text='💰 Деньги за ТикТоки', url='https://t.me/moneytraffictt_bot'))

    async for n, i in asyncstdlib.enumerate(await data.get_channels()):
        if i['channel_id'] in channels:
            channel_btns.append(InlineKeyboardButton(text=btns['sub'] + str(n + 1), url=i['link']))

    while True:
        row = channel_btns[:2]
        markup.add(*row)
        channel_btns = channel_btns[2:]
        if not channel_btns:
            break

    if remove_ads:
        markup.add(InlineKeyboardButton(text=btns['check'], callback_data='check' + (f'?ref={ref}' if ref else '')),
                   InlineKeyboardButton(text=btns['remove_ads'], callback_data='vip'))
    else:
        markup.add(InlineKeyboardButton(text=btns['check'], callback_data='check' + (f'?ref={ref}' if ref else '')))

    return markup


def remove_ads():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['remove_ads'], callback_data='vip'))
    return markup


def zaliv():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['show_messages'], callback_data='show_messages'))
    return markup


def premium_prices():
    markup = InlineKeyboardMarkup()

    for i in prices:
        markup.add(InlineKeyboardButton(text=i['button'].format(i['price']),
                                        callback_data='buy_premium:' + str(i['days']) + ':' + str(i['price'])))

    # markup.add(InlineKeyboardButton(text=btns['back'], callback_data='close'))
    return markup


def premium_discount():
    markup = InlineKeyboardMarkup()
    for i in prices:
        markup.add(InlineKeyboardButton(text=i['button'].format(i['discount']),
                                        callback_data='buy_premium:' + str(i['days']) + ':' + str(i['discount'])))
    return markup


def buy_premium():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['buy_vip2'], callback_data='vip'))
    return markup


def profile(premium: bool):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['edit_profile'], callback_data='edit_profile'))

    if not premium:
        markup.add(InlineKeyboardButton(text=btns['buy_vip2'], callback_data='vip'))

    return markup


def extend_vip():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['extend_vip'], callback_data='vip'))
    return markup


def pay_payok(payok_link):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=btns['qiwi'], url=payok_link + '&method=qw'),
               InlineKeyboardButton(text=btns['card'], url=payok_link + '&method=cd'))
    markup.add(InlineKeyboardButton(text=btns['yoomoney'], url=payok_link + '&method=ya'),
               InlineKeyboardButton(text=btns['other'], url=payok_link))

    markup.add(InlineKeyboardButton(text=btns['back'], callback_data='vip'))
    return markup


def pay_anypay(anypay_link):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=btns['qiwi'], url=anypay_link + '&method=qiwi'),
               InlineKeyboardButton(text=btns['card'], url=anypay_link + '&method=card'))
    markup.add(InlineKeyboardButton(text=btns['crypto'], url=anypay_link),
               InlineKeyboardButton(text=btns['other'], url=anypay_link))

    markup.add(InlineKeyboardButton(text=btns['back'], callback_data='vip'))
    return markup


def pay_minute(payok_link):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['minute_discount'].format(minute_discount_price), url=payok_link))
    return markup


def promo():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=btns['promo'], url='https://t.me/CallBangBot'))
    markup.add(InlineKeyboardButton(text=btns['remove_ads'], callback_data='vip'))
    return markup


def support():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=btns['write'], url=support_url))
    markup.add(InlineKeyboardButton(text=btns['back'], callback_data='close'))
    return markup


def dialog_ended(premium, gender):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=btns['start_search'], callback_data='search'))
    if premium:
        markup.add(InlineKeyboardButton(text=btns['start_search_for_' + gender],
                                        callback_data='male_companion' if gender == 'female' else 'female_companion'))
    else:
        markup.add(InlineKeyboardButton(text=btns['start_search_for_' + gender], callback_data='vip'))

    markup.add(InlineKeyboardButton(text=btns['menu'], callback_data='menu'))
    return markup


def moderation(id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['ban'], callback_data='ban:' + str(id)))
    markup.add(InlineKeyboardButton(text=btns['ignore'], callback_data='ignore:' + str(id)))
    return markup


def unban_admin(id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['unban'], callback_data='unban_admin:' + str(id)))
    return markup


def unban():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=btns['unban'], callback_data='unban'))
    return markup


def paymethod(methood):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=methood, callback_data='paymethod'))
    return markup
