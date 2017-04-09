import collections
import threading
import time

import postgresql
import telegram

import Messages.message_loader


class TelegramBot:
    def __init__(self):
        try:
            with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
                self.token = db.query("select token from accounts where "
                                      "account_type = 'tg_bot'")[0][0]
        except:
            self.token = ''
        self.bot = telegram.Bot(token=self.token)
        self.update_id = 0
        self.incoming_messages = {}
        self.messages_to_send = {}

    def start(self):
        threading.Thread(target=self.parse_incoming_messages).start()

    def get_updates(self):
        updates = []
        while True:
            try:
                new_updates = self.bot.getUpdates(offset=self.update_id)
            except:
                return updates
            if not new_updates:
                break
            self.update_id = new_updates[-1].update_id + 1
            updates += new_updates
        return updates

    def send_message(self, chat_id, text):
        try:
            self.bot.sendMessage(text=text, chat_id=chat_id,
                                 parse_mode=telegram.ParseMode.HTML)
            return True
        except:
            return False

    def send_inline_keyboard(self, chat_id, text, keyboard):
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

    def parse_incoming_messages(self):
        while True:
            updates = self.get_updates()
            time.sleep(0.1)
            for update in updates:
                if update.callback_query:
                    user_id = update.callback_query.from_user.id
                elif update.message:
                    user_id = update.message.chat_id
                else:
                    continue
                if user_id not in self.incoming_messages:
                    self.begin_interaction_with_user(user_id)
                self.incoming_messages[user_id].put_message(update)

    def begin_interaction_with_user(self, user_id):
        self.incoming_messages[user_id] = IncomingMessagesQueue()
        self.messages_to_send[user_id] = collections.deque()
        threading.Thread(target=self.queries_handler,
                         args=(user_id,)).start()
        threading.Thread(target=self.message_sender,
                         args=(user_id,)).start()

    def queries_handler(self, user_id):
        while True:
            update = self.incoming_messages[user_id].get_message()
            if update.callback_query:
                data = update.callback_query.data
                msg_id, query_type = data.split('#')
                message = Messages.message_loader.load_from_database(
                    message_id=int(msg_id))
                if message is None:
                    self.messages_to_send[user_id].append(
                        {'text': 'Message not found!'}
                    )
                    continue
                message.respond(self.incoming_messages[user_id],
                                self.messages_to_send[user_id],
                                int(query_type))
            elif update.message:
                self.messages_handler(update.message, user_id)

    def messages_handler(self, message, user_id):
        text = message.text
        if text == '/start':
            self.messages_to_send[user_id].append({
                'text': 'Main menu',
                'keyboard': [
                    ["Add source"],
                    ["Remove source"],
                    ["Mute source"]
                ]
            })
        if text == 'Add source':
            pass
        if text == 'Remove source':
            pass
        if text == 'Mute source':
            pass

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
                                        caption="" if 'text' not in query else
                                        query['text'])
                else:
                    self.send_message(user_id, query['text'])
                time.sleep(1)
            time.sleep(0.1)


class IncomingMessagesQueue:
    def __init__(self):
        self.queue = collections.deque()
        self.len = 0

    def put_message(self, msg):
        self.queue.append(msg)
        self.len += 1

    def get_message(self):
        while not len(self.queue):
            time.sleep(0.1)
        self.len -= 1
        return self.queue.popleft()

    def __len__(self):
        return self.len
