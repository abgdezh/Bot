import datetime

from Messages.Message import Message
from Messages.stream_utils import get_original_stream_id, get_stream_id
from VkUtil import vk_instance


class VkMessage(Message):
    def __init__(self, raw_msg=None):
        if raw_msg is None:
            return
        self.original_id = raw_msg['id']
        if 'title' in raw_msg and raw_msg['title'] != ' ... ':
            self.title = raw_msg['title']
        self.text = raw_msg['body']
        if raw_msg['out'] == 0:
            self.author = vk_instance.get_user(raw_msg['user_id'])
        else:
            self.author = vk_instance.get_user()
        if 'chat_id' in raw_msg:
            self.stream_id = get_stream_id('vk-msg',
                                           2 * 10 ** 9 + raw_msg['chat_id'])
        else:
            self.stream_id = get_stream_id('vk-msg', raw_msg['user_id'])
        self.date = datetime.datetime.fromtimestamp(raw_msg['date'])
        self.was_archived = False
        self.save_to_database()  # sets message_id

    def send(self, output_messages_queue):
        inline_keyboard = [
            [('Reply', None, str(self.message_id) + '#0')],
            [('Postpone', None, str(self.message_id) + '#1')],
            [('Open original...', 'vk.com/im?sel=' +
              str(get_original_stream_id(self.message_id)), None)]
        ]
        output_messages_queue.append({'text': self.to_output_view(),
                                      'inline_keyboard': inline_keyboard})
        self.set_archived_state(True)

    def to_output_view(self):
        if 'title' in self.__dir__() and self.title is not None:
            res = '<b>' + self.title + '</b>\n'
        else:
            res = ''
        res += self.text + '\n' + '<b>' + self.author + '</b>\n' + '<i>' + str(
            self.date) + '</i>'
        return res

    def respond(self, incoming_messages_queue, output_messages_queue,
                query_type):
        if query_type == 0:
            output_messages_queue.append(
                {'text': 'Replying to ' + self.author})
            output_messages_queue.append(
                {'text': 'Please, type your message:'})
            while True:
                update = incoming_messages_queue.get_message()
                if update.message:
                    vk_instance.send_message(
                        user_id=get_original_stream_id(self.message_id),
                        message_text=update.message.text)
                    output_messages_queue.append(
                        {'text': 'Answer sent!'})
                    return
        elif query_type == 1:
            self.set_archived_state(False)
            output_messages_queue.append(
                {'text': 'Postponed'})


def update_messages():
    l = vk_instance.get_new_messages_raw()
    for raw_msg in l:
        VkMessage(raw_msg)
