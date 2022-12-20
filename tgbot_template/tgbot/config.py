from dataclasses import dataclass
import yaml
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    test_localhost_string_mongodb: str


@dataclass
class TgBot:
    token: str
    admin_ids: list
    use_redis: bool
    name: str


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Decoration:
    texts: dict
    buttons: dict
    prices: dict
    model_anonym_chat: dict
    mailings_posts: list


@dataclass
class Anypay:
    secret: str
    shop: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    decoration: Decoration
    anypay: Anypay
    payment_token: str
    channel_id_to_send_media: int
    channel_id_to_send_ban: int


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    with open('tgbot/config.yaml', encoding='utf-8') as f:
        conf = yaml.safe_load(f)
        return Config(
            tg_bot=TgBot(
                token=env.str("BOT_TOKEN"),
                admin_ids=list(map(int, env.list("ADMINS"))),
                use_redis=env.bool("USE_REDIS"),
                name=env.str("BOT_NAME")
            ),
            db=DbConfig(
                host=env.str('DB_HOST'),
                password=env.str('DB_PASS'),
                user=env.str('DB_USER'),
                database=env.str('DB_NAME'),
                test_localhost_string_mongodb=env.str('test_localhost_string_mongodb')
            ),
            misc=Miscellaneous(),
            decoration=Decoration(
                texts=conf['texts'],
                buttons=conf['buttons'],
                prices=prices,
                model_anonym_chat=model1,
                mailings_posts=mailings_posts
            ),
            anypay=Anypay(
                secret=anypay_secret,
                shop=anypay_shop
            ),
            payment_token=env.str('PAYMENT_TOKEN'),
            channel_id_to_send_media=env.str('CHANNEL_ID_TO_SEND_MEDIA'),
            channel_id_to_send_ban=env.str('CHANNEL_ID_TO_SEND_BAN')
        )


prices = {
    1: {'days': 1, 'price': 79, 'discount': 49, 'button': '24 часа - {0} ₽', 'description': 'vip_1_day'},
    7: {'days': 7, 'price': 149, 'discount': 99, 'button': '7 дней - {0} ₽', 'description': 'vip_7_day'},
    30: {'days': 30, 'price': 179, 'discount': 129, 'button': 'Месяц - {0} ₽', 'description': 'vip_30_day'},
    'forever': {'days': 'forever', 'price': 499, 'discount': 299, 'button': 'Навсегда - {0} ₽',
                'description': 'vip_forever'},
    'reset_react': {'price': 19, 'description': 'reset_react'},
    'unban': {'price': 79, 'description': 'unban'}
}
anypay_secret = '2e7%b*P3H(7s'
anypay_shop = 9995
support_url = 'https://t.me/AnonimHelperBot'

model1 = {
    '1': '<b>Cейчас будет запущен поиск твоего первого собеседника 😉</b>',
    '2': '<b>🔎 Ищем собеседника..</b>',
    '3': '/stop — закончить диалог\n/vip - получить VIP',
    '4': 'Привет, я девушка, а ты?',
    '5': 'AwACAgQAAxkBDQyc7mKnxJfh9tOYcxTK-gvzC-30KAu8AAIjAwAC7zrVUUg6JR2q3Og5JAQ',
    '6': 'AwACAgQAAxkBDQy-SGKnxecYVXUkpR30BQZ8fxWEMHAUAAJFAwAC9gAB1VEg2J3bvNLyAiQE',
    '7': 'AwACAgQAAxkBDQy-SWKnxeez8A58hIBmF8Mfz1WKeIURAAJeAwACERfUUazPyV9QVhhHJAQ',
    '8': 'AwACAgQAAxkBDQy-SmKnxecstVxCePGtcm91P9YIRi__AAJOAwAC_WvVUStuYS88aof5JAQ',
}

mailings_posts = [
    {'text': 'Рассылка лютая', 'keyboard': None}
]
