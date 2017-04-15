import postgresql


class Record:
    def save_to_database(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.record_id = db.query(
                    "INSERT INTO records "
                    "VALUES (DEFAULT, '{0}', '{1}', FALSE) "
                    "RETURNING record_id".format(
                        self.record_type, self.account_id))[0][0]
                fields_names = db.query(
                    "SELECT column_name "
                    "FROM information_schema.columns "
                    "WHERE table_name = '{0}'".format(self.record_type))
                query = 'INSERT INTO {0} VALUES ('.format(self.record_type)
                for i in range(len(fields_names)):
                    attr = fields_names[i][0]
                    if i != 0:
                        query += ', '
                    if attr in self.__dir__():
                        query += '\'' + str(
                            self.__getattribute__(attr)).replace('\'',
                                                                 '\'\'') + '\''
                    else:
                        query += 'NULL'

                query += ')'
                db.query(query)
                return True
        except Exception as e:
            print(query)
            return False

    def set_seen_state(self, state):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                db.query(
                    '''UPDATE records
                        SET seen = ''' + str(state) +
                    " WHERE record_id=" + str(self.record_id)
                )
                self.seen = state
        except Exception as e:
            print(e)
