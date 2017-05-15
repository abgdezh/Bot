import datetime

import postgresql

from Records.Record import Record
from VkUtil import get_vk

LIKE = 0
POSTPONE = 1
REPOST = 2
COMMENT = 3


class VkPost(Record):
    def __init__(self, raw_msg, account_id):
        Record.__init__(self, account_id)
        if raw_msg is None:
            return
        self.record_type = 'vk_post'
        self.vk = get_vk(account_id)
        self.wall_id = raw_msg['owner_id']
        self.post_id = raw_msg['id']
        self.text = raw_msg['text']
        self.author_id = raw_msg['from_id']
        self.date = datetime.datetime.fromtimestamp(raw_msg['date'])
        self.likes = raw_msg['likes']['count']
        self.reposts = raw_msg['reposts']['count']
        self.views = 0 if 'views' not in raw_msg else raw_msg['views']['count']

    def after_load(self):
        self.vk = get_vk(self.account_id)

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
        self.update_seen_state(True)

    def to_output_view(self):
        if self.author_id < 0:
            author = self.vk.get_group_name(-self.author_id)
        else:
            author = self.vk.get_user_name(self.author_id)
        res = '<b>{0}</b>\n{1}\n<i>{2}</i>'.format(
            author,
            self.text,
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
            message = incoming_messages_queue.pop_message()
            comment = message.text
            self.vk.comment_post(self.wall_id, self.post_id, comment)
            output_messages_queue.append(
                {'text': 'Post commented!'})
        elif query_type == POSTPONE:
            self.update_seen_state(False)
            output_messages_queue.append(
                {'text': 'Postponed'})


def get_last_post_id(wall_id, account_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            last_post = db.query(
                'SELECT post_id '
                'FROM vk_post NATURAL JOIN records '
                'WHERE wall_id = {0} AND '
                'account_id = {1} '
                'ORDER BY post_id DESC '
                'LIMIT 1'.format(wall_id, account_id))
            if last_post:
                return last_post[0][0]
            else:
                return None
    except Exception as e:
        print("get_last_post_id failed")
        print(e)
