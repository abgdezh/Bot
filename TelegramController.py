import collections
import threading
import time
from sys import stderr

import postgresql
import sys
import telegram

import Records.record_loader
from account_utils import get_user_id_by_account_id
from CommandHandlers import *
from Records.record_loader import load_from_database


class TelegramBot:
    def __init__(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.token = db.query("SELECT token FROM accounts WHERE "
                                      "account_type = 'tg_bot'")[0][0]
        except Exception:
            print("Cannot load telegram bot token!", file=stderr)
            sys.exit(1)
        self.bot = telegram.Bot(token=self.token)
        self.last_update_id = 0
        self.incoming_messages = {}
        self.messages_to_send = {}

    def start(self):
        threading.Thread(target=self.distribute_incoming_queries).start()
        threading.Thread(target=self.monitor_database_updates).start()

    def get_updates(self):
        """
        Gets new messages sent to bot.
        :return: array of telegram messages
        """
        updates = []
        while True:
            try:
                new_updates = self.bot.getUpdates(offset=self.last_update_id)
            except:
                return updates
            if not new_updates:
                break
            self.last_update_id = new_updates[-1].update_id + 1
            updates += new_updates
        return updates

    def send_message(self, chat_id, text):
        """
        Sends message from the bot
        :param chat_id: id of user
        :param text: text in html format
        :return: True if message was sent, False otherwise
        """
        try:
            self.bot.sendMessage(text=text, chat_id=chat_id,
                                 parse_mode=telegram.ParseMode.HTML)
            return True
        except:
            return False

    def send_inline_keyboard(self, chat_id, text, keyboard):
        """
        Sends inline keyboard.
        :param chat_id: id of user
        :param text: text in html format
        :param keyboard: Keyboard in format [[('Button text', 
        'http://example.com/link/to/open/on/click', 'Data to be sent back 
        after click')]]
        :return: True if message was sent, False otherwise
        """
        button_arr = []
        for i in keyboard:
            button_arr.append([])
            for button_text, url, data in i:
                button_arr[-1].append(telegram.InlineKeyboardButton(
                    text=button_text, callback_data=data, url=url))
        try:
            self.bot.send_message(chat_id=chat_id, text=text,
                                  reply_markup=telegram.InlineKeyboardMarkup(
                                      button_arr),
                                  parse_mode=telegram.ParseMode.HTML)
            return True
        except:
            return False

    def send_keyboard(self, chat_id, text, keyboard):
        """
        Sends keyboard.
        :param chat_id: id of user
        :param text: text in html format
        :param keyboard: array of array of strings
        :return: True if message was sent, False otherwise
        """
        button_arr = []
        for i in keyboard:
            button_arr.append([])
            for button_text in i:
                button_arr[-1].append(
                    telegram.KeyboardButton(text=button_text))
        try:
            self.bot.send_message(chat_id=chat_id, text=text,
                                  reply_markup=telegram.ReplyKeyboardMarkup(
                                      button_arr),
                                  parse_mode=telegram.ParseMode.HTML)
            return True
        except:
            return False

    def send_document(self, chat_id, text, path_to_file):
        try:
            self.bot.sendDocument(caption=text, chat_id=chat_id,
                                  document=open(path_to_file, 'rb'))
            return True
        except Exception as e:
            print(e)
            return False

    def distribute_incoming_queries(self):
        while True:
            updates = self.get_updates()
            for update in updates:
                if update.callback_query:
                    user_id = update.callback_query.from_user.id
                elif update.message:
                    user_id = update.message.chat_id
                else:
                    continue
                if user_id not in self.incoming_messages:
                    self.begin_interaction_with_user(user_id)
                self.incoming_messages[user_id].push(update)
            time.sleep(0.1)

    def begin_interaction_with_user(self, user_id):
        self.incoming_messages[user_id] = IncomingMessagesQueue()
        self.messages_to_send[user_id] = collections.deque()
        threading.Thread(target=self.queries_handler,
                         args=(user_id,)).start()
        threading.Thread(target=self.message_sender,
                         args=(user_id,)).start()

    def queries_handler(self, user_id):
        while True:
            update = self.incoming_messages[user_id].pop()
            if update.callback_query:
                data = update.callback_query.data
                record_id, query_type = data.split('#')
                record = Records.record_loader.load_from_database(
                    record_id=int(record_id))
                if record is None:
                    self.messages_to_send[user_id].append(
                        {'text': 'Record not found!'}
                    )
                    continue
                record.respond(self.incoming_messages[user_id],
                               self.messages_to_send[user_id],
                               int(query_type))
            elif update.message:
                self.messages_handler(update.message, user_id)

    def messages_handler(self, message, user_id):
        text = message.text
        methods = {'/start': start,
                   'Add vk account': add_vk_account,
                   'Add source': add_source,
                   'Remove source': remove_source,
                   'Exit': lambda a, b: start(a, b, False),
                   '/ls': ls
                   }
        if text in methods:
            methods[text](self, user_id)
        elif text.startswith('/cd '):
            cd(self, user_id, text.split('/cd ')[1])
        elif text.startswith('/get '):
            get(self, user_id, text.split('/get ')[1])

    def message_sender(self, user_id):
        while True:
            while len(self.messages_to_send[user_id]):
                query = self.messages_to_send[user_id].popleft()
                if 'keyboard' in query:
                    self.send_keyboard(user_id, query['text'],
                                       query['keyboard'])
                elif 'inline_keyboard' in query:
                    self.send_inline_keyboard(user_id, query['text'],
                                              query['inline_keyboard'])
                elif 'photo' in query:
                    self.bot.send_photo(user_id, query['photo'],
                                        caption='' if 'text' not in query else
                                        query['text'])
                elif 'document' in query:
                    self.send_document(
                        user_id,
                        '' if 'text' not in query else query['text'],
                        query['document']
                    )
                else:
                    self.send_message(user_id, query['text'])
                time.sleep(1)
            time.sleep(0.1)

    def monitor_database_updates(self):
        while True:
            time.sleep(1)
            try:
                with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                    records = \
                        db.query('SELECT record_id '
                                 'FROM records '
                                 'WHERE seen = FALSE '
                                 'AND date_to_show < current_timestamp '
                                 'LIMIT 1')
                    if not records:
                        continue
                    record_id = records[0][0]
                    record = load_from_database(record_id)
                    user_id = get_user_id_by_account_id(record.account_id)
                    if user_id not in self.messages_to_send:
                        self.begin_interaction_with_user(user_id)
                    record.send(self.messages_to_send[user_id])
            except Exception as e:
                print("monitor_database_updates failed")
                print(e)


class IncomingMessagesQueue:
    def __init__(self):
        self.queue = collections.deque()
        self.len = 0

    def push(self, msg):
        self.queue.append(msg)
        self.len += 1

    def pop(self):
        while not len(self.queue):
            time.sleep(0.1)
        self.len -= 1
        return self.queue.popleft()

    def pop_message(self):
        while True:
            update = self.pop()
            if update.message is not None:
                return update.message

    def __len__(self):
        return self.len
