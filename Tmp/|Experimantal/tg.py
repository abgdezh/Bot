import telegram

bot = telegram.Bot(token='')
update_id = 157600100
while True:
    updates = bot.getUpdates(offset=update_id)
    for u in updates:
        print(u)
        text = u['message']['text']
        chat_id = u['message']['chat']['id']
        update_id = u['update_id'] + 1
        bot.sendMessage(chat_id=chat_id, text=str(u))
    # bot.sendMessage(chat_id=chat_id, text='<b>{0:s}</b>'.format(text), parse_mode=telegram.ParseMode.HTML)
    # bot.sendMessage(chat_id=chat_id, text='<i>{0:s}</i>'.format(text), parse_mode=telegram.ParseMode.HTML)
