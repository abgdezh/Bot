import telegram
import vk_api
import datetime
import time


def auth_handler():
    return input('Code:\n'), False


vk_session = vk_api.VkApi(
    token="")
vk_session.auth()
bot = telegram.Bot(token='')
chat_id = 62827234  # 67037445
vk = vk_session.get_api()
update_id = 1576001000
while True:
    try:
        updates = bot.getUpdates(offset=update_id)
    except:
        continue
    for u in updates:
        if not u['message']: continue
        text = u['message']['text']
        chat_id = u['message']['chat']['id']
        update_id = u['update_id'] + 1
        try:
            arr = text.split()
            domain = arr[0]
            num = int(arr[1])
        except:
            num = 5
        print(domain)
        while True:
            try:
                res = vk.wall.get(domain=domain, count=num)
                break
            except:
                pass
        for post in res['items'][::-1]:
            text = str(datetime.datetime.fromtimestamp(post['date'])) + '\n' + \
                   post['text'] + "\nlikes: " + str(
                post['likes']['count']) + ", reposts: " + str(
                post['reposts']['count']) + '\n'
            link = 'http://vk.com/wall' + str(post['owner_id']) + '_' + str(
                post['id'])
            attachment = post['attachments'][
                0] if 'attachments' in post else None
            if attachment and 'photo' in attachment:
                keys = attachment['photo'].keys()
                keys = [k for k in keys if k.startswith('photo_')]
                keys.sort(key=lambda x: int(x.split('photo_')[1]))
                photo = attachment['photo'][keys[-1]]
            else:
                photo = None
            try:
                bot.sendMessage(chat_id=chat_id, text=text + link,
                                disable_web_page_preview=True)
                if photo: bot.sendPhoto(chat_id=chat_id, photo=photo)
            except telegram.error.Unauthorized:
                print(u['message']['text'], u['message']['chat'])
                break
            else:
                time.sleep(1)
