import os
import secrets
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from sqlalchemy import func

# Initialize Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Secret key
app.secret_key = "ssshasd572332762332"

# -----------------------------
# Database configuration
# -----------------------------
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")  # default to SQLite

if DB_TYPE == "mysql":
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "pythonproject")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    # Local SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'myapp_'

db = SQLAlchemy(app)

# -----------------------------
# Models
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    check_in = db.Column(db.String(20), nullable=False)
    check_out = db.Column(db.String(20), nullable=False)
    no_of_guests = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(120), nullable=False)

# -----------------------------
# Forms
# -----------------------------
class CreateRoomForm(FlaskForm):
    room_name = StringField('Room Name', validators=[DataRequired()])
    room_type = StringField('Room Type', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    room_image = FileField('Room Image', validators=[DataRequired()])

# -----------------------------
# Upload folder config
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -----------------------------
# Initialize DB and session
# -----------------------------
with app.app_context():
    db.create_all()  # Only runs if database/tables don't exist

Session(app)

@app.route('/')
def home():
    return redirect(url_for('user_login'))

# User login route
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # Consider using hashed passwords
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
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
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
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
            new_user = User(username=name, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('user_login'))
    return render_template('user/register.html', msg=msg)

# User Logout route
@app.route('/logout')
def user_logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('user_login'))

# Admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        account = AdminUser.query.filter_by(email=email).first()
        if account and check_password_hash(account.password, password):
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            session['email'] = account.email
            msg = 'Logged in successfully!'
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('admin/login.html', msg=msg)

# Admin registration route
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        existing_account = AdminUser.query.filter_by(email=email).first()

        if existing_account:
            msg = 'Account already exists!'
        elif not re.match(r'^[A-Za-z0-9]+$', name):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            msg = 'Invalid email address!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        elif password != confirm_password:
            msg = 'Passwords do not match!'
        else:
            hashed_password = generate_password_hash(password)
            new_admin = AdminUser(username=name, password=hashed_password, email=email)
            db.session.add(new_admin)
            db.session.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('admin_login'))
    return render_template('admin/register.html', msg=msg)

@app.route('/admin_logout')
def admin_logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('admin_login'))

# User index page
@app.route('/index')
def index():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_id = session.get('id')
    user = User.query.get(user_id)
    return render_template('user/index.html', username=session['username'], email=session['email'])

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    # Calculate dashboard statistics
    total_bookings = Booking.query.count()
    active_guests = Booking.query.filter_by(status='Confirmed').count()
    
    # Calculate occupancy rate (assuming you have total rooms - adjust as needed)
    total_rooms = 50  # Replace with your actual room count from Room.query.count()
    occupancy_rate = f"{int((active_guests / total_rooms) * 100)}%" if total_rooms > 0 else "0%"
    
    # Get recent bookings for the activity table
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_bookings=total_bookings,
                         active_guests=active_guests,
                         occupancy_rate=occupancy_rate,
                         recent_bookings=recent_bookings)

# Room Management Route
@app.route('/manage_rooms')
def manage_rooms():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/manage_rooms.html')

# Customer Deleting Route
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('manage_customers'))

# Customer Management Route
@app.route('/manage_customers')
def manage_customers():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    
    # Calculate customer statistics
    # New customers this month (you might want to add created_at field to User model)
    # For now, we'll use a placeholder
    new_customers = 0  # You can implement this when you add timestamp fields
    
    # Active customers (customers with confirmed bookings)
    active_customers = len(set([booking.email for booking in Booking.query.filter_by(status='Confirmed').all()]))
    
    return render_template('admin/manage_customers.html', 
                         users=users,
                         new_customers=new_customers,
                         active_customers=active_customers)

@app.route('/my_bookings')
def my_bookings():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_email = session['email']
    bookings = Booking.query.filter_by(email=user_email).all()
    return render_template('user/my_bookings.html', bookings=bookings, email=user_email, username=session['username'])

# Manage Bookings Route
@app.route('/manage_bookings')
def manage_bookings():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    bookings = Booking.query.all()
    return render_template('admin/manage_bookings.html', bookings=bookings)

