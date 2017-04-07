from Messages.Message import Message


class VkMessage(Message):


    def sendToTelegram(self):
        user_id = 62827234
        text = self.author + "\n" + self.text + "\n" + self.date
        keyboard = [[('Go to', 'vk.com', None)],
                    [('Next', None, 'vkmsg#next#' + str(self.original_id))]]
        self.bot.send_inline_keyboard(user_id, text, keyboard)

    def request(bot, chat_id, data):
        bot.send_message(chat_id, "Send reply to " + "<>" + data)
        response = bot.get_updates()
