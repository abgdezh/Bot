import datetime

from Messages.Message import Message
from Messages.stream_utils import get_stream_id, get_original_stream_id
from VkUtil import vk_instance


class VkWallMessage(Message):
    def __init__(self, raw_msg=None):
        if raw_msg is None:
            return
        self.original_id = raw_msg['id']
        self.text = raw_msg['text']
        if raw_msg['from_id'] > 0:
            self.author = vk_instance.get_user(raw_msg['from_id'])
        else:
            self.author = vk_instance.get_group(raw_msg['from_id'])
        self.stream_id = get_stream_id('vk-wall', raw_msg['owner_id'])
        self.date = datetime.datetime.fromtimestamp(raw_msg['date'])
        self.was_archived = False
        self.save_to_database()  # sets message_id

    def send(self, output_messages_queue):
        inline_keyboard = [
            [('Like', None, str(self.message_id) + '#0'),
             ('Share', None, str(self.message_id) + '#2'),
             ('Comment', None, str(self.message_id) + '#3')],
            [('Postpone', None, str(self.message_id) + '#1')],
            [('Open original...', 'vk.com/wall' +
              str(get_original_stream_id(self.message_id)) + '_' +
                  str(self.original_id), None)]
        ]
        output_messages_queue.append({'text': self.to_output_view(),
                                      'inline_keyboard': inline_keyboard})
        self.set_archived_state(True)

    def to_output_view(self):
        res = '<b>' + self.author + '</b>\n' + self.text + '\n' + '<i>' + str(
            self.date) + '</i>'
        return res

    def respond(self, incoming_messages_queue, output_messages_queue,
                query_type):
        if query_type == 0:
            vk_instance.like_post(get_original_stream_id(self.message_id),
                                  self.original_id)
            output_messages_queue.append(
                {'text': 'Post ' + self.text[:20] + '... liked!'})
        elif query_type == 2:
            vk_instance.share_post(get_original_stream_id(self.message_id),
                                   self.original_id)
            output_messages_queue.append(
                {'text': 'Post \'' + self.text[:20] + '...\' shared!'})
        elif query_type == 3:
            output_messages_queue.append(
                {'text': 'Type your comment to post \'' + self.text[:20] +
                         '...\''})
            while True:
                update = incoming_messages_queue.get_message()
                if update.message is not None:
                    break
            comment = update.message.text
            vk_instance.comment_post(get_original_stream_id(self.message_id),
                                     self.original_id, comment)
            output_messages_queue.append(
                {'text': 'Post commented!'})
        elif query_type == 1:
            self.set_archived_state(False)
            output_messages_queue.append(
                {'text': 'Postponed'})