@app.route('/confirm_booking/<int:booking_id>')
def confirm_booking(booking_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = 'Confirmed'
        db.session.commit()
        flash('Booking confirmed successfully!')
    else:
        flash('Booking not found!')
    return redirect(url_for('manage_bookings'))

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = 'Cancelled'
        db.session.commit()
        flash('Booking cancelled successfully!')
    else:
        flash('Booking not found!')
    return redirect(url_for('manage_bookings'))

@app.route('/create_room', methods=['POST'])
def create_room():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    form = CreateRoomForm()
    if form.validate_on_submit():
        room_image = form.room_image.data
        filename = secure_filename(room_image.filename)
        room_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_room = Room(name=form.room_name.data, type=form.room_type.data, price=form.price.data, image=filename)
        db.session.add(new_room)
        db.session.commit()
        return 'Room created successfully!'
    return 'Error creating room'

# Feedback Management Route
@app.route('/manage_feedback')
def manage_feedback():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
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
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    return render_template('user/rooms.html', username=session['username'])

# Room Management Route
@app.route('/nearby_places')
def nearby_places():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    return render_template('user/nearby_places.html', username=session['username'])

@app.route('/contact_us')
def contact_us():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    return render_template('user/contact_us.html', username=session['username'])

@app.route('/book_room_submit', methods=['POST'])
def book_room_submit():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_name = request.form['room_name']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        guests = request.form['guests']
        room_type = request.form['room_type']

        try:
            price = float(request.form['price'])
        except ValueError:
            flash("Invalid price format.")
            return redirect(url_for('rooms'))

        new_booking = Booking(
            name=name,
            email=email,
            room_name=room_name,
            check_in=check_in,
            check_out=check_out,
            no_of_guests=guests,
            room_type=room_type,
            price=price,
            status='Pending'
        )

        db.session.add(new_booking)
        db.session.commit()
        flash('Booking successful! Your booking is pending confirmation by the admin.')
        return redirect(url_for('index'))

    return redirect(url_for('rooms'))


@app.route('/book_room1')
def book_room1():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_id = session.get('id')
    account = User.query.get(user_id)
    return render_template('user/book_room1.html', username=session['username'], email=account.email)

# Rooms index page
@app.route('/book_room2')
def book_room2():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_id = session.get('id')
    account = User.query.get(user_id)
    return render_template('user/book_room2.html', username=session['username'], email=account.email)

# Rooms index page
@app.route('/book_room3')
def book_room3():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_id = session.get('id')
    account = User.query.get(user_id)
    return render_template('user/book_room3.html', username=session['username'], email=account.email)

@app.route('/profile')
def user_profile():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    user_id = session.get('id')
    account = User.query.get(user_id)
    return render_template('user/profile.html', username=account.username, email=account.email)

@app.route('/admin_profile')
def admin_profile():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/profile.html', username=session['username'])

# User forgot password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def user_forgot_password():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        account = User.query.filter_by(email=email).first()
        if account:
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
            account = User.query.filter_by(email=email).first()
            if account:
                account.password = generate_password_hash(new_password)
                db.session.commit()
                msg = 'Password successfully reset!'
                return redirect(url_for('user_login'))
    return render_template('user/reset_password.html', msg=msg, email=email)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    msg = ''
    user_id = session.get('id')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Validate username and email
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            msg = 'Invalid email address!'
        else:
            account = User.query.filter_by(email=email).filter(User.id != user_id).first()
            if account:
                msg = 'Email is already used by another account!'
            else:
                user = User.query.get(user_id)
                user.username = name
                user.email = email
                db.session.commit()
                msg = 'Profile updated successfully!'
                session['username'] = name
                session['email'] = email
    account = User.query.get(user_id)
    return render_template('user/profile.html', msg=msg, username=account.username, email=account.email)

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    msg = ''
    if request.method == 'POST':
        user_id = session['id']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password and confirm_password:
            if new_password != confirm_password:
                msg = 'Passwords do not match!'
            elif len(new_password) <= 8:
                msg = 'Password must be more than 8 characters.'
            else:
                user = User.query.get(user_id)
                user.password = generate_password_hash(new_password)
                db.session.commit()
                msg = 'Password updated successfully!'
    return render_template('user/profile.html', msg=msg)

@app.route('/admin_update_profile', methods=['GET', 'POST'])
def admin_update_profile():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    msg = ''
    if request.method == 'POST':
        user_id = session['id']
        name = request.form['name']
        email = request.form['email']
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            msg = 'Invalid email address!'
        else:
            admin = AdminUser.query.get(user_id)
            admin.username = name
            admin.email = email
            db.session.commit()
            msg = 'Profile updated successfully!'
            session['username'] = name
            session['email'] = email
    else:
        user_id = session['id']
        admin = AdminUser.query.get(user_id)
        return render_template('admin/profile.html', username=admin.username, email=admin.email, msg=msg)
    return render_template('admin/profile.html', username=session['username'], email=session['email'], msg=msg)

@app.route('/admin_update_password', methods=['GET', 'POST'])
def admin_update_password():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    msg = ''
    if request.method == 'POST':
        user_id = session['id']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password and confirm_password:
            if new_password != confirm_password:
                msg = 'Passwords do not match!'
            elif len(new_password) <= 8:
                msg = 'Password must be more than 8 characters.'
            else:
                admin = AdminUser.query.get(user_id)
                admin.password = generate_password_hash(new_password)
                db.session.commit()
                msg = 'Password updated successfully!'
    return render_template('admin/profile.html', msg=msg)

if __name__ == "__main__":
    app.run(debug=True)