import logging
import typing

from aiogram.dispatcher.filters import BoundFilter


class ModeratorFilter(BoundFilter):
    key = 'is_moderator'

    def __init__(self, is_moderator: typing.Optional[bool] = None):
        self.is_moderator = is_moderator

    async def check(self, obj):
        if self.is_moderator is None:
            return False
        bot_data = obj.bot.get('db')
        moderators_ids = [moder['user_id'] for moder in (await bot_data.get_moderators())]
        return (obj.from_user.id in moderators_ids) == self.is_moderator

