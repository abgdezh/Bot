import postgresql


def add_vk_chat_subscription(chat_id, account_id):
    if chat_id in get_chat_subscriptions(account_id):
        return
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscription_id = \
                db.query("INSERT INTO subscriptions "
                         "VALUES (DEFAULT, 'vk_chat', {0}) "
                         "RETURNING subscription_id".format(account_id))[0][0]
            db.query("INSERT INTO vk_chat_subscription "
                     "VALUES ({0}, {1})".format(subscription_id, chat_id))
    except Exception as e:
        print("add_vk_chat_subscription failed")
        print(e)


def add_vk_wall_subscription(wall_id, account_id):
    if wall_id in get_wall_subscriptions(account_id):
        return
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscription_id = \
                db.query("INSERT INTO subscriptions "
                         "VALUES (DEFAULT, 'vk_wall', {0}) "
                         "RETURNING subscription_id".format(account_id))[0][0]
            db.query("INSERT INTO vk_wall_subscription "
                     "VALUES ({0}, {1})".format(subscription_id, wall_id))
    except Exception as e:
        print("add_vk_wall_subscription failed")
        print(e)


def get_chat_subscriptions(account_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscriptions = \
                db.query('SELECT chat_id '
                         'FROM vk_chat_subscription '
                         'NATURAL JOIN subscriptions '
                         'WHERE account_id = {0}'.format(account_id))
            subscriptions = [i[0] for i in subscriptions]
            return subscriptions
    except Exception as e:
        print("get_chat_subscriptions failed")
        print(e)
        return []


def get_wall_subscriptions(account_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscriptions = \
                db.query('SELECT wall_id '
                         'FROM vk_wall_subscription '
                         'NATURAL JOIN subscriptions '
                         'WHERE account_id = {0}'.format(account_id))
            subscriptions = [i[0] for i in subscriptions]
            return subscriptions
    except Exception as e:
        print("get_wall_subscriptions failed")
        print(e)
        return []


def delete_vk_chat_subscription(chat_id, account_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscription_id = db.query(
                "SELECT subscription_id "
                "FROM vk_chat_subscription "
                "NATURAL JOIN subscriptions "
                "WHERE chat_id = {0} AND "
                "account_id = {1}".format(chat_id, account_id)
            )
            if not subscription_id:
                return
            subscription_id = subscription_id[0][0]
            db.query(
                "DELETE FROM vk_chat_subscription "
                "WHERE subscription_id = {0}".format(subscription_id)
            )
            db.query(
                "DELETE FROM subscriptions "
                "WHERE subscription_id = {0}".format(subscription_id)
            )
    except Exception as e:
        print("delete_vk_chat_subscription failed")
        print(e)


def delete_vk_wall_subscription(wall_id, account_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            subscription_id = db.query(
                "SELECT subscription_id "
                "FROM vk_wall_subscription "
                "NATURAL JOIN subscriptions "
                "WHERE wall_id = {0} AND "
                "account_id = {1}".format(wall_id, account_id)
            )
            if not subscription_id:
                return
            subscription_id = subscription_id[0][0]
            db.query(
                "DELETE FROM vk_wall_subscription "
                "WHERE subscription_id = {0}".format(subscription_id)
            )
            db.query(
                "DELETE FROM subscriptions "
                "WHERE subscription_id = {0}".format(subscription_id)
            )
    except Exception as e:
        print("delete_vk_wall_subscription failed")
        print(e)
