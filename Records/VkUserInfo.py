from Records.Record import Record
from VkUtil import get_vk


class VkUserInfo(Record):
    def __init__(self, raw_msg, account_id):
        Record.__init__(self, account_id)
        if raw_msg is None:
            return

    def after_load(self):
        self.vk = get_vk(self.account_id)
