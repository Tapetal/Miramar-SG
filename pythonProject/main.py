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
from flask_migrate import Migrate


# Initialize Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Secret key
app.secret_key = os.environ.get("SECRET_KEY", "ssshasd572332762332")

# -----------------------------
# Database configuration - FIXED FOR RENDER
# -----------------------------
# Get DATABASE_URL from environment
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Running on Render with PostgreSQL
    # Fix postgres:// to postgresql:// for SQLAlchemy 1.4+ compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print(f"✅ Connected to PostgreSQL: {database_url.split('@')[1].split('/')[0]}")  # Log hostname only
else:
    # Local development with SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    print("✅ Using local SQLite database")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'myapp_'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    description = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    amenities = db.Column(db.Text, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# Forms
# -----------------------------
class CreateRoomForm(FlaskForm):
    room_name = StringField('Room Name', validators=[DataRequired()])
    room_type = StringField('Room Type', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    description = StringField('Description')
    room_image = FileField('Room Image', validators=[DataRequired()])

# -----------------------------
# Upload folder config
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.static_folder, 'admin', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -----------------------------
# Initialize DB and session
# -----------------------------
# Don't call db.create_all() here - it will run when importing the module
# Instead, we'll create tables on first request or via a separate command

Session(app)

@app.route('/')
def home():
    return redirect(url_for('user_login'))

# Initialize database tables (run this once after deployment)
@app.route('/init-db')
def init_db():
    try:
        db.create_all()
        return "✅ Database tables created successfully!"
    except Exception as e:
        return f"❌ Error creating tables: {str(e)}"

# User login route
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
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
    
    total_bookings = Booking.query.count()
    active_guests = Booking.query.filter_by(status='Confirmed').count()
    
    total_rooms = 50
    occupancy_rate = f"{int((active_guests / total_rooms) * 100)}%" if total_rooms > 0 else "0%"
    
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_bookings=total_bookings,
                         active_guests=active_guests,
                         occupancy_rate=occupancy_rate,
                         recent_bookings=recent_bookings)

@app.route('/manage_rooms')
def manage_rooms():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    rooms = Room.query.all()
    
    total_rooms = len(rooms)
    available_rooms = len([r for r in rooms if r.is_available])
    occupied_rooms = total_rooms - available_rooms
    avg_price = sum(r.price for r in rooms) / total_rooms if rooms else 0
    
    return render_template('admin/manage_rooms.html', 
                         rooms=rooms,
                         available_rooms=available_rooms,
                         occupied_rooms=occupied_rooms,
                         avg_price=f"{avg_price:.2f}")

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('manage_customers'))

@app.route('/manage_customers')
def manage_customers():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    
    new_customers = 0
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
    
    total_spent = sum(booking.price for booking in bookings if booking.status == 'Confirmed')
    
    return render_template('user/my_bookings.html', 
                         bookings=bookings, 
                         email=user_email, 
                         username=session['username'],
                         total_spent=total_spent)

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

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'loggedin' not in session:
        return {'success': False, 'message': 'Not logged in'}, 401
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.email != session['email']:
        return {'success': False, 'message': 'Unauthorized'}, 403
    
    if booking.status.lower() != 'pending':
        return {'success': False, 'message': 'Cannot cancel confirmed bookings'}, 400
    
    booking.status = 'Cancelled'
    db.session.commit()
    
    return {'success': True, 'message': 'Booking cancelled successfully'}

@app.route('/create_room', methods=['POST'])
def create_room():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        room_name = request.form.get('room_name')
        room_type = request.form.get('room_type')
        price = float(request.form.get('price'))
        capacity = int(request.form.get('capacity'))
        description = request.form.get('description', '')
        
        if 'room_image' not in request.files:
            flash('No file selected')
            return redirect(url_for('manage_rooms'))
        
        file = request.files['room_image']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('manage_rooms'))
        
        if file:
            filename = secure_filename(file.filename)
            filename = f"{int(datetime.now().timestamp())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_room = Room(
                name=room_name,
                type=room_type,
                price=price,
                capacity=capacity,
                description=description,
                image=filename
            )
            
            db.session.add(new_room)
            db.session.commit()
            flash('Room created successfully!')
            return redirect(url_for('manage_rooms'))
            
    except Exception as e:
        flash(f'Error creating room: {str(e)}')
        return redirect(url_for('manage_rooms'))

@app.route('/manage_feedback')
def manage_feedback():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/manage_feedback.html')

@app.route('/guest')
def guest():
    return render_template('guest/guest.html')

@app.route('/guest_rooms')
def guest_rooms():
    return render_template('guest/guest_rooms.html')

@app.route('/guest_nearby')
def guest_nearby():
    return render_template('guest/guest_nearby.html')

@app.route('/guest_contact')
def guest_contact():
    return render_template('guest/guest_contact.html')

@app.route('/rooms')
def rooms():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    
    rooms = Room.query.filter_by(is_available=True).all()
    return render_template('user/rooms.html', username=session['username'], rooms=rooms)

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

@app.route('/book_room/<int:room_id>')
def book_room(room_id):
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    
    room = Room.query.get_or_404(room_id)
    user_id = session.get('id')
    user = User.query.get(user_id)
    
    return render_template('user/book_room.html', 
                         room=room, 
                         username=session['username'], 
                         email=user.email)

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
        guests = int(request.form['guests'])
        room_type = request.form['room_type']

        try:
            price = float(request.form['price'])
        except ValueError:
            flash("Invalid price format.")
            return redirect(url_for('rooms'))

        room = Room.query.filter_by(name=room_name).first()
        if room and guests > room.capacity:
            flash(f"This room can accommodate maximum {room.capacity} guests.")
            return redirect(url_for('book_room', room_id=room.id))

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

@app.route('/delete_room/<int:room_id>')
def delete_room(room_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    room = Room.query.get_or_404(room_id)
    
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], room.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    except:
        pass
    
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully!')
    return redirect(url_for('manage_rooms'))

@app.route('/toggle_room_availability/<int:room_id>')
def toggle_room_availability(room_id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    room = Room.query.get_or_404(room_id)
    room.is_available = not room.is_available
    db.session.commit()
    
    status = "available" if room.is_available else "unavailable"
    flash(f'Room "{room.name}" is now {status}.')
    return redirect(url_for('manage_rooms'))

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)