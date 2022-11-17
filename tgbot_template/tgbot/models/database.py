import datetime
import random
import time

from motor import motor_asyncio
import asyncio

from pymongo import DeleteOne


class Database:
    def __init__(self, connection_mongodb):
        self.cluster = motor_asyncio.AsyncIOMotorClient(connection_mongodb)
        self.db = self.cluster.admin
        self.users = self.db.users
        self.settings = self.db.settings
        self.ref_links = self.db.ref_links
        self.user_ref_links = self.db.user_ref_links
        self.messages = self.db.messages
        self.anonchat_users = self.db.anonchat_users
        self.channels = self.db.channels
        self.mailing = self.db.mailing
        self.mailing_users = self.db.mailing_users
        self.banned_users = self.db.banned_users
        self.payments = self.db.payments
        self.stats = self.db.stats

    async def add_user(self, user_id, ref, lang='ru', ref_commercial=False):
        if ref_commercial:
            await self.ref_links.update_one({'link': ref_commercial}, {'$inc': {'users': 1, 'transitions': 1}})

        await self.stats.update_one({'stat': 'all'}, {'$inc': {'users': 1}}, upsert=False)
        await self.users.insert_one({'user_id': user_id, 'ref': ref, 'lang': lang})

    async def get_user(self, user_id):
        return await self.users.find_one({'user_id': user_id})

    async def get_users(self):
        return self.users.find({})

    async def users_count(self):
        return await self.users.count_documents({})

    async def get_user_anonchat_profile(self, user_id):
        return await self.anonchat_users.find_one({'user_id': user_id})

    async def add_user_anonchat_profile(self, user_id, gender, age, ref, ref_commercial=None):

        await self.anonchat_users.insert_one(
            {'user_id': user_id, 'gender': gender, 'age': age, 'dialogs': 0, 'messages': 0, 'likes': 0,
             'dislikes': 0, 'reports_count': 0, 'last_companion_id': None, 'time': 0, 'vip_days': None,
             'vip_hours':None,
             'vip_date': None, 'last_dialogs': [0], 'last_companion_gender': None, 'last_companion_age': None,
             'date_registration': datetime.datetime.now(), 'premium': None,
             'saw_discount_minute': False, 'ref': ref, 'total_donated': 0})

    async def edit_user_anonchat_profile(self, user_id, gender, age, ref_commercial=None, first=None):
        if ref_commercial and first:
            await self.ref_links.update_one({'link': ref_commercial}, {'$inc': {'sum_average_age': age}}, upsert=False)
            if gender == 'male':
                await self.ref_links.update_one({'link': ref_commercial}, {'$inc': {'male': 1}}, upsert=False)

            elif gender == 'female':
                await self.ref_links.update_one({'link': ref_commercial},
                                                {'$inc': {'female': 1}}, upsert=False)

            await self.ref_links.update_one({'link': ref_commercial}, {'$inc': {'anonchat_users': 1}}, upsert=False)

        if first:
            await self.stats.update_one({'stat': 'all'}, {'$inc': {'sum_average_age': age}}, upsert=False)
            await self.stats.update_one({'stat': 'all'}, {'$inc': {'anonchat_users': 1}}, upsert=False)

        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'gender': gender, 'age': int(age)}},
                                             upsert=False)

    async def increment_dialogs_count(self, user_id, dialogs):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'dialogs': dialogs}},
                                             upsert=False)

    async def increment_messages_count(self, user_id, messages):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'messages': messages}},
                                             upsert=False)
        await self.update_messages()

    async def increment_likes(self, user_id, likes):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'likes': likes}},
                                             upsert=False)

    async def increment_dislikes(self, user_id, dislikes):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'dislikes': dislikes}},
                                             upsert=False)

    async def increment_reports_count(self, user_id, reports_count):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'reports_count': reports_count}},
                                             upsert=False)

    async def increment_subs_ref_commercial(self, link, count_subs):
        await self.ref_links.update_one({'link': link}, {'$inc': {'subs': count_subs}})

    async def reset_reports_count(self):
        users = await self.get_users()
        async for user in users:
            await self.anonchat_users.update_one({'user_id': user['user_id']},
                                                 {'$set': {'reports_count': 0}},
                                                 upsert=False)

    async def set_last_companion_id(self, user_id, companion_id):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'last_companion_id': companion_id}},
                                             upsert=False)

    async def edit_premium(self, user_id, premium, days=None, hours=None):
        if premium:
            await self.anonchat_users.update_one({'user_id': user_id},
                                                 {'$set': {'premium': premium, 'vip_days': int(days),
                                                            'vip_hours': hours,
                                                           'vip_date': datetime.datetime.now()}}, upsert=False)
        else:
            await self.anonchat_users.update_one({'user_id': user_id},
                                                 {'$set': {'premium': premium, 'vip_days': None,
                                                           'vip_date': None}}, upsert=False)

    async def edit_total_time(self, user_id, time):
        user = await self.get_user_anonchat_profile(user_id)
        await self.anonchat_users.update_one({'user_id': user_id}, {'$set': {'time': user['time'] + time}},
                                             upsert=False)

    async def get_premium_users(self):
        return [i['user_id'] async for i in self.anonchat_users.find({'premium': {'$ne': None}})]

    async def get_premium_users_count(self):
        return await self.anonchat_users.count_documents({'premium': {'$ne': None}})

    async def get_mailing(self, message_id):
        return await self.mailing.find_one({'message_id': message_id})

    async def get_mailings(self):
        return [i async for i in self.mailing.find({})]

    async def get_mailing_users(self):
        users = [user['user_id'] async for user in self.mailing_users.find({}).limit(29)]

        if users:
            requests = [DeleteOne({'user_id': i}) for i in users]
            await self.mailing_users.bulk_write(requests)

        return users

    async def update_users_mailing(self):
        await self.mailing_users.delete_many({})
        mailing_ignore = await self.get_premium_users()
        mailing_users = [{'user_id': user['user_id']} async for user in await self.get_users() if
                         user['user_id'] not in mailing_ignore]
        await self.mailing_users.insert_many(mailing_users)

    async def add_mailing(self, chat_id, message_id, markup, details, date):
        # await self.mailing.delete_many({})
        # await self.mailing_users.delete_many({})

        # mailing_users2 = []
        # async for user in await self.get_users():
        #     if user['user_id'] not in mailing_ignore:
        #         for _ in range(1000):
        #             mailing_users2.append({'user_id': user['user_id']})

        await self.mailing.insert_one(
            {'message_id': message_id, 'chat_id': chat_id, 'markup': markup, 'users_count': None,
             'details': details, 'date': date, 'sent': 0, 'not_sent': 0, 'is_active': False})

    async def reset_mailing_date(self, message_id):
        await self.mailing.update_one({'message_id': message_id}, {'$set': {'date': None}}, upsert=False)

    async def edit_mailing_progress(self, message_id, sent=0, not_sent=0):
        await self.mailing.update_one({'message_id': message_id}, {'$inc': {'sent': sent, 'not_sent': not_sent}},
                                      upsert=False)

    async def del_mailing(self, message_id):
        await self.mailing.delete_many({'message_id': message_id})
        await self.update_users_mailing()

    async def set_active_mailing(self, message_id, is_active):
        await self.update_users_mailing()
        mailing_users_count = await self.mailing_users.count_documents({})

        await self.mailing.update_one({'message_id': message_id},
                                      {'$set': {'is_active': is_active, 'users_count': mailing_users_count}},
                                      upsert=False)

    async def add_channel(self, channel_id, link):
        await self.channels.insert_one({'channel_id': channel_id, 'link': link})

    async def del_channel(self, link):
        await self.channels.delete_one({'link': link})

    async def get_channels(self):
        return self.channels.find({})

    async def get_channel(self, link):
        return await self.channels.find_one({'link': link})

    async def update_messages(self):
        await self.messages.update_one({'type': 'total'}, {'$inc': {'messages': 1}}, upsert=False)
        await self.messages.update_one({'type': 'today'}, {'$inc': {'messages': 1}}, upsert=False)

    async def get_messages_stats(self):
        return {'total': (await self.messages.find_one({'type': 'total'}))['messages'],
                'today': (await self.messages.find_one({'type': 'today'}))['messages']}

    async def add_messages(self):
        self.messages.insert_one({'type': 'total', 'messages': 0})
        self.messages.insert_one({'type': 'today', 'messages': 0})

    async def del_today_messages(self):
        await self.messages.update_one({'type': 'today'}, {'$set': {'messages': 0}}, upsert=False)

    async def get_anonchat_users_stats(self):
        return await self.anonchat_users.count_documents(
            {'gender': {'$ne': None}, 'age': {'$ne': None}}), await self.anonchat_users.count_documents(
            {'gender': 'male', 'age': {'$ne': None}}), await self.anonchat_users.count_documents(
            {'gender': 'female', 'age': {'$ne': None}})

    async def ban_user(self, user_id, hours=None, time_mute=None):
        banned_users = await self.get_ban_users()
        banned_users_ids = [i['user_id'] for i in banned_users]
        if user_id not in banned_users_ids:
            if hours and time_mute:
                self.banned_users.insert_one({'user_id': int(user_id), 'hours': hours, 'time_mute': time_mute})
            else:
                self.banned_users.insert_one({'user_id': int(user_id)})

    async def unban_user(self, user_id):
        await self.banned_users.delete_one({'user_id': user_id})

    async def get_ban_users(self):
        return [i async for i in self.banned_users.find({})]

    async def get_ban_user(self, user_id):
        return self.banned_users.find_one({'user_id': user_id})

    async def add_message_to_last_dialog(self, user_id, message_id):
        user = await self.get_user_anonchat_profile(user_id)
        last_dialog_messages = user['last_dialogs'][-1]
        last_dialog_messages.append(message_id)
        last_dialogs_without_current = user['last_dialogs'][1:-1]
        await self.anonchat_users.update_one({'user_id': user_id},
                                             {'$set': {
                                                 'last_dialogs': [user['reports_count'], *last_dialogs_without_current,
                                                                  last_dialog_messages]}},
                                             upsert=False)

    async def add_new_last_dialog(self, user_id):
        user = await self.get_user_anonchat_profile(user_id)
        last_dialogs = user['last_dialogs']
        if len(last_dialogs) >= 6:
            last_dialogs.pop(1)
        last_dialogs.append([])
        await self.anonchat_users.update_one({'user_id': user_id},
                                             {'$set': {'last_dialogs': last_dialogs}},
                                             upsert=False)

    async def get_last_dialogs(self, user_id):
        user = await self.get_user_anonchat_profile(user_id)
        last_dialogs = user['last_dialogs']
        return [i for i in last_dialogs[1:]]

    async def add_ref(self, link, price):
        await self.ref_links.insert_one({'link': link, 'users': 0, 'anonchat_users': 0, 'male': 0, 'female': 0,
            'sum_average_age': 0, 'transitions': 0, 'price': price,
                                         'donaters': 0, 'all_price': 0})

    async def increment_ref_transition(self, link):
        await self.ref_links.update_one({'link': link},
                                        {'$inc': {'transitions': 1}},
                                        upsert=False)

    async def add_ref_donater(self, link, price):
        await self.ref_links.update_one({'link': link},
                                        {'$inc': {'donaters': 1, 'all_price': price}},
                                        upsert=False)

    async def get_refs(self):
        return self.ref_links.find({})

    async def get_ref(self, link):
        return await self.ref_links.find_one({'link': link})

    async def delete_ref(self, link):
        await self.ref_links.delete_one({'link': link})

    async def set_last_companion_age(self, user_id, age):
        await self.anonchat_users.update_one({'user_id': user_id},
                                             {'$set': {'last_companion_age': age}},
                                             upsert=False)

    async def set_last_companion_gender(self, user_id, gender):
        await self.anonchat_users.update_one({'user_id': user_id},
                                             {'$set': {'last_companion_gender': gender}},
                                             upsert=False)

    async def get_anypay_payment_id(self):
        return int(time.time() * 10000)

    async def add_anypay_payment_no_discount(self, user_id, sign, secret, payment_id, days, price):
        await self.payments.insert_one(
            {'type': 'anypay', 'user_id': user_id, 'sign': sign, 'secret': secret, 'payment_id': payment_id,
             'days': days, 'price': price, 'paid': False, 'gived': False, 'discount': None})

    async def get_payment_by_secret(self, secret):
        return await self.payments.find_one({'secret': secret})

    async def edit_paid_status(self, secret):
        await self.payments.update_one({'secret': secret}, {'$set': {'paid': True, 'discount': None}}, upsert=False)

    async def edit_given_status(self, secret):
        await self.payments.update_one({'secret': secret}, {'$set': {'gived': True}}, upsert=False)

    async def get_ungiven_payments(self):
        await self.payments.delete_many({'gived': True, 'paid': True})
        return self.payments.find({'gived': False, 'paid': True})

    async def edit_user_donates(self, user_id, count):
        await self.anonchat_users.update_one({'user_id': user_id}, {'$inc': {'total_donated': count}}, upsert=False)

    async def increment_price_all_stats(self, price):
        await self.stats.update_one({'stat': 'all'}, {'$inc': {'all_price': price}}, upsert=False)

    async def get_stats(self):
        return await self.stats.find_one({'stat': 'all'})
    
    async def ref_stats_online(self, link):
        male = await self.anonchat_users.count_documents(
            {'gender': 'male', 'age': {'$ne': None}, 'ref': link})
        female = await self.anonchat_users.count_documents(
            {'gender': 'female', 'age': {'$ne': None}, 'ref': link})
        all_anonchat_users = await self.anonchat_users.count_documents(
            {'gender': {'$ne': None}, 'age': {'$ne': None}, 'ref': link})
        all_users = await self.users.count_documents(
            {'ref': link}
        )
        return {'male': male, 'female': female, 'all_anonchat_users': all_anonchat_users, 'all_users': all_users}

async def del_today_messages(database):
    await database.del_today_messages()


async def main():
    database = Database('mongodb://localhost:27017')
    ref = await database.get_ref('https://t.me/verymuchsimplebot?start=MjkzNjc5Mw')
    print(ref['users'])


if __name__ == '__main__':
    asyncio.run(main())
