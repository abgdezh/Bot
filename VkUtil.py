import time

import postgresql
import vk_api

from Message import Message


class VkUtil:
    def __init__(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.token = db.query("select token from accounts where "
                                      "account_type = 'vk'")
        except:
            self.token = ''
        self.last_message_id = 10100
        vk_session = vk_api.VkApi(token=self.token)
        vk_session.auth()
        self.vk = vk_session.get_api()

    def get_new_messages_raw(self):
        """
        :return: all messages with id > self.last_message_id as a list of dicts
        """
        messages = []
        offset = 0
        while True:
            try:
                new_messages = self.vk.messages.get(
                    last_message_id=self.last_message_id, offset=offset,
                    count=200)
            except vk_api.exceptions.ApiError as e:
                if e.code == 6:  # error occurs while sending too many requests
                    time.sleep(1)
                    continue
                else:
                    return []  # handling other errors is senseless
            messages += new_messages['items']
            if new_messages['items'] and new_messages['items'][-1][
                'id'] > self.last_message_id:
                offset += 200
            else:
                break
        self.last_message_id = messages[0]['id']
        return messages

    def update_messages(self):
        for msg in self.get_new_messages_raw():
            self.parse_message(msg)

    def parse_message(self, msg_dict):
        msg = Message()
        msg.text = msg_dict['body']

    def send_message(self, message):
        # TODO sends Message
        pass
