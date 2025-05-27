DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS matchnights;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS seasons;

CREATE TABLE seasons (
    season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    starting_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teamname VARCHAR(50)
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER REFERENCES teams (team_id),
    playername TEXT NOT NULL
);

CREATE TABLE matchnights (
    matchnight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time DATE NOT NULL,
    season_id INTEGER REFERENCES seasons (season_id),
    hometeam_id INTEGER REFERENCES teams (team_id),
    awayteam_id INTEGER REFERENCES teams (team_id)
);

CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    matchnight_id INTEGER REFERENCES matchnights (matchnight_id),
    game_type INTEGER, 
    home_player_id INTEGER REFERENCES players (player_id),
    away_player_id INTEGER REFERENCES players (player_id),
    home_score INTEGER,
    away_score INTEGER
);


