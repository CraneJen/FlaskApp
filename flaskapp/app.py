from flask import Flask, render_template, request, session, flash, redirect, url_for
import psycopg2
# from psycopg2.extensions import parse_dsn
from wtforms import Form, TextField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
import os


app = Flask(__name__)
# config  Postgresql
conn = psycopg2.connect(os.environ['PSQL_DSN'])
# secret key
app.secret_key = os.environ['SECRET_KEY']
# debug
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=1, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match!')
    ])
    confirm = PasswordField('Confirm Password')


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

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run()
