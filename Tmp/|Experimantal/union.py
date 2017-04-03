import telegram
import vk_api

def auth_handler():
	return input('Code:\n'), False

vk_session = vk_api.VkApi(token="")
vk_session.auth()
vk = vk_session.get_api()

bot = telegram.Bot(token='')
update_id = 157600104
while True:
	updates = bot.getUpdates(offset=update_id)
	for u in updates:
		print(u)
		text = u['message']['text']
		chat_id = u['message']['chat']['id']
		update_id = u['update_id'] + 1
		vk.messages.send(user_id=113454893, message=text)
