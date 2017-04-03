# import TelegramBot
#
# t = TelegramBot.TelegramBot()
# r = t.get_updates()
# for i in r:
#     print(i)
#
# arr = [[0] * 8 for i in range(4)]
# for i in range(4):
#     for j in range(8):
#         arr[i][j] = chr(ord('A') + i * 8 + j)
# t.send_keyboard(62827234, '~', arr)

from VkUtil import VkUtil

t = VkUtil()
#t.update_messages()

import Message
import datetime

m = Message.Message()
m.message_id = 1
m.stream_id = 2
m.original_id = 3
m.title = 'titl'
m.author = 'me'
m.date = datetime.datetime.today()
m.was_archivated = True
m.save_to_database()