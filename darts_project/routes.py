# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from darts_project import app
from darts_project.db import get_db

# When flask recieves this request, it will call the index function
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/teams', methods=('GET', 'POST'))
def adminteams():
    if '_flashes' in session:
        session['_flashes'].clear()
    if request.method == 'POST':
        teamname = request.form['teamname']
        error = None

        if not teamname:
            error = 'Team name is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO teams (teamname) VALUES (?)', (teamname,))
            db.commit()
            return redirect(url_for('teams'))
        
    return render_template('teams.html')

@app.route('/admin/games', methods=('GET', 'POST'))
def admingames():
    db = get_db()
    cursor = db.cursor()
    teamres = cursor.execute('SELECT team_id, teamname FROM teams')
    team_data = [{'team_id':team_id, 'teamname':teamname} for team_id, teamname in teamres]
    playerres = cursor.execute('SELECT player_id, playername FROM players')
    player_data = [{'player_id':player_id, 'playername':playername} for player_id, playername in playerres]
    if '_flashes' in session:
        session['_flashes'].clear()
    if request.method == 'POST':
        date_time = request.form['date_time']
        home_teamname = request.form['home_teamid']
        away_teamname = request.form['away_teamid']
        home_players = [request.form[f"home_player{i}"] for i in range(1, 10) if f"home_player{i}" in request.form]
        away_players = [request.form[f"away_player{i}"] for i in range(1, 10) if f"away_player{i}" in request.form]
        home_players_score = [request.form[f"home_player{i}_score"] for i in range(1,10) if f"home_player{i}_score" in request.form]
        away_players_score = [request.form[f"away_player{i}_score"] for i in range(1,10) if f"away_player{i}_score" in request.form]

        season_row = db.execute('SELECT season_id FROM seasons WHERE ? BETWEEN starting_date AND end_date', (date_time,)).fetchone()
        if season_row:
            season_id = season_row['season_id']  # Extract the scalar value
        else:
            season_id = None

        error = None
        if not date_time:
            error = 'Date is required.'
        if not home_teamname:
            error = 'Home Team is required.'
        if not away_teamname:
            error = 'Away Team is required.'
        if len(home_players) != 9:
            error = 'Home players must be filled in.'
        if len(away_players) != 9:
            error = 'Away players must be filled in.'
        if len(home_players_score) != 9:
            error = 'Home players scores must be filled in.'
        if len(away_players_score) != 9:
            error = 'Away players scores must be filled in.'
        if home_teamname == away_teamname:
            error = 'Home team and away team cannot be the same.'
        if not season_id:
            error = 'No matching season found for the provided date.'
        if error is not None:
            flash(error)
        else:
            matchnight = db.execute('INSERT INTO matchnights (date_time, season_id, hometeam_id, awayteam_id) VALUES (?, ?, ?, ?)', (date_time, season_id, home_teamname, away_teamname))
            matchnight_id = matchnight.lastrowid
            for x in range(9):
                home_playerid = home_players[x]
                away_playerid = away_players[x]
                home_score = home_players_score[x]
                away_score = away_players_score[x]
                if home_playerid and away_playerid and home_score and away_score:
                    db.execute('INSERT INTO games (matchnight_id, game_type, home_player_id, away_player_id, home_score, away_score) VALUES (?, ?, ?, ?, ?, ?)', (matchnight_id, 'singles', home_playerid, away_playerid, home_score, away_score))
            db.commit()
            return redirect(url_for('admingames'))
        
    return render_template('games.html', team_data=team_data, player_data=player_data)

@app.route('/admin/players', methods=('GET', 'POST'))
def adminplayers():
    db = get_db()
    cursor = db.cursor()
    res = cursor.execute('SELECT team_id, teamname FROM teams')
    team_data = [{'team_id':team_id, 'teamname':teamname} for team_id, teamname in res]
    if '_flashes' in session:
        session['_flashes'].clear()

    if request.method == 'POST':
        player_name = request.form['playername']
        team_id = request.form['team_id']
        error = None

        if not player_name:
            error = 'Player name is required.'
        if not team_id:
            error = 'Team is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO players (team_id, playername) VALUES (?, ?)', (team_id, player_name))
            db.commit()
            return redirect(url_for('players'))
        
    return render_template('players.html', team_data=team_data)

