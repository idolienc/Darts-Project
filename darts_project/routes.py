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
            return redirect(url_for('games'))
        
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
            return redirect(url_for('players'))
        
    return render_template('players.html', team_data=team_data)

@app.route('/singlesleaguetable')
def singlesleaguetable():
    db = get_db()
    cursor = db.cursor()
    query = """
    WITH match_results AS (
    SELECT 
        mn.matchnight_id,
        mn.hometeam_id,
        mn.awayteam_id,
        SUM(CASE WHEN l.home_score > l.away_score THEN 1 ELSE 0 END) AS home_games_won,
        SUM(CASE WHEN l.away_score > l.home_score THEN 1 ELSE 0 END) AS away_games_won
    FROM matchnights mn
    JOIN games g ON g.matchnight_id = mn.matchnight_id
    JOIN legs l ON l.game_id = g.game_id
    WHERE g.game_type = 'singles'
    GROUP BY mn.matchnight_id
),
team_summary AS (
    SELECT 
        t.team_id,
        t.teamname,
        -- Matchnights Played
        (SELECT COUNT(*) FROM match_results mr 
         WHERE mr.hometeam_id = t.team_id OR mr.awayteam_id = t.team_id) AS played,

        -- Matchnights Won
        (SELECT COUNT(*) FROM match_results mr 
         WHERE (mr.hometeam_id = t.team_id AND mr.home_games_won >= 5)
            OR (mr.awayteam_id = t.team_id AND mr.away_games_won >= 5)) AS won,

        -- Matchnights Lost
        (SELECT COUNT(*) FROM match_results mr 
         WHERE (mr.hometeam_id = t.team_id AND mr.home_games_won < 5)
            OR (mr.awayteam_id = t.team_id AND mr.away_games_won < 5)) AS lost,

        -- Games For
        (SELECT SUM(CASE WHEN mr.hometeam_id = t.team_id THEN mr.home_games_won
                         WHEN mr.awayteam_id = t.team_id THEN mr.away_games_won
                    END)
         FROM match_results mr) AS games_for,

        -- Games Against
        (SELECT SUM(CASE WHEN mr.hometeam_id = t.team_id THEN mr.away_games_won
                         WHEN mr.awayteam_id = t.team_id THEN mr.home_games_won
                    END)
         FROM match_results mr) AS games_against
    FROM teams t
),
final_table AS (
    SELECT 
        team_id,
        teamname,
        played,
        won,
        lost,
        games_for,
        games_against,
        (games_for - games_against) AS game_diff,
        (won * 3) AS bonus_points,
        (games_for + (won * 3)) AS points
    FROM team_summary
)
SELECT * FROM final_table
ORDER BY points DESC, game_diff DESC;
    """

    singles_table = db.execute(query).fetchall()
    return render_template('singlesleaguetable.html', singles_table=singles_table,)

@app.route('/doublesleaguetable')
def doublesleaguetable():
    db = get_db()
    cursor = db.cursor()
    query = """
    
    """

    doubles_table = db.execute(query).fetchall()
    return render_template('doublesleaguetable.html', doubles_table=doubles_table)