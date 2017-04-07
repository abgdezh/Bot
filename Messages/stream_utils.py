import postgresql


def get_original_stream_id(message_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query(
                '''SELECT original_stream_id
                    FROM messages
                    JOIN streams USING (stream_id)
                    WHERE message_id=''' + str(message_id))[0][0]
            return int(response)
    except:
        return 0


def get_stream_id(stream_type, original_id):
    try:
        with postgresql.open('mb:qwerty@localhost:5432/bot') as db:
            response = db.query(
                '''SELECT *
                    FROM streams
                    WHERE stream_type=\'''' + stream_type +
                "\' AND original_stream_id=" + str(original_id)
            )
            if response:
                return response[0][0]
            else:
                return db.query(
                    '''INSERT INTO streams (stream_type, original_stream_id)
                        VALUES (\'''' + stream_type + '\', ' + str(
                        original_id) +
                    ") RETURNING stream_id"
                )[0][0]
    except Exception as e:
        print(e)
