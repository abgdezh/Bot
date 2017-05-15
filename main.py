import threading

import TelegramController
from Subscriptions.update_messages import vk_updater

TelegramController.TelegramBot().start()

threading.Thread(target=vk_updater).start()
