import datetime

from Records.Record import Record
from VkUtil import VkUtil

REPLY = 0
POSTPONE = 1


class VkMessage(Record):
    def __init__(self, raw_msg, account_id):
        if raw_msg is None:
            return
        self.record_type = 'vk_message'
        self.account_id = account_id
        self.seen = False

        self.vk = VkUtil(account_id)

        self.message_id = raw_msg['id']
        if 'chat_id' in raw_msg:
            self.chat_id = 2 * 10 ** 9 + raw_msg['chat_id']
        else:
            self.chat_id = raw_msg['user_id']
        self.author_id = self.vk.get_own_id() if raw_msg['out'] \
            else raw_msg['user_id']
        self.text = raw_msg['body']
        self.date = datetime.datetime.fromtimestamp(raw_msg['date'])
        self.save_to_database()  # sets record_id

    def after_load(self):
        self.vk = VkUtil(self.account_id)

    def send(self, output_messages_queue):
        inline_keyboard = [
            [('Reply', None, '{0}#{1}'.format(self.record_id, REPLY))],
            [('Postpone', None, '{0}#{1}'.format(self.record_id, POSTPONE))],
            [('Open original...', 'vk.com/im?sel={0}'.format(self.chat_id),
              None)]
        ]
        output_messages_queue.append({'text': self.to_output_view(),
                                      'inline_keyboard': inline_keyboard})
        self.set_seen_state(True)

    def to_output_view(self):
        res = '<b>{0}</b>\n{1}\n<i>{2}</i>'.format(self.author_id, self.text,
                                                   self.date)
        return res

    def respond(self, incoming_messages_queue, output_messages_queue,
                query_type):
        if query_type == REPLY:
            output_messages_queue.append(
                {'text': 'Replying to ' + self.vk.get_user_name(
                    self.author_id)})
            output_messages_queue.append(
                {'text': 'Please, type your message:'})
            while True:
                update = incoming_messages_queue.pop()
                if update.message is not None:
                    self.vk.send_message(
                        user_id=self.chat_id,
                        message_text=update.message.text)
                    output_messages_queue.append(
                        {'text': 'Answer sent!'})
                    return
        elif query_type == POSTPONE:
            self.set_seen_state(False)
            output_messages_queue.append(
                {'text': 'Postponed'})
