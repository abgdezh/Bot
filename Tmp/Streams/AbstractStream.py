class AbstractStream:
    def get_updates(self):
        # implemented in children
        pass

    def send_message(self, message):
        # implemented in children
        pass

    def save_messages(self):
        messages = self.get_updates()
        # TODO Implement saving to a DB
