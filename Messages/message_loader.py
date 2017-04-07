import postgresql

from Messages.Message import Message
from Messages.VkMessage import VkMessage
from Messages.VkWall import VkWall


def load_from_database(message_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query('select * from messages where message_id =' +
                                str(message_id))
            fields_names = db.query("select column_name "
                                    "from information_schema.columns "
                                    "where table_name = 'messages'")
            message = create_message_by_stream_type(
                get_stream_type_by_message_id(message_id))
            for i in range(len(fields_names)):
                message.__setattr__(fields_names[i][0], response[0][i])
    except Exception as e:
        print(e)
        return None
    return message


def get_stream_type_by_message_id(message_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query(
                '''SELECT stream_type
                    FROM messages
                    JOIN streams USING (stream_id)
                    WHERE message_id=''' + str(message_id))[0][0]
    except:
        response = ""
    return response


def create_message_by_stream_type(stream_type):
    d = {'vk-msg': VkMessage,
         'vk-wall': VkWall}
    if stream_type not in d:
        return Message()
    return d[stream_type]()


