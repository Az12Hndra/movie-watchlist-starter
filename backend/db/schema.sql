-- users table, consist of id, username, email, password, 

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- uses autoincrement to add more users automatically
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY, -- doesn't need autoincrement because the amount of movies is determined
    title TEXT NOT NULL,
    year INT NOT NULL,
    director TEXT NOT NULL, 
    genres TEXT NOT NULL,
    rating REAL NOT NULL CHECK (rating BETWEEN 0 AND 10),
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    synopsis TEXT NOT NULL,
    poster_url TEXT NOT NULL,
    cast_members TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watchlists (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE RESTRICT,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review TEXT CHECK (length(review) <= 2000),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, movie_id)
);