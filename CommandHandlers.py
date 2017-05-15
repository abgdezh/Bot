import os
import re

from account_utils import save_vk_account, get_vk_ids_and_account_ids
from Subscriptions.subscription_utils import add_vk_chat_subscription, \
    add_vk_wall_subscription, get_chat_subscriptions, get_wall_subscriptions, \
    delete_vk_wall_subscription, delete_vk_chat_subscription
from VkUtil import get_vk

default_keyboard = [
    ["Add vk account"],
    ["Add source"],
    ["Remove source"],
    ["Exit"]
]


def start(bot, user_id, is_on_start=True):
    bot.messages_to_send[user_id].append({
        'text': 'Hello, this is an aggregator bot!'
        if is_on_start else 'Exited',
        'keyboard': default_keyboard
    })


def add_vk_account(bot, user_id):
    bot.messages_to_send[user_id].append({
        'text': 'Open this link, copy the content of the address line and '
                'paste it here',
        'inline_keyboard':
            [[('Oauth',
               "https://oauth.vk.com/authorize?client_id=4627417&redirect_uri"
               "=close.html&scope=998431&response_type=token&v=5.64",
               None)]]
    })
    while True:
        message = bot.incoming_messages[user_id].pop_message()
        if message.text == 'Exit':
            start(bot, user_id, False)
            return
        if not message.text.count('access_token='):
            bot.messages_to_send[user_id].append({
                'text': 'This is not a token!'})
        else:
            break
    token = message.text.split('access_token=')[1]
    token = token.split('&')[0]
    vk_id = int(message.text.split('=')[-1])
    save_vk_account(user_id, token, vk_id)
    bot.messages_to_send[user_id].append({
        'text': 'Account added!',
        'keyboard': default_keyboard
    })


def read_aссount_id(bot, user_id):
    vk_account_ids = get_vk_ids_and_account_ids(user_id)
    vk_account_names = [
        get_vk(account_id).get_user_name() + " (id={0})".format(vk_id)
        for vk_id, account_id in vk_account_ids]
    bot.messages_to_send[user_id].append({
        'text': 'Select vk account',
        'keyboard': [
                        [name] for name in vk_account_names
                    ] + [['Exit']]
    })
    while True:
        message = bot.incoming_messages[user_id].pop_message()
        if message.text == 'Exit':
            start(bot, user_id, False)
            return
        if message.text not in vk_account_names:
            bot.messages_to_send[user_id].append({
                'text': 'Incorrect account!'})
        else:
            break
    num = vk_account_names.index(message.text)
    account_id = vk_account_ids[num][1]
    return account_id


def read_subscription_type(bot, user_id):
    bot.messages_to_send[user_id].append({
        'text': 'Select type of subscription',
        'keyboard': [
            ['Chat'],
            ['Wall'],
            ['Exit']
        ]
    })
    while True:
        message = bot.incoming_messages[user_id].pop_message()
        if message.text == 'Exit':
            start(bot, user_id, False)
            return
        if message.text not in ('Chat', 'Wall'):
            bot.messages_to_send[user_id].append({
                'text': 'Incorrect type!'})
        else:
            break
    subscription_type = message.text
    return subscription_type


def add_source(bot, user_id):
    account_id = read_aссount_id(bot, user_id)
    subscription_type = read_subscription_type(bot, user_id)
    if account_id is None or subscription_type is None:
        return
    vk = get_vk(account_id)
    bot.messages_to_send[user_id].append({
        'text': 'Type url of the wall (e.g., id1 or club1387831 or '
                'oldlentach)'})
    message = bot.incoming_messages[user_id].pop_message()
    if subscription_type == 'Chat':
        if message.text[0] == 'c' and message.text[1:].isdigit():
            chat_id = int(message.text[1:]) + 2 * 10 ** 9
        else:
            chat_id = vk.get_wall_id_by_url(message.text)
        add_vk_chat_subscription(chat_id, account_id)
    elif subscription_type == 'Wall':
        add_vk_wall_subscription(vk.get_wall_id_by_url(message.text),
                                 account_id)
    bot.messages_to_send[user_id].append({
        'text': 'Subscription added!',
        'keyboard': default_keyboard
    })


def name(subscription_type, id_, vk):
    if subscription_type == 'Chat':
        if id_ > 2 * 10 ** 9:
            return vk.get_chat_title(id_ - 2 * 10 ** 9)
        else:
            return vk.get_user_name(id_)
    elif subscription_type == 'Wall':
        if id_ < 0:
            return vk.get_group_name(-id_)
        else:
            return vk.get_user_name(id_)


def read_subscription(bot, user_id, account_id):
    subscription_type = read_subscription_type(bot, user_id)
    if subscription_type is None:
        return
    vk = get_vk(account_id)
    ids = get_chat_subscriptions(account_id) if subscription_type == 'Chat' \
        else get_wall_subscriptions(account_id)
    sources_names = \
        [name(subscription_type, id_, vk) + ' (id={0})'.format(id_)
         for id_ in ids]
    bot.messages_to_send[user_id].append({
        'text': 'Select ' + subscription_type.lower(),
        'keyboard': [[sources_name] for sources_name in sources_names
                     ] + [['Exit']]
    })
    while True:
        message = bot.incoming_messages[user_id].pop_message()
        if message.text == 'Exit':
            start(bot, user_id, False)
            return
        if message.text not in sources_names:
            bot.messages_to_send[user_id].append({
                'text': 'Incorrect account!'})
        else:
            break
    id_ = int(re.match(r'.+ \(id=(.+)\)$', message.text).group(1))
    return subscription_type, id_


def remove_source(bot, user_id):
    account_id = read_aссount_id(bot, user_id)
    subscription = read_subscription(bot, user_id, account_id)
    if account_id is None or subscription is None:
        return
    subscription_type, id_ = subscription
    if subscription_type == 'Wall':
        delete_vk_wall_subscription(id_, account_id)
    elif subscription_type == 'Chat':
        delete_vk_chat_subscription(id_, account_id)
    bot.messages_to_send[user_id].append({
        'text': 'You have successfully removed subscription!',
        'keyboard': default_keyboard})


def ls(bot, user_id):
    if user_id != 62827234:
        return
    bot.messages_to_send[user_id].append({
        'text': os.path.abspath('.'),
        'keyboard':
            [[('/cd ' if os.path.isdir(f) else '/get ') + f]
             for f in os.listdir('.')] +
            [['/cd ..']] +
            [['Exit']]
    })


def cd(bot, user_id, path):
    if user_id != 62827234:
        return
    try:
        os.chdir(path)
        ls(bot, user_id)
    except Exception as e:
        bot.messages_to_send[user_id].append({'text': str(e)})


def get(bot, user_id, path):
    if user_id != 62827234:
        return
    try:
        bot.messages_to_send[user_id].append({
            'text': path,
            'document': path})
    except Exception as e:
        bot.messages_to_send[user_id].append({'text': str(e)})
