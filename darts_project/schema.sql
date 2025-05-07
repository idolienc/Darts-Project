DROP TABLE IF EXISTS seasons;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;

CREATE TABLE seasons (
    season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    starting_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time DATE NOT NULL,
    hometeam_id REFERENCES teams (team_id),
    awayteam_id REFERENCES teams (team_id),
    hometeam_singles_legs INTEGER NOT NULL,
    awayteam_singles_legs INTEGER NOT NULL,
    hometeam_doubles_legs INTEGER NOT NULL,
    awayteam_doubles_legs INTEGER NOT NULL
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