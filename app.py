import os
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
    # url_has_allowed_host_and_scheme,
    abort,
    # url_for,
)

# from flask_debugtoolbar import DebugToolbarExtension
# from flask_login import LoginManager, login_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message

load_dotenv()

CURR_USER_KEY = 'curr_user'
DEFAULT_IMAGE_URL = '/static/images/default-pic.png'
DEFAULT_HEADER_IMAGE_URL = '/static/images/warbler-hero.jpg'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# toolbar = DebugToolbarExtension(app)
csrf = CSRFProtect(app)

connect_db(app)

# login_manager = LoginManager()
# login_manager.init_app(app)


##############################################################################
# User signup/login/logout


# @login_manager.user_loader
# def load_user(user_id):
#     '''Reloads the user object from the user ID stored in the session.'''

#     return User.query.get(user_id)


@app.before_request
def add_user_to_g():
    '''If we're logged in, add curr user to Flask global.'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    '''Log in user.'''

    session[CURR_USER_KEY] = user.id


def do_logout():
    '''Log out user.'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    '''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     '''Handle user login and redirect to homepage on success.'''

#     form = LoginForm()

#     if form.validate_on_submit():

#         user = User.authenticate(
#             form.username.data,
#             form.password.data)

#         if user:
#             # log in the user with flask-login
#             login_user(user)
#             flash(f'Hello, {user.username}!', 'success')

#             # get next parameter from the request args
#             # next = request.args.get('next')

#             # check if next parameter is safe for redirects
#             # if not url_has_allowed_host_and_scheme(next, request.host):
#             #     return abort(400)

#             # redirect to home page
#             return redirect('/')

#         flash('Invalid credentials.', 'danger')

#     return render_template('users/login.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Handle user login and redirect to homepage on success.'''

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(
            form.username.data,
            form.password.data)

        if user:
            do_login(user)
            flash(f'Hello, {user.username}!', 'success')
            return redirect('/')

        flash('Invalid credentials.', 'danger')

    return render_template('users/login.html', form=form)


@app.post('/logout')
def logout():

    if g.user:
        do_logout()
        flash('Success, you logged out!', 'success')
        return redirect('/login')

    flash('Logout attempt failed.', 'error')
    return redirect('/home')


##############################################################################
# General user routes:


@app.get('/users')
def list_users():
    '''Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    '''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f'%{search}%')).all()

    form = FlaskForm()

    return render_template('users/index.html', users=users, form=form)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    '''Show user profile.'''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    form = FlaskForm()

    return render_template('users/show.html', user=user, form=form)


@app.get('/users/<int:user_id>/following')
def show_following(user_id):
    '''Show list of people this user is following.'''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    form = FlaskForm()

    return render_template('users/following.html', user=user, form=form)


@app.get('/users/<int:user_id>/followers')
def show_followers(user_id):
    '''Show list of followers of this user.'''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    form = FlaskForm()

    return render_template('users/followers.html', user=user, form=form)


@app.post('/users/follow/<int:follow_id>')
def start_following(follow_id):
    '''Add a follow for the currently-logged-in user.

    Redirect to following page for the current for the current user.
    '''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f'/users/{g.user.id}/following')


@app.post('/users/stop-following/<int:follow_id>')
def stop_following(follow_id):
    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    followed_user = User.query.get(follow_id)
    if followed_user in g.user.following:
        g.user.following.remove(followed_user)
        db.session.commit()

    return redirect(f'/users/{g.user.id}/following')


@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    '''Update profile for current user.'''

    user = g.user

    if not user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    form = UserEditForm(obj=user)

    if form.validate_on_submit():

        if User.authenticate(user.username, form.password.data):
            user.email = form.email.data
            user.username = form.username.data
            user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
            user.header_image_url = form.header_image_url.data or DEFAULT_HEADER_IMAGE_URL
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            return redirect(f'/users/{user.id}')

        else:
            flash('Incorrect password.')

    return render_template('users/edit.html', form=form)


@app.post('/users/delete')
def delete_user():
    '''Delete user.

    Redirect to signup page.
    '''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    do_logout()

    Message.query.filter_by(user_id=g.user.id).delete()
    db.session.delete(g.user)
    db.session.commit()

    return redirect('/signup')


@app.get('/users/<int:user_id>/likes')
def show_liked_messages(user_id):
    '''Shows likes page for given user'''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    form = FlaskForm()

    return render_template('/users/likes.html', user=user, form=form)


@app.post('/messages/<int:message_id>/like')
def toggle_like_message(message_id):
    '''Adds or removes a message from a user's liked messages.

    Redirects to user likes page
    '''

    form = FlaskForm()

    if not g.user or not form.validate_on_submit():
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    liked_message = Message.query.get_or_404(message_id)

    if liked_message not in g.user.liked_messages:
        g.user.liked_messages.insert(0, liked_message)
    else:
        g.user.liked_messages.remove(liked_message)

    db.session.commit()

    return redirect(f'/users/{g.user.id}/likes')


##############################################################################
# Messages routes:


@app.route('/messages/new', methods=['GET', 'POST'])
def add_message():
    '''Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    '''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f'/users/{g.user.id}')

    return render_template('messages/create.html', form=form)


@app.get('/messages/<int:message_id>')
def show_message(message_id):
    '''Show a message.'''

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    form = FlaskForm()

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg, form=form)


@app.post('/messages/<int:message_id>/delete')
def delete_message(message_id):
    '''Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    '''

    msg = Message.query.get_or_404(message_id)

    if not g.user or g.user.id != msg.user_id:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    db.session.delete(msg)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')


##############################################################################
# Homepage and error pages


@app.get('/')
def homepage():
    '''Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    '''

    if g.user:

        homepage_ids = [user.id for user in g.user.following] + [g.user.id]

        messages = (Message
                    .query
                    .filter(Message.user_id.in_(homepage_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        form = FlaskForm()

        return render_template('home.html', messages=messages, form=form)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(response):
    '''Add non-caching headers on every request.'''

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
