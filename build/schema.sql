CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS games (
    id serial PRIMARY KEY
    , name text NOT NULL
    , version text NOT NULL
    , created_at timestamp DEFAULT CURRENT_TIMESTAMP
    , updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rules (
    id serial PRIMARY KEY
    , rule text NOT NULL
    , created_at timestamp DEFAULT CURRENT_TIMESTAMP
    , updated_at timestamp DEFAULT CURRENT_TIMESTAMP
    , embedding vector (384)
    , game_id integer
    , FOREIGN KEY (game_id) REFERENCES games (id)
);

