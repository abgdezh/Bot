import collections
import threading
import postgresql
import telegram
import time
import Message


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
        self.queries_queues = {}
        self.responses_queues = {}

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
            self.bot.sendMessage(text=text, chat_id=chat_id)
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
                                      button_arr))
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
                                      button_arr))
            return True
        except:
            return False

    def parse_incoming_messages(self):
        while True:
            updates = self.get_updates()
            time.sleep(0.1)
            for update in updates:
                if update.callback_query:
                    user_id = update.callback_query.chat_id
                elif update.message:
                    user_id = update.message.chat_id
                else:
                    continue
                if user_id not in self.queries_queues:
                    self.queries_queues[user_id] = collections.deque()
                    self.responses_queues[user_id] = collections.deque()
                    threading.Thread(target=self.queries_handler,
                                     args=(user_id,)).start()
                    threading.Thread(target=self.updater,
                                     args=(user_id,)).start()
                self.queries_queues[user_id].append(update)

    def queries_handler(self, user_id):
        while True:
            while len(self.queries_queues[user_id]):
                update = self.queries_queues[user_id].popleft()
                if update.callback_query:
                    data = update.callback_query.data
                    msg_id, query_type = data.split('#')
                    message = Message.Message(message_id=int(msg_id))
                    message.respond(self.queries_queues[user_id],
                                    int(query_type))
                elif update.message:
                    text = update.message.text
                    self.command_handler(update.message)
            time.sleep(0.1)

    def command_handler(self, message):
        pass

    def updater(self, user_id):
        while True:
            while len(self.responses_queues[user_id]):
                query = self.responses_queues[user_id].popleft()
                if 'keyboard' in query:
                    self.send_keyboard(user_id, query['text'],
                                       query['keyboard'])
                elif 'inline_keyboard' in query:
                    self.send_keyboard(user_id, query['text'],
                                       query['inline_keyboard'])
                elif 'photo' in query:
                    self.bot.send_photo()
                else:
                    self.send_message(user_id, query['text'])
            time.sleep(1)
