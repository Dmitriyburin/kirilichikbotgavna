import datetime

import aioredis
import asyncio


class AnonymChat:
    def __init__(self):
        self.r = aioredis.from_url("redis://localhost")

    async def add_to_search(self, user_id, gender, age, companion_gender=None, companion_age=None):
        search = await self.get_search(user_id)
        if search:
            return False

        await self.r.sadd('search',
                          str({'user_id': user_id, 'gender': gender, 'age': age,
                               'companion_gender': companion_gender,
                               'companion_age': companion_age,
                               'dialog_started': 0}))

    async def get_suitable_companion(self, user_id, gender, age, companion_gender=None, companion_age=None):
        elements = list(await self.r.smembers('search'))
        for i in elements[::-1]:
            companion = eval(i.decode('utf-8'))
            if companion['user_id'] == user_id:
                continue

            # проверка на пол
            if not (companion_gender is None or (companion_gender and companion['gender'] == companion_gender)):
                continue
            if not (companion['companion_gender'] is None or (
                    companion['companion_gender'] and companion['companion_gender'] == gender)):
                continue

            # проверка на возраст
            if not (companion_age is None or (companion_age and companion_age == '18+' and companion['age'] >= 18)
                    or (companion_age and companion_age == '18-' and companion['age'] < 18)):
                continue
            if not (companion['companion_age'] is None
                    or (companion['companion_age'] and companion['companion_age'] == '18+' and age >= 18)
                    or (companion['companion_age'] and companion['companion_age'] == '18-' and age < 18)):
                continue

            await self.remove_from_search(companion['user_id'])
            return companion
        return False

    async def get_active_chat(self, user_id):
        chat = await self.r.get(str(user_id))
        if chat:
            return eval(chat.decode('utf-8'))
        return False

    async def get_search(self, user_id):
        elements = list(await self.r.smembers('search'))
        for i in elements[::-1]:
            user = eval(i.decode('utf-8'))
            if user['user_id'] == user_id:
                return user
        return False

    async def remove_from_search(self, user_id):
        user = await self.get_search(user_id)
        await self.r.srem('search', str(user))

    async def chat_found(self, user_id, companion):
        curr_time = datetime.datetime.now()
        await self.r.set(str(user_id), str({'user_id': companion, 'dialog_started': curr_time}))
        await self.r.set(str(companion), str({'user_id': user_id, 'dialog_started': curr_time}))

    async def stop_chat(self, user_id, companion_id):
        user = await self.get_active_chat(user_id)
        companion = await self.get_active_chat(companion_id)

        await self.r.delete(str(user_id))
        await self.r.delete(str(companion_id))
        return datetime.datetime.now() - user['dialog_started']

    async def get_active_anonchat_users(self):
        result = []

        for i in await self.r.smembers('search'):
            result.append(eval(i.decode('utf-8')))

        return result

    async def get_anonchat_online(self):
        users_online_ids = []

        async for i in self.r.scan_iter("*"):
            if i.decode('utf-8') != 'search':
                users_online_ids.append(i.decode('utf-8').split(':')[1])

        return users_online_ids


async def main():
    chat = AnonymChat()
    companion = await chat.get_suitable_companion(companion_gender='female')
    if companion:
        await chat.chat_found(123, companion['user_id'], 42341)
        print('user: 123 ', 'user2: ', companion['user_id'])
    else:
        await chat.add_to_search(user_id=125, companion_gender=143, age=12, gender='female')
        print('searching...')


if __name__ == '__main__':
    asyncio.run(main())
