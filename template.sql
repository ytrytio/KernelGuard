PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    created_at TEXT DEFAULT (DATETIME('now', '+3 hours')),
    about TEXT DEFAULT ""
);
