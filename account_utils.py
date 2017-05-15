import postgresql


def save_vk_account(user_id, token, vk_id):
    if user_id in get_vk_ids_and_account_ids(user_id):
        return
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            account_id = db.query(
                "INSERT INTO accounts "
                "VALUES (DEFAULT, {0}, 'vk', '{1}', {2}) "
                "RETURNING account_id".format(user_id, token, vk_id)
            )[0][0]
            return account_id
    except Exception as e:
        print("save_vk_account failed")
        print(e)


def get_vk_ids_and_account_ids(user_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            ids = db.query(
                "SELECT id, account_id "
                "FROM accounts "
                "WHERE user_id = {0}".format(user_id)
            )
            return ids
    except Exception as e:
        print("get_vk_ids_and_account_ids failed")
        print(e)
        return [[]]


def get_vk_accounts():
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            accounts = db.query("SELECT account_id "
                                "FROM accounts "
                                "WHERE account_type = 'vk'")
            accounts = [i[0] for i in accounts]
            return accounts
    except Exception as e:
        print("get_vk_accounts failed")
        print(e)
        return []


def get_user_id_by_account_id(account_id, cache={}):
    if account_id in cache:
        return cache[account_id]
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            cache[account_id] = db.query('SELECT user_id '
                                         'FROM accounts '
                                         'WHERE account_id = {0}'.format(
                account_id))[0][0]
            return cache[account_id]

    except Exception as e:
        print("get_user_id_by_account_id failed")
        print(e)
        exit(1)