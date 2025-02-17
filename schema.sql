CREATE TABLE IF NOT EXISTS clash (
    id SERIAL,
    clashname VARCHAR(255) NOT NULL,
    optin BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    code int,
    clan_tag VARCHAR(255),
    clan VARCHAR(255) DEFAULT 0,
    terms boolean DEFAULT FALSE,
    phone VARCHAR(255),
    enemy_clan VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS war (
    id SERIAL PRIMARY KEY,
    war_start TIMESTAMP NOT NULL,
    triggered BOOLEAN DEFAULT FALSE

);