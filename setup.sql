CREATE TABLE IF NOT EXISTS PUBG_BOT (
    token   varchar(300)    not null,
    PUBG_API   varchar(300)    not null,
    KoreanBots_token   varchar(300)    null,
    topgg_token   varchar(300)    null,
    UniqueBots_token   varchar(300)    null
);
CREATE TABLE IF NOT EXISTS BLACKLIST (
    ID  bigint(20)  null
);
CREATE TABLE IF NOT EXISTS SERVER_INFO (
    id  bigint(20)  not null,
    prefix  varchar(30)  null
);
INSERT INTO PUBG_BOT(token, PUBG_API) value ('DISCORD BOT TOKEN', 'PUBG API TOKEN');

CREATE TABLE IF NOT EXISTS SERVER_DATA (
    id  bigint(2)   not null,
    date    datetime   null,
    data    bigint(10) null
);
CREATE TABLE IF NOT EXISTS SEASON_STATUS (
    Steam   json    null  default '{}',
    Kakao   json    null  default '{}',
    XBOX   json    null  default '{}',
    PSN   json    null  default '{}',
    Stadia   json    null  default '{}',
    last_update   json    null  default '{}',
    ID   tinyint(1)    null  default '{}'
);
CREATE TABLE IF NOT EXISTS matches (
    match_id   varchar(40) not null,
    match_data json    null    default '{}'
);
CREATE TABLE IF NOT EXISTS player_data (
    player_id   varchar(41) primary key,
    nickname varchar(100)    not null,
    season_date datetime default NOW() null,
    ranked_date datetime default NOW() null,
    platform tinyint(1) null default -1,
    matches_date datetime default NOW() null,
    matches_data json default '{}' null
);
CREATE TABLE IF NOT EXISTS season_stats (
    player_id   varchar(41) not null,
    player_data json    null    default '{}',
    season  varchar(50) null
);
CREATE TABLE IF NOT EXISTS ranked_stats (
    player_id   varchar(41) not null,
    player_data json    null    default '{}',
    season  varchar(50) null
);