drop table favorites;
drop table tweets;
drop table follows;
drop table users;


CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email varchar(100),
  password varchar(130) NOT NULL,
  salt varchar(70) NOT NULL,
  phone varchar(20),
  name varchar(40),
  created_at timestamptz NOT NULL default CURRENT_TIMESTAMP,
  last_login_at timestamptz NOT NULL default CURRENT_TIMESTAMP,
  deleted_at timestamptz,
  latitude DECIMAL,
  longtitude DECIMAL,
  UNIQUE (email)
);

CREATE TABLE tweets (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  content varchar(300) NOT NULL,
  latitude DECIMAL,
  longtitude DECIMAL,
  num_favorites INTEGER NOT NULL default 0,
  created_at timestamptz NOT NULL default CURRENT_TIMESTAMP,
  deleted_at timestamptz
);
CREATE INDEX tweet_user_index ON tweets (deleted_at, user_id);

CREATE TABLE follows (
  id BIGSERIAL PRIMARY KEY,
  followee_id BIGINT NOT NULL REFERENCES users(id),
  follower_id BIGINT NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL default CURRENT_TIMESTAMP,
  deleted_at timestamptz
);
CREATE INDEX follower_index ON follows (deleted_at, follower_id);
CREATE INDEX followee_index ON follows (deleted_at, followee_id);
CREATE INDEX follow_index ON follows (deleted_at, follower_id, followee_id);





CREATE TABLE favorites (
  id BIGSERIAL PRIMARY KEY,
  tweet_id BIGINT NOT NULL REFERENCES tweets(id),
  user_id BIGINT NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL default CURRENT_TIMESTAMP,
  deleted_at timestamptz
);
CREATE INDEX fav_tweet_index ON favorites (deleted_at, tweet_id);