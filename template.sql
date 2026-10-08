PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    created_at TEXT DEFAULT (DATETIME('now', '+3 hours')),
    about TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS global (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    user_id INTEGER PRIMARY KEY NOT NULL,
    joined_at TEXT,
    trusted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS votebans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    message_id INTEGER,
    target_id INTEGER NOT NULL,
    target_link TEXT NOT NULL,
    initiator_link TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    mute_at TEXT NOT NULL,
    muted INTEGER NOT NULL DEFAULT 0,
    extended INTEGER NOT NULL DEFAULT 0,
    closed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS voteban_votes (
    voteban_id INTEGER NOT NULL REFERENCES votebans(id) ON DELETE CASCADE,
    voter_id INTEGER NOT NULL,
    vote INTEGER NOT NULL,
    PRIMARY KEY (voteban_id, voter_id)
);

INSERT OR IGNORE INTO global (key, value) VALUES ('model', 'qwen/qwen3.6-27b')
