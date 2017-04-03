import TelegramBot
import threading

telegramBot = TelegramBot.TelegramBot()
telegramBot.start()

user_id = 62827234
# how to add simple message
telegramBot.add_message_to_queue(user_id, 'some text')
# how to add a photo
telegramBot.add_message_to_queue(user_id, 'description of photo',
                                 photo='http://fit4brain.com/wp-content/uploads/2014/05/cat.jpg')
# how to add a keyboard
telegramBot.add_message_to_queue(user_id, 'Sending a keyboard...',
                                 keyboard=[['a', 'b'], ['c']])

# how to add an inline keyboard (order of arguments: button text, url,
# data to resend back)
inline_keyboard = [[('VK', 'vk.com', None), ('YA', 'ya.ru', None)],
                   [('like', None, '239#1')]]

telegramBot.add_message_to_queue(user_id, 'Sending inline buttons...',
                                 inline_keyboard=inline_keyboard)
