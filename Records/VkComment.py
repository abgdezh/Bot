from Records.Record import Record
from VkUtil import VkUtil


class VkComment(Record):
    def __init__(self, raw_msg, account_id):
        pass

    def after_load(self):
        self.vk = VkUtil(self.account_id)