from Records.VkMessage import VkMessage


def update_messages(vk):
    for message in vk.get_new_messages_raw():
        VkMessage(message, vk.account_id)