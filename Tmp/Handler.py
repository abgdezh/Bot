import Messages.message_loader
from Messages import Message


def handler(update):
    if update.callback_query:
        message_id, request_type = update.callback_query.data.split('#', 1)
        message = Messages.message_loader.load_from_database(message_id)
        message.request(request_type)
    elif update.message:
        print(update.message)
