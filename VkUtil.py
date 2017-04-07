import time

import postgresql
import vk_api


class VkUtil:
    def __init__(self, user_id):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.token = db.query(
                    "select token from accounts where "
                    "account_type = 'vk' and user_id=" + str(user_id))[0][0]
                message_ids = db.query(
                    '''WITH stream_ids AS
                            (SELECT stream_id
                            FROM streams
                            JOIN accounts USING (account_id)
                            WHERE token = \'''' + self.token + "') " +
                    '''SELECT original_id
                        FROM stream_ids
                        NATURAL JOIN messages
                        ORDER BY original_id DESC;'''
                )
                print(message_ids)
                if message_ids:
                    self.first_message_id = message_ids[0][0]
                else:
                    self.first_message_id = 0
        except Exception as e:
            print(e)
            return
        vk_session = vk_api.VkApi(token=self.token)
        vk_session.auth()
        self.vk = vk_session.get_api()

    def get_new_messages_raw(self):
        """
        :return: all messages with id > self.last_message_id as a list of dicts
        """
        messages = []
        last_message_id = max(
            self.vk.messages.get(count=1)['items'][0]['id'],
            self.vk.messages.get(count=1, out=1)['items'][0]['id']
        )
        while True:
            try:
                new_messages = self.vk.messages.getById(
                    message_ids=",".join(
                        [str(self.first_message_id + i + 1) for i in
                         range(100)]))
            except vk_api.exceptions.ApiError as e:
                if e.code == 6:  # error occurs while sending too many requests
                    time.sleep(1)
                    continue
                else:
                    return []  # handling other errors is senseless
            messages += new_messages['items']
            print(len(messages))
            self.first_message_id += 100
            if self.first_message_id >= last_message_id:
                self.first_message_id = messages[-1]['id']
                break
        return messages

    def send_message(self, user_id, message_text):
        self.vk.messages.send(user_id=user_id, message=message_text)

    def get_user(self, user_id=None, cache={}):
        if user_id in cache:
            return cache[user_id]
        try:
            if user_id is not None:
                res = self.vk.users.get(user_ids=[user_id])[0]
            else:
                res = self.vk.users.get()[0]
            cache[user_id] = res['first_name'] + ' ' + res['last_name']
            return cache[user_id]
        except Exception as e:
            return ''


vk_instance = VkUtil(62827234)
