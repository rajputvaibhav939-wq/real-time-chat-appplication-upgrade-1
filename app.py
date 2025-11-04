from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, send, emit
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)

# ----------------- APP SETUP -----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

users = {}

# ----------------- USER MODEL -----------------
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password


@login_manager.user_loader
def load_user(username):
    user = users.get(username)
    if user:
        return User(username, user['password'])
    return None


# ----------------- AUTH ROUTES -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "Username already exists! Try another."

        users[username] = {'password': password}
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user['password'] == password:
            login_user(User(username, password))
            return redirect(url_for('chat'))

        return "Invalid credentials!"

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ----------------- CHAT ROUTE -----------------
@app.route('/')
@login_required
def chat():
    return render_template('chat.html', username=current_user.id)


# ----------------- SOCKET EVENTS -----------------
@socketio.on('connect')
def user_connected():
    emit('message', f'{current_user.id} joined the chat!', broadcast=True)


@socketio.on('disconnect')
def user_disconnected():
    emit('message', f'{current_user.id} left the chat!', broadcast=True)


@socketio.on('message')
def handle_message(msg):
    # Include username and timestamp
    from datetime import datetime
    time = datetime.now().strftime('%H:%M:%S')
    full_msg = f"[{time}] {current_user.id}: {msg}"
    print(full_msg)
    send(full_msg, broadcast=True)


# ----------------- MAIN -----------------
if __name__ == '__main__':
    socketio.run(app, debug=True)