@app.route('/singlesleaguetable')
def singlesleaguetable():
    db = get_db()

    query = """
        WITH match_results AS (
        SELECT
            mn.matchnight_id,
            mn.hometeam_id,
            mn.awayteam_id,
            SUM(CASE WHEN g.home_score > g.away_score THEN 1 ELSE 0 END) AS home_games_won,
            SUM(CASE WHEN g.away_score > g.home_score THEN 1 ELSE 0 END) AS away_games_won
        FROM matchnights mn
        LEFT JOIN games g ON mn.matchnight_id = g.matchnight_id
        GROUP BY mn.matchnight_id
    ),
    team_stats AS (
        SELECT
            t.team_id,
            t.teamname,
            COUNT(DISTINCT mn.matchnight_id) AS matches_played,
            SUM(CASE
                WHEN t.team_id = mn.hometeam_id AND COALESCE(mr.home_games_won, 0) > COALESCE(mr.away_games_won, 0) THEN 1
                WHEN t.team_id = mn.awayteam_id AND COALESCE(mr.away_games_won, 0) > COALESCE(mr.home_games_won, 0) THEN 1
                ELSE 0
            END) AS matches_won,
            SUM(CASE
                WHEN t.team_id = mn.hometeam_id AND COALESCE(mr.home_games_won, 0) < COALESCE(mr.away_games_won, 0) THEN 1
                WHEN t.team_id = mn.awayteam_id AND COALESCE(mr.away_games_won, 0) < COALESCE(mr.home_games_won, 0) THEN 1
                ELSE 0
            END) AS matches_lost,
            SUM(CASE
                WHEN t.team_id = mn.hometeam_id THEN COALESCE(mr.home_games_won, 0)
                WHEN t.team_id = mn.awayteam_id THEN COALESCE(mr.away_games_won, 0)
                ELSE 0
            END) AS games_won,
            SUM(CASE
                WHEN t.team_id = mn.hometeam_id THEN COALESCE(mr.away_games_won, 0)
                WHEN t.team_id = mn.awayteam_id THEN COALESCE(mr.home_games_won, 0)
                ELSE 0
            END) AS games_lost,
            SUM(CASE
                WHEN t.team_id = mn.hometeam_id AND COALESCE(mr.home_games_won, 0) > COALESCE(mr.away_games_won, 0) THEN 3
                WHEN t.team_id = mn.awayteam_id AND COALESCE(mr.away_games_won, 0) > COALESCE(mr.home_games_won, 0) THEN 3
                ELSE 0
            END) AS bonus_points
        FROM teams t
        LEFT JOIN matchnights mn ON t.team_id IN (mn.hometeam_id, mn.awayteam_id)
        LEFT JOIN match_results mr ON mn.matchnight_id = mr.matchnight_id
        GROUP BY t.team_id, t.teamname
    ),
    final_table AS (
        SELECT
            teamname,
            matches_played,
            matches_won,
            matches_lost,
            games_won,
            games_lost,
            (games_won - games_lost) AS game_difference,
            bonus_points,
            (games_won + bonus_points) AS total_points
        FROM team_stats
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY total_points DESC, game_difference DESC, teamname) AS position,
        *
    FROM final_table
    ORDER BY position;
    """

    table = db.execute(query).fetchall()

    return render_template('singlesleaguetable.html', table=table)

@app.route('/doublesleaguetable')
def doublesleaguetable():
    db = get_db()
    cursor = db.cursor()
    query = """
    
    """

    doubles_table = db.execute(query).fetchall()
    return render_template('doublesleaguetable.html', doubles_table=doubles_table)