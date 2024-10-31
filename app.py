from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@socketio.on('message')
def handle_message(msg):
    username = session.get('username', 'Anonymous')
    full_message = f"{username}: {msg}"
    send(full_message, broadcast=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
