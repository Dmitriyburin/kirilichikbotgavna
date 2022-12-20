from aiogram.dispatcher.filters.state import State, StatesGroup


class Profile(StatesGroup):
    gender = State()
    age = State()


class SetAge(StatesGroup):
    age = State()


class Search(StatesGroup):
    search = State()


class GetMailing(StatesGroup):
    mailing = State()
    set_time = State()


class AddChannel(StatesGroup):
    channel = State()
    link = State()


class DeleteChannel(StatesGroup):
    channel = State()


class AddRef(StatesGroup):
    date = State()
    price = State()
    contact = State()


class DeleteRef(StatesGroup):
    ref = State()


class StatsRef(StatesGroup):
    ref = State()


class BanUser(StatesGroup):
    user_id = State()


class UnbanUser(StatesGroup):
    user_id = State()


class AddModerator(StatesGroup):
    user_id = State()


class DeleteModerator(StatesGroup):
    user_id = State()


class AddBlackWord(StatesGroup):
    word = State()


class DeleteBlackWord(StatesGroup):
    word = State()


class AddVip(StatesGroup):
    user_id = State()
    days = State()


class AddAdvertising(StatesGroup):
    message_id = State()
    views = State()
    accept = State()


class RefsMonth(StatesGroup):
    month_callback = State()


class RequiredChannel(StatesGroup):
    required_channel = State()


class ReturnDialog(StatesGroup):
    enter_text = State()


class SpeakToRobot1(StatesGroup):
    step1 = State()
    step2 = State()
    step3 = State()
    step4 = State()


class Captcha(StatesGroup):
    enter_captcha = State()
