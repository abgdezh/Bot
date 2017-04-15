import datetime

from Records.Record import Record
from VkUtil import VkUtil

LIKE = 0
POSTPONE = 1
REPOST = 2
COMMENT = 3


class VkPost(Record):
    def __init__(self, raw_msg, account_id):
        if raw_msg is None:
            return
        self.record_type = 'vk_post'
        self.account_id = account_id
        self.seen = False

        self.vk = VkUtil(account_id)

        self.wall_id = raw_msg['owner_id']
        self.post_id = raw_msg['id']
        self.text = raw_msg['text']
        self.author_id = raw_msg['from_id']
        self.date = datetime.datetime.fromtimestamp(raw_msg['date'])
        self.likes = raw_msg['likes']['count']
        self.reposts = raw_msg['reposts']['count']
        self.views = raw_msg['views']['count']
        self.save_to_database()  # sets record_id

    def after_load(self):
        self.vk = VkUtil(self.account_id)

    def send(self, output_messages_queue):
        inline_keyboard = [
            [('Like', None, '{0}#{1}'.format(self.record_id, LIKE)),
             ('Share', None, '{0}#{1}'.format(self.record_id, REPOST)),
             ('Comment', None, '{0}#{1}'.format(self.record_id, COMMENT))],
            [('Postpone', None, '{0}#{1}'.format(self.record_id, POSTPONE))],
            [('Open original...',
              'vk.com/wall{0}_{1}'.format(self.wall_id, self.post_id), None)]
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
        if query_type == LIKE:
            self.vk.like_post(self.wall_id, self.post_id)
            output_messages_queue.append(
                {'text': 'Post "' + self.text[:20] + '..." liked!'})
        elif query_type == REPOST:
            self.vk.share_post(self.wall_id, self.post_id)
            output_messages_queue.append(
                {'text': 'Post "' + self.text[:20] + '..." shared!'})
        elif query_type == COMMENT:
            output_messages_queue.append(
                {'text': 'Type your comment to post \'' + self.text[:20] +
                         '...\''})
            while True:
                update = incoming_messages_queue.pop()
                if update.message is not None:
                    break
            comment = update.message.text
            self.vk.comment_post(self.wall_id, self.post_id, comment)
            output_messages_queue.append(
                {'text': 'Post commented!'})
        elif query_type == POSTPONE:
            self.set_seen_state(False)
            output_messages_queue.append(
                {'text': 'Postponed'})
