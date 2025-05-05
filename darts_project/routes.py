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
            db.execute('INSERT INTO games (date_time, hometeam_id, awayteam_id, hometeam_singles_score, awayteam_singles_score, hometeam_doubles_score, awayteam_doubles_score) VALUES (?, ?, ?, ?, ?, ?, ?)', (date_time, home_teamname, away_teamname, hometeam_score_singles, away_teamscore_singles, home_teamscore_doubles, away_teamscore_doubles))
            db.commit()
            return redirect(url_for('index'))
        
    return render_template('games.html', team_data=team_data)

#@app.route('/admin/games', methods=('GET', 'POST'))