import postgresql

from Records.Record import Record
from Records.VkMessage import VkMessage
from Records.VkPost import VkPost
from Records.VkComment import VkComment
from Records.VkUserInfo import VkUserInfo


def load_from_database(record_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            record_type = db.query('SELECT record_type '
                                   'FROM records '
                                   'WHERE record_id = '
                                   '{0}'.format(record_id))[0][0]
            fields_names = db.query("SELECT DISTINCT column_name "
                                    "FROM information_schema.columns "
                                    "WHERE table_name IN "
                                    "('{0}', 'records')".format(record_type))
            message = create_message_by_record_type(record_type)
            fields_values = db.query('SELECT ' + ', '.join([i[0] for i in
                                                            fields_names]) +
                                     ' FROM {0} '
                                     'NATURAL JOIN records '
                                     'WHERE record_id = '
                                     '{1}'.format(record_type, record_id))
            for i in range(len(fields_names)):
                message.__setattr__(fields_names[i][0], fields_values[0][i])
            message.after_load()
    except Exception as e:
        print(e)
        return None
    return message


def create_message_by_record_type(record_type):
    d = {'vk_message': VkMessage,
         'vk_post': VkPost,
         'vk_comment': VkComment,
         'vk_user_info': VkUserInfo
         }
    if record_type not in d:
        return Record()
    return d[record_type](None, 0)
