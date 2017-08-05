from flask import Flask, render_template, request, session, flash, redirect, url_for
import psycopg2
# from psycopg2.extensions import parse_dsn
from wtforms import Form, TextField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
# from reg_confirm import generete_token
import os


app = Flask(__name__)
# config  Postgresql
conn = psycopg2.connect(os.environ['PSQL_DSN'])
# secret key
app.secret_key = os.environ['SECRET_KEY']
app.security_key = os.environ['SECURITY_KEY']
# debug
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


# Register Form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=1, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match!')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = conn.cursor()

        try:
            # execute save user register info
            cur.execute("INSERT INTO users(name,username,email,password) VALUES(%s, %s, %s, %s)", (name, username, email, password))
            conn.commit()
            # close connect
            cur.close()
            flash('You are now register adn can log in!!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            conn.rollback()
            # cur.close()
            flash('The username is be registerd!', 'warning')
        # token = generete_token(email)

    return render_template('register.html', form=form)


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form field
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor
        cur = conn.cursor()
        cur.execute("SELECT username,password FROM users WHERE username = '{}';".format(username))
        data = cur.fetchone()
        print(data)
        if data:
            password = data[1]
            print(type(password))
            if sha256_crypt.verify(password_candidate, password):
                # app.logger.info("PASSWORD MATCH!")
                session['logged_in'] = True
                session['username'] = username
                flash('You are login in!', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid login'
                # app.logger.info("NO USER!")
                return render_template('login.html', error=error)
            # close sursor
            cur.close()
        else:
            error = 'User not found!'
            # app.logger.info("NO USER!")
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are logout', 'success')
    return redirect(url_for('login'))


def check_login(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('Unauthorized login!', 'danger')
            return redirect(url_for('login'))
    return wrap


# Dashboard
@app.route('/dashboard')
@check_login
def dashboard():
    return render_template('dashboard.html')


@app.route('/articles')
@check_login
def articles():
    return render_template('articles.html')


if __name__ == '__main__':
    app.run()
