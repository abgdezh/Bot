import vk_api


def auth_handler():
    return input('Code:\n'), False


vk_session = vk_api.VkApi(
    token="")
vk_session.auth()
vk = vk_session.get_api()
last_message_id = 10182

while True:
    message = vk.messages.get(last_message_id=last_message_id)['items']
    if message:
        print(message[-1])
        last_message_id = message[-1]['id']
        vk.messages.send(user_id=message[-1]['user_id'],
                         message='Your id is' + str(message[-1]['user_id']))
