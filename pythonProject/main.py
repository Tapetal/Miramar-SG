import os
import secrets
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from flask_session import Session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired
import re

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuration
app.secret_key = "ssshasd572332762332"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "pythonproject"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Initialize MySQL and Session
mysql = MySQL(app)
Session(app)

@app.route('/')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        account = cursor.fetchone()

        if account and account['Password'] == password:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['Username']
            session['email'] = account['Email']  # Add this line to store email in session
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect email or password!'
    return render_template('user/login.html', msg=msg)



# User registration route
@app.route('/register', methods=['GET', 'POST'])
def user_register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'^[A-Za-z0-9]+$', name):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            msg = 'Invalid email address!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        elif password != confirm_password:
            msg = 'Passwords do not match!'
        elif len(password) <= 8:
            msg = 'Password must be more than 8 characters.'
        else:
            cursor.execute('INSERT INTO users (Username, Password, Email) VALUES (%s, %s, %s)', (name, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('user_login'))
    return render_template('user/register.html', msg=msg)


# User Logout route
@app.route('/logout')
def user_logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('Username', None)
    return redirect(url_for('user_login'))

# User login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin_users WHERE Email = % s AND Password = % s', (email, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['Username']
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('admin/login.html', msg=msg)

# User registration route
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin_users WHERE Email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        elif password != confirm_password:
            msg = 'Passwords do not match!'
        else:
            cursor.execute('INSERT INTO admin_users (Username, Password, Email) VALUES (%s, %s, %s)',(name, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('user_login'))
    return render_template('admin/login.html', msg=msg)

@app.route('/admin_logout')
def admin_logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('Username', None)
    return redirect(url_for('admin_login'))

# User index page
@app.route('/index')
def index():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    return render_template('user/index.html', username=session['username'], email=session['email'])

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

# Room Management Route
@app.route('/manage_rooms')
def manage_rooms():
    return render_template('admin/manage_rooms.html')

# Customer Deleting Route
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    mysql.connection.commit()
    return redirect(url_for('manage_customers'))

# Customer Management Route
@app.route('/manage_customers')
def manage_customers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('admin/customers.html', users=users)

@app.route('/my_bookings')
def my_bookings():
    if 'email' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_email = session['email']  # Get the logged-in user's email from the session
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Query to fetch only the logged-in user's bookings
    cursor.execute('SELECT * FROM bookings WHERE email = %s', (user_email,))
    bookings = cursor.fetchall()

    return render_template('user/my_bookings.html', bookings=bookings, email=user_email)



# Manage Bookings Route
@app.route('/manage_bookings')
def manage_bookings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    return render_template('admin/manage_bookings.html', bookings=bookings)

@app.route('/confirm_booking/<int:booking_id>')
def confirm_booking(booking_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', ('Confirmed', booking_id))
        mysql.connection.commit()
        flash('Booking confirmed successfully!')
        return redirect(url_for('manage_bookings'))
    except Exception as e:
        flash('Error confirming booking: {}'.format(e))
        return redirect(url_for('manage_bookings'))

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', ('Canceled', booking_id))
        mysql.connection.commit()
        flash('Booking canceled!')
        return redirect(url_for('manage_bookings'))
    except Exception as e:
        flash('Error canceling booking: {}'.format(e))
        return redirect(url_for('manage_bookings'))

class CreateRoomForm(FlaskForm):
    room_name = StringField('Room Name', validators=[DataRequired()])
    room_type = StringField('Room Type', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    room_image = FileField('Room Image', validators=[DataRequired()])
@app.route('/create_room', methods=['POST'])
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        # Get the uploaded file
        room_image = form.room_image.data
        # Save the file to a directory on the server

        filename = secure_filename(room_image.filename)
        room_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Insert the new room into the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO rooms (name, type, price, image) VALUES (%s, %s, %s, %s)', (form.room_name.data, form.room_type.data, form.price.data, filename))
        mysql.connection.commit()
        # Return a success message or redirect to a success page
        return 'Room created successfully!'
    return 'Error creating room'

# Feedback Management Route
@app.route('/manage_feedback')
def manage_feedback():
    return render_template('admin/manage_feedback.html')

# Guest index page
@app.route('/guest')
def guest():
    return render_template('guest/guest.html')

# Guest rooms page
@app.route('/guest_rooms')
def guest_rooms():
    return render_template('guest/guest_rooms.html')

# Guest nearby places page
@app.route('/guest_nearby')
def guest_nearby():
    return render_template('guest/guest_nearby.html')

# Guest contact page
@app.route('/guest_contact')
def guest_contact():
    return render_template('guest/guest_contact.html')

# Rooms index page
@app.route('/rooms')
def rooms():
    return render_template('user/rooms.html',  username=session['username'])

# Room Management Route
@app.route('/nearby_places')
def nearby_places():
    return render_template('user/nearby_places.html',  username=session['username'])

@app.route('/contact_us')
def contact_us():
    return render_template('user/contact_us.html',  username=session['username'])

@app.route('/book_room_submit', methods=['POST'])
def book_room_submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_name = request.form['room_name']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        guests = request.form['guests']
        price = request.form['price']
        room_type = request.form['room_type']

        # Save data to database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO bookings (name, email, room_name, check_in, check_out, no_of_guests, room_type, price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, email, room_name, check_in, check_out, guests, room_type, price, 'Pending'))
        mysql.connection.commit()

        flash('Booking successful! Your booking is pending confirmation by the admin.')
        return redirect(url_for('index'))
    return redirect(url_for('rooms'))

@app.route('/book_room1')
def book_room1():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    return render_template('user/book_room1.html', username=session['username'], email=account['Email'])

# Rooms index page
@app.route('/book_room2')
def book_room2():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    return render_template('user/book_room2.html', username=session['username'], email=account['Email'])

# Rooms index page
@app.route('/book_room3')
def book_room3():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    return render_template('user/book_room3.html', username=session['username'], email=account['Email'])

@app.route('/profile')
def user_profile():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    return render_template('user/profile.html', username=account['Username'], email=account['Email'])

# Rooms index page
@app.route('/my_booking')
def my_booking():
    return render_template('user/my_bookings.html',  username=session['username'])

@app.route('/admin_profile')
def admin_profile():
    return render_template('admin/profile.html', username=session['username'])

# User forgot password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def user_forgot_password():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        account = cursor.fetchone()

        if account:
            # Directly redirect to reset password form
            return redirect(url_for('user_reset_password', email=email))
        else:
            msg = 'Email not found!'

    return render_template('user/forgot_password.html', msg=msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def user_reset_password():
    email = request.args.get('email')
    msg = ''

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            msg = 'Passwords do not match!'
        elif len(new_password) <= 8:
            msg = 'Password must be more than 8 characters.'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE users SET Password = %s WHERE Email = %s', (new_password, email))
            mysql.connection.commit()
            msg = 'Password successfully reset!'
            return redirect(url_for('user_login'))

    return render_template('user/forgot_password.html', msg=msg, email=email)


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    msg = ''
    user_id = session.get('id')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if username is valid
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            msg = 'Invalid email address!'
        else:
            # Check if email is already used by another account
            cursor.execute('SELECT * FROM users WHERE Email = %s AND id != %s', (email, user_id))
            account = cursor.fetchone()
            if account:
                msg = 'Email is already used by another account!'
            else:
                # Update the user details
                cursor.execute('UPDATE users SET Username = %s, Email = %s WHERE id = %s', (name, email, user_id))
                mysql.connection.commit()
                msg = 'Profile updated successfully!'

                # Update session variables
                session['username'] = name
                session['email'] = email

    # Fetch updated user details
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()

    return render_template('user/profile.html', msg=msg, username=account['Username'], email=account['Email'])




@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    msg = ''
    if request.method == 'POST':
        user_id = session['id']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if new_password and confirm_password:
            if new_password != confirm_password:
                msg = 'Passwords do not match!'
            elif len(new_password) <= 8:
                msg = 'Password must be more than 8 characters.'
            else:
                # Update the user password
                cursor.execute('UPDATE users SET Password = %s WHERE id = %s', (new_password, user_id))
                mysql.connection.commit()
                msg = 'Password updated successfully!'
    return render_template('user/profile.html', msg=msg)


@app.route('/admin_update_profile', methods=['GET', 'POST'])
def admin_update_profile():
    if 'loggedin' in session:
        msg = ''
        if request.method == 'POST':
            user_id = session['id']
            name = request.form['name']
            email = request.form['email']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check if username is valid
            if not re.match(r'^[a-zA-Z0-9]+$', name):
                msg = 'Username must contain only characters and numbers!'
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                msg = 'Invalid email address!'
            else:
                # Check if email is already used by another account
                cursor.execute('SELECT * FROM admin_users WHERE Email = %s AND id != %s', (email, user_id))
                account = cursor.fetchone()
                if account:
                    msg = 'Email is already used by another account!'
                else:
                    # Update the admin details
                    cursor.execute('UPDATE admin_users SET Username = %s, Email = %s WHERE id = %s', (name, email, user_id))
                    mysql.connection.commit()
                    msg = 'Profile updated successfully!'
                    session['username'] = name
                    session['email'] = email
        else:
            user_id = session['id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin_users WHERE id = %s', (user_id,))
            account = cursor.fetchone()
            return render_template('admin/profile.html', username=account['Username'], email=account['Email'], msg=msg)
        return render_template('admin/profile.html', username=session['username'], email=session['email'], msg=msg)
    return redirect(url_for('admin_login'))

@app.route('/admin_update_password', methods=['GET', 'POST'])
def admin_update_password():
    msg = ''
    if request.method == 'POST':
        user_id = session['id']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if new_password and confirm_password:
            if new_password != confirm_password:
                msg = 'Passwords do not match!'
            elif len(new_password) <= 8:
                msg = 'Password must be more than 8 characters.'
            else:
                # Update the admin password
                cursor.execute('UPDATE admin_users SET Password = %s WHERE id = %s', (new_password, user_id))
                mysql.connection.commit()
                msg = 'Password updated successfully!'
    return render_template('admin/profile.html', msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
