import datetime
import time

from account_utils import get_vk_accounts
from Records.VkMessage import VkMessage
from Records.VkPost import get_last_post_id, VkPost
from Subscriptions.subscription_utils import get_chat_subscriptions, \
    get_wall_subscriptions
from VkUtil import get_vk


def update_messages(account_id):
    vk = get_vk(account_id)
    subscriptions = set(get_chat_subscriptions(account_id))
    for message in vk.get_new_messages_raw():
        msg = VkMessage(message, vk.account_id)
        if msg.chat_id in subscriptions and msg.author_id != vk.get_own_id():
            msg.date_to_show = datetime.datetime.today()
        else:
            msg.date_to_show = None
        msg.save_to_database()


def update_posts(account_id):
    vk = get_vk(account_id)
    subscriptions = get_wall_subscriptions(account_id)
    for wall_id in subscriptions:
        for raw_post in vk.get_posts(wall_id,
                                     get_last_post_id(wall_id, account_id)):
            post = VkPost(raw_post, vk.account_id)
            post.date_to_show = datetime.datetime.today()
            post.save_to_database()


def vk_updater():
    while True:
        accounts = get_vk_accounts()
        for account in accounts:
            update_messages(account)
            update_posts(account)
        time.sleep(0.1)
