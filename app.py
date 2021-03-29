from flask import Flask, g, session, json, render_template, request, redirect, url_for, abort, flash, get_flashed_messages
import chatter_classes as cc, sqlite3, os

app = Flask(__name__)

app.config.from_object(__name__)

app.config.update(
    {
        'DATABASE': os.path.join(app.root_path, 'test.db'),
        'SECRET_KEY': '123456' # TODO: Change secret key
    }
)

def get_db():

    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


def get_active_user() -> cc.User:
    try:
        return cc.User(session['active_userid'], get_db())
    except KeyError:
        return None

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/message/<int:messageid>')
def show_message(messageid):

    au = get_active_user()

    if au:

        m = cc.Message(messageid, get_db())

        if m.chatroom.user_is_owner(au) or \
            m.chatroom.user_is_member(au):

            html = f"<h1>Message from {m.sender.username}</h1>" \
                   f"<p>{m.content}</p>" \
                   f"<p>Sent: {m.timestamp.isoformat()}</p>"

            return html
        else:
            return 'You cannot see this message'

    else:
        return 'You must be logged in to see this!'

@app.route('/login', methods=['GET', 'POST'])
def login():

    '''active_user = cc.User.authenticate('TestUser1', 'pass1234', get_db())

    session['active_userid'] = active_user.userid

    return str(active_user.userid)'''

    if request.method == "GET":
        return render_template('login.html')
    else:
        # Process the login

        username = request.form['username']
        password = request.form['password']

        try:
            active_user = cc.User.authenticate(username, password, get_db())
            session['active_userid'] = active_user.userid
            return "Login successful! Welcome " + active_user.username

        except cc.UserAuthenticationError:
            flash("Invalid login details")
            return render_template('login.html')



@app.route('/logout')
def logout():

    if get_active_user():
        del session['active_userid']

    return 'Logged out'


@app.route('/view/chatroom/list')
def view_chatroom_list():
    au = get_active_user()
    if au:
        return render_template('show_chatrooms.html', au=au)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
