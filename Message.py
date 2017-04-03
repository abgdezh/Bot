import postgresql


class Message:
    def __new__(cls, message_id=-1):
        if message_id == -1:
            res = super(Message, cls).__new__(cls)
            res.__init__()
            return res
        return load_message(message_id)

    def __init__(self, message_id=-1):
        self.message_id = get_max_id() + 1

    def save_to_database(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                fields_names = db.query("select column_name "
                                        "from information_schema.columns "
                                        "where table_name = 'messages'")
                query = 'insert into messages values ('
                for i in range(len(fields_names)):
                    attr = fields_names[i][0]
                    if i != 0:
                        query += ', '
                    if attr in self.__dir__():
                        query += "'" + str(self.__getattribute__(attr)) + "'"
                    else:
                        query += 'null'

                query += ')'
                db.query(query)
                return True
        except Exception as e:
            print(e)
            return False

    def send(self):
        pass

    def respond(self, queue, query_type):
        print("Inline button pressed", queue, query_type)

    def get_user_id(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                response = db.query(
                    '''WITH account AS
                        (SELECT account_id
                        FROM messages
                        JOIN streams USING (stream_id)
                        WHERE message_id=''' + str(self.message_id) +
                    ''' SELECT user_id
                        FROM account
                        NATURAL JOIN accounts''')[0][0]
        except:
            response = 0
        return response

    def get_stream_type(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                response = db.query(
                    '''SELECT stream_type
                        FROM messages
                        JOIN streams USING (stream_id)
                        WHERE message_id=''' + str(self.message_id))[0][0]
        except:
            response = ""
        return response

    def set_send_and_respond_function(self):
        stream_type = self.get_stream_type()
        if stream_type == 'vk_msg':
            pass

def get_max_id():
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query(
                'select max(message_id) from messages')[0][0]
    except:
        response = 0
    return response


def load_message(message_id):
    message = Message()
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query('select * from messages where message_id ='
                                + str(message_id))
            fields_names = db.query("select column_name "
                                    "from information_schema.columns "
                                    "where table_name = 'messages'")
            for i in range(len(fields_names)):
                message.__setattr__(fields_names[i][0], response[0][i])

    except:
        pass
    message.set_send_and_respond_function()
    return message
