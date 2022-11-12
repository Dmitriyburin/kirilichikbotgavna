from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup, ForceReply


def kb_registration():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Зарегистрироваться', callback_data='registration'))
    return markup


def select_gender(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['male'], callback_data='registration:male'))
    markup.add(InlineKeyboardButton(btns['female'], callback_data='registration:female'))
    return markup


def select_companion_gender(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['male_companion'], callback_data='companion_details:male'))
    markup.add(InlineKeyboardButton(btns['female_companion'], callback_data='companion_details:female'))
    return markup


def select_companion_age(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['companion_age_18+'], callback_data='companion_details:18+'))
    markup.add(InlineKeyboardButton(btns['companion_age_18-'], callback_data='companion_details:18-'))
    return markup


def vip_search(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['search_by_age'], callback_data='search_by:age'))
    markup.add(InlineKeyboardButton(btns['search_by_gender'], callback_data='search_by:gender'))
    return markup


def set_profile(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Изменить пол', callback_data='set_profile:gender'))
    markup.add(InlineKeyboardButton('Изменить возраст', callback_data='set_profile:age'))
    markup.add(InlineKeyboardButton('⬅️Назад', callback_data='back_to:profile'))
    return markup


def set_gender(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['male'], callback_data='set_gender:male'))
    markup.add(InlineKeyboardButton(btns['female'], callback_data='set_gender:female'))
    return markup


def estimate_companion(btns, is_admin=False):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['like'], callback_data='estimate_companion:like'),
               InlineKeyboardButton(btns['dislike'], callback_data='estimate_companion:dislike'))

    if is_admin:
        markup.add(InlineKeyboardButton('Забанить', callback_data='estimate_companion:report'))
    else:
        markup.add(InlineKeyboardButton(btns['report'], callback_data='estimate_companion:report'))
    return markup


def estimate_companion_short_only_report(btns, is_admin=False):
    markup = InlineKeyboardMarkup()
    if is_admin:
        markup.add(InlineKeyboardButton('Забанить', callback_data='estimate_companion:report'))
    else:
        markup.add(InlineKeyboardButton(btns['report'], callback_data='estimate_companion:report'))
    return markup


def estimate_companion_short_only_react(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['like'], callback_data='estimate_companion:like'),
               InlineKeyboardButton(btns['dislike'], callback_data='estimate_companion:dislike'))
    return markup


def vip_privileges(prices):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(prices[1]['button'].format(prices[1]['price']),
                                    callback_data=f"buy_vip:{prices[1]['days']}"))
    markup.add(InlineKeyboardButton(prices[7]['button'].format(prices[7]['price']),
                                    callback_data=f"buy_vip:{prices[7]['days']}"))
    markup.add(InlineKeyboardButton(prices[30]['button'].format(prices[30]['price']),
                                    callback_data=f"buy_vip:{prices[30]['days']}"))
    markup.add(InlineKeyboardButton(prices[365]['button'].format(prices[365]['price']),
                                    callback_data=f"buy_vip:{prices[365]['days']}"))
    return markup


def profile(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['buy_vip'], callback_data='print_profile:buy_vip'))
    markup.add(InlineKeyboardButton(btns['about_me'], callback_data='print_profile:about_me'),
               InlineKeyboardButton(btns['mystats'], callback_data='print_profile:mystats'))
    return markup


def back(btns, callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('⬅️Назад', callback_data=callback_data))
    return markup


def back_button(callback_data):
    return InlineKeyboardButton('⬅️Назад', callback_data=callback_data)


def cancel(btns, callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Отмена', callback_data=callback_data))
    return markup


def delete_mailing(btns, message_id, ):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Удалить', callback_data=f'cancel:mailing2-{message_id}'))
    return markup


def generate_captcha():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Новая captcha', callback_data='generate_captcha'))
    return markup


def required_sub(btns, channels):
    markup = InlineKeyboardMarkup(row_width=2)
    for index, channel in enumerate(channels):
        markup.add(InlineKeyboardButton(f'Канал #{index + 1}', url=channel))
    markup.add(InlineKeyboardButton('Проверить подписку', callback_data='check_sub_call'))
    return markup


def ban_user(btns, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['ban'], callback_data=f'ban_user:{user_id}'))
    return markup


def extend_vip(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['extend_vip'], callback_data=f'extend_vip'))
    return markup
