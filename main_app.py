# -*- coding: utf-8 -*-
"""
Created on Tue May 31 17:17:43 2022

@author: Group7
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from psycopg2 import connect

# Create the application instance
app = Flask(__name__,template_folder='templates')
app.secret_key = b'[\xb92G8\xcf\xba.I\xd1m\xb2\xf3\xea4\x93\xe5\xa0g\x93\x91\xbb\x81\xeb'

# Create a URL route in our application for "/" and other html pages
 
@app.route('/Signup', methods=('POST', 'GET'))
@app.route('/signup', methods=('POST', 'GET'))
def signup():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        error    = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email: 
            error = 'email is required.'
        else :
            myFile = open('dbConfig.txt')
            connStr = myFile.readline()
            conn = connect(connStr)
            cur = conn.cursor()
            cur.execute(
            'SELECT userid FROM sys_table WHERE username = %s', (username,))
            if cur.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                cur.close()
                conn.close()

        if error is None:
            cur.execute(
                'INSERT INTO sys_table (username, password, email) VALUES (%s, %s, %s)',
                (username, generate_password_hash(password), email)
            )
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

        flash(error)

     return render_template('signup.html')

 
@app.route('/Login', methods=('POST', 'GET'))
@app.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        conn = connect(connStr)
        cur = conn.cursor()
        error = None
        cur.execute(
            'SELECT * FROM sys_table WHERE username = %s', (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['userid'] = user[0]
            return redirect(url_for('home'))

        flash(error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('start'))


#@app.before_app_request
def load_logged_in_user():
    user_id = session.get('userid')

    if user_id is None:
        g.user = None
    else:
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        conn = connect(connStr)
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM sys_table WHERE userid = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
    if g.user is None:
        return False
    else: 
        return True
    
    

@app.route('/')
@app.route('/start')
def start():
    return render_template('start.html')

 
@app.route('/home')
def home():
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
    cur = conn.cursor()
    cur.execute(
            """SELECT sys_table.username, post.post_id, post.created, post.title, post.body 
               FROM sys_table, post WHERE  
                    sys_table.userid = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    load_logged_in_user()

    return render_template('home.html', posts=posts)

@app.route('/generic')
def generic():
     return render_template('generic.html')

@app.route('/elements')
def elements():
     return render_template('elements.html')

@app.route('/about_us')
def about_us():
     return render_template('about_us.html')
 

@app.route('/contact')
def contact():
    return render_template('contact.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
 app.run(debug=True)
