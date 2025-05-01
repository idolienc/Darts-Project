DROP TABLE IF EXISTS league;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;

CREATE TABLE league (
    league_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id REFERENCES teams (team_id),
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0
);

CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time DATE NOT NULL,
    hometeam_id REFERENCES teams (team_id),
    awayteam_id REFERENCES teams (team_id),
    hometeam_singles_score INTEGER NOT NULL,
    awayteam_singles_score INTEGER NOT NULL,
    hometeam_doubles_score INTEGER NOT NULL,
    awayteam_doubles_score INTEGER NOT NULL
);

CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teamname VARCHAR(50)
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id REFERENCES teams (team_id),
    playername TEXT NOT NULL
);