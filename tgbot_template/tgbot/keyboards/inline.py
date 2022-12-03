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
    markup.add(InlineKeyboardButton('Сбросить дизлайки', callback_data='set_profile:reset_react'))
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


def vip_privileges(prices, urls):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(prices[1]['button'].format(prices[1]['price']), url=urls[1]))
    markup.add(InlineKeyboardButton(prices[7]['button'].format(prices[7]['price']), url=urls[7]))
    markup.add(InlineKeyboardButton(prices[30]['button'].format(prices[30]['price']), url=urls[30]))
    markup.add(
        InlineKeyboardButton(prices['forever']['button'].format(prices['forever']['price']), url=urls['forever']))
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
    markup.add(InlineKeyboardButton('🔎 Проверить подписку', callback_data='check_sub_call:channel'))
    markup.add(InlineKeyboardButton('🚫 Убрать рекламу', callback_data='check_sub_call:vip'))
    return markup


def ban_user(btns, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['ban'], callback_data=f'ban_user:{user_id}'))
    return markup


def extend_vip(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['extend_vip'], callback_data=f'extend_vip'))
    return markup


def vip(btns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🏆 Приобрести VIP Status', callback_data=f'vip:vip'))
    markup.add(InlineKeyboardButton('💵 Получить ВИП бесплатно', callback_data=f'vip:freevip'))
    return markup


def reset_dislikes(btns, url):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(btns['reset_dislikes_buy'], url=url))
    return markup


def yes_or_not(callback):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(InlineKeyboardButton('Да', callback_data=f'{callback}:yes'),
               InlineKeyboardButton('Нет', callback_data=f'{callback}:no'))
    return markup


def delete(callback):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Удалить', callback_data=f'delete:{callback}'))
    return markup


def aa():
    return InlineKeyboardMarkup(
        inline_keyboard=[[{"text": "Возможности Notepost", "url": "https://t.me/notepostbot?start=info"}]])


if __name__ == '__main__':
    print(aa().to_python())
