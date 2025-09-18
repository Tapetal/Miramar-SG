# import secrets
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_mysqldb import MySQL
import re


def init_routes(app, mysql):
    app.secret_key = "ssshasd572332762332"
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = ""
    app.config['MYSQL_DB'] = "pythonproject"

    mysql.init_app(app)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    @app.route('/')
    # User login route

    @app.route('/login', methods=['GET', 'POST'])
    def user_login():
        msg = ''
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE Email = % s AND Password = % s', (email, password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['Username']
                msg = 'Logged in successfully !'
                return render_template('index.html', msg=msg)
            else:
                msg = 'Incorrect username / password !'
        return render_template('user/login.html', msg=msg)
    #
    # # User registration route
    # @app.route('/register', methods=['GET', 'POST'])
    # def user_register():
    #     msg = ''
    #     if request.method == 'POST':
    #         name = request.form['name']
    #         email = request.form['email']
    #         password = request.form['password']
    #         confirm_password = request.form['confirm_password']
    #
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #         cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
    #         account = cursor.fetchone()
    #
    #         if account:
    #             msg = 'Account already exists!'
    #         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
    #             msg = 'Invalid email address!'
    #         elif not re.match(r'[A-Za-z0-9]+', name):
    #             msg = 'Username must contain only characters and numbers!'
    #         elif not name or not password or not email:
    #             msg = 'Please fill out the form!'
    #         elif password != confirm_password:
    #             msg = 'Passwords do not match!'
    #         else:
    #             cursor.execute('INSERT INTO users (Username, Password, Email) VALUES (%s, %s, %s)',
    #                            (name, password, email))
    #             mysql.connection.commit()
    #             msg = 'You have successfully registered!'
    #             return redirect(url_for('user_login'))
    #
    #     return render_template('user/register.html', msg=msg)
    #
    # # Admin login route
    # @app.route('/admin_login', methods=['GET', 'POST'])
    # def admin_login():
    #     msg = ''
    #     if request.method == 'POST':
    #         email = request.form['email']
    #         password = request.form['password']
    #
    #         if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
    #             msg = 'Invalid email address!'
    #         elif len(password) <= 8:
    #             msg = 'Password must be more than 8 characters!'
    #         else:
    #             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #             cursor.execute('SELECT * FROM admin_users WHERE Email = %s AND Password = %s', (email, password))
    #             account = cursor.fetchone()
    #             if account:
    #                 session['loggedin'] = True
    #                 session['id'] = account['id']
    #                 session['Username'] = account['Username']
    #                 return redirect(url_for('admin_dashboard'))
    #             else:
    #                 msg = 'Incorrect email or password!'
    #     return render_template('admin/login.html', msg=msg)
    #
    # # Admin registration route
    # @app.route('/admin_register', methods=['GET', 'POST'])
    # def admin_register():
    #     msg = ''
    #     if request.method == 'POST':
    #         name = request.form['name']
    #         email = request.form['email']
    #         password = request.form['password']
    #         confirm_password = request.form['confirm_password']
    #
    #         if not re.match(r'^[a-zA-Z]+$', name):
    #             msg = 'Username should not contain digits.'
    #         elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
    #             msg = 'Invalid email address!'
    #         elif len(password) <= 8:
    #             msg = 'Password must be more than 8 characters.'
    #         elif password != confirm_password:
    #             msg = 'Passwords do not match.'
    #         else:
    #             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #             cursor.execute('SELECT * FROM admin_users WHERE Email = %s', (email,))
    #             account = cursor.fetchone()
    #             if account:
    #                 msg = 'Account already exists!'
    #             else:
    #                 cursor.execute('INSERT INTO admin_users (Username, Password, Email) VALUES (%s, %s, %s)',
    #                                (name, password, email))
    #                 mysql.connection.commit()
    #                 msg = 'You have successfully registered!'
    #                 return redirect(url_for('admin_login'))
    #     return render_template('admin/login.html', msg=msg)
    #
    # # User forgot password route
    # @app.route('/forgot_password', methods=['GET', 'POST'])
    # def user_forgot_password():
    #     msg = ''
    #     if request.method == 'POST':
    #         email = request.form['email']
    #
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #         cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
    #         account = cursor.fetchone()
    #
    #         if account:
    #             # Generate a token for password reset (you can store this in the database)
    #             token = secrets.token_urlsafe(16)
    #             cursor.execute('UPDATE users SET password_reset_token = %s WHERE Email = %s', (token, email))
    #             mysql.connection.commit()
    #
    #             # Redirect to the reset password page with the token
    #             return redirect(url_for('reset_password', token=token))
    #         else:
    #             msg = 'Email not found!'
    #
    #     return render_template('user/forgot_password.html', msg=msg)
    #
    # @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    # def user_reset_password(token):
    #     msg = ''
    #     if request.method == 'POST':
    #         new_password = request.form['new_password']
    #         confirm_password = request.form['confirm_password']
    #
    #         if new_password != confirm_password:
    #             msg = 'Passwords do not match!'
    #         elif len(new_password) <= 8:
    #             msg = 'Password must be more than 8 characters.'
    #         else:
    #             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #             cursor.execute(
    #                 'UPDATE users SET Password = %s, password_reset_token = NULL WHERE password_reset_token = %s',
    #                 (new_password, token))
    #             mysql.connection.commit()
    #             msg = 'Password successfully reset!'
    #             return redirect(url_for('user_login'))
    #
    #     return render_template('user/reset_password.html', msg=msg)
    #
    # # Admin forgot password route
    # @app.route('/admin_forgot_password', methods=['GET', 'POST'])
    # def admin_forgot_password():
    #     msg = ''
    #     title = 'Forgot Password'
    #     if request.method == 'POST':
    #         email = request.form['email']
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #         cursor.execute('SELECT * FROM admin_users WHERE Email = %s', (email,))
    #         account = cursor.fetchone()
    #
    #         if account:
    #             token = secrets.token_urlsafe(16)
    #             cursor.execute('UPDATE admin_users SET password_reset_token = %s WHERE Email = %s', (token, email))
    #             mysql.connection.commit()
    #             cursor.close()
    #             msg = 'Password reset link sent to your email!'
    #             # Here you would normally send an email with the reset link
    #         else:
    #             msg = 'Email not found!'
    #
    #     return render_template('admin/forgot_password.html', msg=msg, title=title, reset_password=False)
    #
    # @app.route('/admin_reset_password/<token>', methods=['GET', 'POST'])
    # def admin_reset_password(token):
    #     msg = ''
    #     title = 'Reset Password'
    #     if request.method == 'POST':
    #         new_password = request.form['new_password']
    #         confirm_password = request.form['confirm_password']
    #         if new_password != confirm_password:
    #             msg = 'Passwords do not match!'
    #         elif len(new_password) <= 8:
    #             msg = 'Password must be more than 8 characters.'
    #         else:
    #             cursor = mysql.connection.cursor()
    #             cursor.execute(
    #                 'UPDATE admin_users SET Password = %s, password_reset_token = NULL WHERE password_reset_token = %s',
    #                 (new_password, token))
    #             mysql.connection.commit()
    #             cursor.close()
    #             msg = 'Password successfully reset!'
    #             return redirect(url_for('admin_login'))
    #
    #     return render_template('admin/forgot_password.html', msg=msg, token=token, title=title, reset_password=True)
    #
    # # User index page
    # @app.route('/index')
    # def index():
    #     return render_template('user/index.html')
    #
    # # Admin dashboard
    # @app.route('/admin_dashboard')
    # def admin_dashboard():
    #     return render_template('admin/dashboard.html')
    #
    # # User Logout route
    # @app.route('/logout')
    # def user_logout():
    #     session.pop('loggedin', None)
    #     session.pop('id', None)
    #     session.pop('Username', None)
    #     return redirect(url_for('user_login'))
    #
    # # Admin Logout route
    # @app.route('/admin_logout')
    # def admin_logout():
    #     session.pop('loggedin', None)
    #     session.pop('id', None)
    #     session.pop('Username', None)
    #     return redirect(url_for('admin_login'))