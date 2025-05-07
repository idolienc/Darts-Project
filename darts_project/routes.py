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
            return redirect(url_for('index'))
        
    return render_template('teams.html')

@app.route('/admin/games', methods=('GET', 'POST'))
def admingames():
    db = get_db()
    cursor = db.cursor()
    res = cursor.execute('SELECT team_id, teamname FROM teams')
    team_data = [{'team_id':team_id, 'teamname':teamname} for team_id, teamname in res]
    if '_flashes' in session:
        session['_flashes'].clear()
    if request.method == 'POST':
        date_time = request.form['date_time']
        home_teamname = request.form['home_teamid']
        away_teamname = request.form['away_teamid']
        hometeam_score_singles = request.form['hometeam_score_singles']
        away_teamscore_singles = request.form['awayteam_score_singles']
        home_teamscore_doubles = request.form['hometeam_score_doubles']
        away_teamscore_doubles = request.form['awayteam_score_doubles']
        error = None

        if not date_time:
            error = 'Date is required.'
        if not home_teamname:
            error = 'Home Team is required.'
        if not away_teamname:
            error = 'Away Team is required.'
        if not hometeam_score_singles:
            error = 'Home Team Singles Score is required.'
        if not away_teamscore_singles:
            error = 'Away Team Singles Score is required.'
        if not home_teamscore_doubles:
            error = 'Home Team Doubles Score is required.'
        if not away_teamscore_doubles:
            error = 'Away Team Doubles Score is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO games (date_time, hometeam_id, awayteam_id, hometeam_singles_legs, awayteam_singles_legs, hometeam_doubles_legs, awayteam_doubles_legs) VALUES (?, ?, ?, ?, ?, ?, ?)', (date_time, home_teamname, away_teamname, hometeam_score_singles, away_teamscore_singles, home_teamscore_doubles, away_teamscore_doubles))
            db.commit()
            return redirect(url_for('index'))
        
    return render_template('games.html', team_data=team_data)

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
            return redirect(url_for('index'))
        
    return render_template('players.html', team_data=team_data)

@app.route('/leaguetable')
def leaguetable():
    db = get_db()
    cursor = db.cursor()
    query = """
    SELECT
        teams.team_id,
        teams.teamname,

        COALESCE(SUM(
            IF(games.hometeam_id = teams.team_id,
                games.hometeam_singles_legs + games.hometeam_doubles_legs,
                IF(games.awayteam_id = teams.team_id,
                    games.awayteam_singles_legs + games.awayteam_doubles_legs,
                    0)
            )
        ), 0) AS legs_won,

        COALESCE(SUM(
            IF(
                games.hometeam_id = teams.team_id
                AND (games.hometeam_singles_legs + games.hometeam_doubles_legs) > (games.awayteam_singles_legs + games.awayteam_doubles_legs),
                3,
                IF(
                    games.awayteam_id = teams.team_id
                    AND (games.awayteam_singles_legs + games.awayteam_doubles_legs) > (games.hometeam_singles_legs + games.hometeam_doubles_legs),
                    3,
                    0
                )
            )
        ), 0) AS match_points,

        COALESCE(SUM(
            IF(games.hometeam_id = teams.team_id,
                games.hometeam_singles_legs + games.hometeam_doubles_legs,
                IF(games.awayteam_id = teams.team_id,
                    games.awayteam_singles_legs + games.awayteam_doubles_legs,
                    0)
            )
        ), 0)
        +
        COALESCE(SUM(
            IF(
                games.hometeam_id = teams.team_id
                AND (games.hometeam_singles_legs + games.hometeam_doubles_legs) > (games.awayteam_singles_legs + games.awayteam_doubles_legs),
                3,
                IF(
                    games.awayteam_id = teams.team_id
                    AND (games.awayteam_singles_legs + games.awayteam_doubles_legs) > (games.hometeam_singles_legs + games.hometeam_doubles_legs),
                    3,
                    0
                )
            )
        ), 0) AS total_points

    FROM teams
    LEFT JOIN games ON teams.team_id = games.hometeam_id OR teams.team_id = games.awayteam_id
    GROUP BY teams.team_id, teams.teamname
    ORDER BY total_points DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    table_data = [dict(row) for row in rows]
    return render_template('leaguetable.html', table=table_data)