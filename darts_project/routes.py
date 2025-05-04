# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from darts_project import app
from darts_project.db import get_db

# When flask recieves this request, it will call the index function
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=('GET', 'POST'))
def admin():
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
        
    return render_template('admin.html')

#@app.route('/admin/games', methods=('GET', 'POST'))