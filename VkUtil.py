import time

import postgresql
import vk_api


class VkUtil:
    def __init__(self, account_id):
        self.account_id = account_id
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.token = db.query(
                    "SELECT token "
                    "FROM accounts "
                    "WHERE account_id = {0}".format(account_id))[0][0]
                message_ids = db.query(
                    'SELECT message_id '
                    'FROM records '
                    'NATURAL JOIN vk_message '
                    'WHERE account_id = {0} '
                    'ORDER BY message_id DESC '
                    'LIMIT 1'.format(account_id)
                )
                if message_ids:
                    self.first_message_id = message_ids[0][0]
                else:
                    self.first_message_id = 0
        except Exception as e:
            print(e)
            return
        vk_session = vk_api.VkApi(token=self.token, api_version='5.63')
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
            self.first_message_id += 100
            if self.first_message_id >= last_message_id:
                if messages:
                    self.first_message_id = messages[-1]['id']
                else:
                    self.first_message_id -= 100
                break
        return messages

    def send_message(self, user_id, message_text):
        self.vk.messages.send(user_id=user_id, message=message_text)

    def get_post(self, wall_id):
        return self.vk.wall.get(owner_id=wall_id, count=1)['items'][0]

    def like_post(self, wall_id, post_id):
        self.vk.likes.add(type='post', owner_id=wall_id, item_id=post_id)

    def share_post(self, wall_id, post_id):
        self.vk.wall.repost(object='wall' + str(wall_id) + '_' + str(post_id))

    def comment_post(self, wall_id, post_id, message):
        self.vk.wall.createComment(owner_id=wall_id, post_id=post_id,
                                   message=message)

    def get_user_name(self, user_id=None, cache={}):
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

    def get_own_id(self):
        try:
            return self.vk.users.get()[0]['id']
        except Exception as e:
            print(e)
            return 0

    def get_group_name(self, group_id, cache={}):
        if group_id in cache:
            return cache[group_id]
        try:
            res = self.vk.groups.getById(group_id=group_id)['response']
            cache[group_id] = res['name']
            return cache[group_id]
        except Exception as e:
            return ''
