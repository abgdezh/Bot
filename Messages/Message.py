import postgresql


class Message:
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
                        query += '\'' + str(
                            self.__getattribute__(attr)).replace(
                            '\'', '\'\'') + '\''
                    else:
                        query += 'default' if attr == 'message_id' else 'null'

                query += ') returning message_id'
                self.message_id = db.query(query)[0][0]
                return True
        except Exception as e:
            print(e)
            return False

    def send(self, output_messages_queue):
        pass

    def respond(self, incoming_messages_queue, output_messages_queue,
                query_type):
        output_messages_queue.append({
            'text': 'Responding to ' + self.text + ", " + str(query_type)})

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

    def set_archived_state(self, state):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                db.query(
                    '''UPDATE messages
                        SET was_archived = ''' + str(state) +
                    " WHERE message_id=" + str(self.message_id)
                )
                self.was_archived = state
        except Exception as e:
            print(e)
