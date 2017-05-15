CREATE TABLE records (
  record_id   BIGSERIAL PRIMARY KEY,
  record_type VARCHAR,
  account_id  INTEGER,
  seen        BOOLEAN
);

CREATE TABLE vk_message (
  record_id  BIGINT REFERENCES records,
  message_id INTEGER,
  chat_id    INTEGER,
  author_id  INTEGER,
  text       VARCHAR,
  date       TIMESTAMP
);

CREATE TABLE vk_post (
  record_id BIGINT REFERENCES records,
  wall_id   INTEGER,
  post_id   INTEGER,
  author_id INTEGER,
  text      VARCHAR,
  date      TIMESTAMP,
  likes     INTEGER,
  reposts   INTEGER,
  views     INTEGER
);

CREATE TABLE vk_comment (
  record_id BIGINT REFERENCES records,
  wall_id   INTEGER,
  post_id   INTEGER,
  author_id INTEGER,
  text      VARCHAR,
  date      TIMESTAMP,
  likes     INTEGER
);

CREATE TABLE vk_user_info (
  record_id BIGINT REFERENCES records,
  user_id   INTEGER,
  info_type VARCHAR,
  value     VARCHAR
);






CREATE TABLE subscriptions (
  subscription_id   SERIAL PRIMARY KEY,
  subscription_type VARCHAR,
  account_id        INTEGER,
  send_instantly    BOOLEAN
);

CREATE TABLE vk_chat_subscription (
  subscription_id INTEGER REFERENCES subscriptions,
  chat_id         INTEGER
);

CREATE TYPE SORT_ORDERS AS ENUM ('date', 'likes', 'reposts', 'views');
CREATE TABLE vk_wall_subscription (
  subscription_id INTEGER REFERENCES subscriptions,
  wall_id         INTEGER,
  sort_order      SORT_ORDERS
);

CREATE TABLE vk_post_subscription (
  subscription_id INTEGER REFERENCES subscriptions,
  wall_id         INTEGER,
  post_id         INTEGER,
  sort_by_likes   BOOLEAN
);

CREATE TABLE vk_user_subscription (
  subscription_id INTEGER REFERENCES subscriptions,
  user_id         INTEGER,
  info_type       VARCHAR
);
