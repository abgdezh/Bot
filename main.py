import TelegramBot
import time

telegramBot = TelegramBot.TelegramBot()
telegramBot.start()

user_id = 62827234

while user_id not in telegramBot.messages_to_send:
    time.sleep(0.1)


# how to add simple message
telegramBot.messages_to_send[user_id].append({'text': 'some text'})
# how to add a photo
telegramBot.messages_to_send[user_id].append(
    {'text': 'description of photo',
     'photo': 'http://fit4brain.com/wp-content/uploads/2014/05/cat.jpg'})
# how to add a keyboard
telegramBot.messages_to_send[user_id].append(
    {'text': 'Sending a keyboard...',
     'keyboard': [['a', 'b'], ['c']]})

# how to add an inline keyboard (order of arguments: button text, url,
# data to resend back)
inline_keyboard = [[('VK', 'vk.com', None), ('YA', 'ya.ru', None)],
                   [('like', None, '239#1')]]

telegramBot.messages_to_send[user_id].append(
    {'text': 'Sending inline buttons...',
     'inline_keyboard': inline_keyboard})
