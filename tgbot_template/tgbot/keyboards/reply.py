from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup, ForceReply


def main(btns, premium=None, return_dialog=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text=btns['find_dialog2']))
    markup.add(KeyboardButton(text=btns['vip_search']), KeyboardButton(text=btns['horny_chat']))
    markup.add(KeyboardButton(text=btns['mystats2']))
    return markup
