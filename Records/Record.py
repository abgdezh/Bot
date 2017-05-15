import datetime
import traceback

import postgresql
import sys


class Record:
    def __init__(self, account_id):
        self.account_id = account_id
        self.seen = False
        self.date_to_show = None

    def save_to_database(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                date_to_show = "'{0}'".format(self.date_to_show) \
                    if self.date_to_show is not None else "NULL"
                self.record_id = db.query(
                    "INSERT INTO records "
                    "VALUES (DEFAULT, '{0}', '{1}', FALSE, {2}) "
                    "RETURNING record_id".format(
                        self.record_type, self.account_id, date_to_show))[
                    0][0]
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
            print("save_to_database failed")
            print(query)
            return False

    def update_seen_state(self, state, date=None):
        if date is None:
            date = datetime.datetime.today()
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                db.query(
                    '''UPDATE records
                        SET seen = ''' + str(state) +
                    " WHERE record_id=" + str(self.record_id)
                )
                db.query(
                    'UPDATE records '
                    'SET date_to_show = \'{0}\' '
                    'WHERE record_id = {1}'.format(date, self.record_id)
                )
                self.seen = state
        except Exception as e:
            print("update_seen_state failed")
            print(e)
