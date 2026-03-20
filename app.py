from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime, date
import os

# ────────────────────────────────────────────────
# APP INITIALIZATION (MOST IMPORTANT FIX)
# ────────────────────────────────────────────────
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.secret_key = os.environ.get('SECRET_KEY', 'shanvi-secret-123456')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shanvi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False   # ← only for local testing

db = SQLAlchemy(app)

# ────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ────────────────────────────────────────────────
# FORMS
# ────────────────────────────────────────────────
class BookingForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    event_type = SelectField('Event Type', choices=[
        ('Wedding', 'Wedding'), ('Birthday', 'Birthday'),
        ('Engagement', 'Engagement'), ('Corporate', 'Corporate'), ('Other', 'Other')
    ], validators=[DataRequired()])
    event_date = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired()])
    guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=3000)])
    message = TextAreaField('Message / Special Requirements')

    def validate_event_date(self, field):
        if field.data < date.today():
            raise ValidationError("Cannot select a past date")

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# ────────────────────────────────────────────────
# BASE TEMPLATE (same as before)
# ────────────────────────────────────────────────
BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hotel Shanvi & Marriage Hall{% if title %} — {{ title }}{% endif %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <style>
    :root { --gold: #d4af37; --dark-gold: #b8972e; }
    .text-gold { color: var(--gold) !important; }
    .btn-gold { background: var(--gold); color: black; font-weight: 600; }
    .btn-gold:hover { background: var(--dark-gold); }
    .hero {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
                    url('https://maps.app.goo.gl/DQAAhb1Gkbxz4bsYA') no-repeat center center/cover;
        min-height: 75vh;
        color: white;
        display: flex;
        align-items: center;
        text-align: center;
        }
    .floating-buttons {
      position: fixed; bottom: 25px; right: 25px; z-index: 1000;
    }
    .card-hover:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.15);
      transition: all 0.25s ease;
    }
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
  <div class="container">
    <a class="navbar-brand fw-bold text-gold fs-3" href="/">Hotel Shanvi</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="nav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
        <li class="nav-item"><a class="nav-link" href="/services">Services</a></li>
        <li class="nav-item"><a class="nav-link" href="/gallery">Gallery</a></li>
        <li class="nav-item"><a class="nav-link" href="/contact">Contact</a></li>
        <li class="nav-item"><a class="nav-link btn btn-gold ms-3 px-4" href="/book">Book Now</a></li>
      </ul>
    </div>
  </div>
</nav>

{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, msg in messages %}
      <div class="alert alert-{{ category }} alert-dismissible fade show m-3" role="alert">
        {{ msg }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    {% endfor %}
  {% endif %}
{% endwith %}

{{ content | safe }}

<footer class="bg-dark text-white py-5 mt-5">
  <div class="container">
    <div class="row">
      <div class="col-md-6">
        <h4 class="text-gold">Hotel Shanvi & Marriage Hall</h4>
        <p>Kargahar, Bihar 821107, India</p>
        <p><i class="fas fa-phone me-2"></i> 09142155803</p>
      </div>
      <div class="col-md-6 text-md-end">
        <p>© 2025 Hotel Shanvi & Marriage Hall</p>
      </div>
    </div>
  </div>
</footer>

<div class="floating-buttons d-flex flex-column gap-3">
  <a href="tel:09142155803" class="btn btn-danger rounded-circle shadow p-3">
    <i class="fas fa-phone fa-2x"></i>
  </a>
  <a href="https://wa.me/919142155803?text=Hello%2C%20I%20would%20like%20to%20book%20a%20date%20at%20Hotel%20Shanvi" target="_blank"
     class="btn btn-success rounded-circle shadow p-3">
    <i class="fab fa-whatsapp fa-2x"></i>
  </a>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  const dateEl = document.getElementById('event_date');
  if (dateEl) {
    const msg = document.createElement('div');
    msg.className = 'mt-2 fw-bold';
    dateEl.parentElement.appendChild(msg);
    dateEl.addEventListener('change', async () => {
      if (!dateEl.value) return;
      try {
        const r = await fetch(`/check-date?date=${dateEl.value}`);
        const data = await r.json();
        if (!data.available) {
          msg.innerHTML = '<span class="text-danger">✗ Date already booked</span>';
          dateEl.classList.add('is-invalid');
        } else {
          msg.innerHTML = '<span class="text-success">✓ Available</span>';
          dateEl.classList.remove('is-invalid');
        }
      } catch {
        msg.innerHTML = '<span class="text-warning">Cannot check availability</span>';
      }
    });
  }
});
</script>
</body>
</html>
"""

# ────────────────────────────────────────────────
# PAGE CONTENTS (same as your original)
# ────────────────────────────────────────────────
HOME = """ ... (aapka pura HOME content same rakha hai) ... """
# (Baki sab templates — ABOUT, BOOK, CONTACT, ADMIN_LOGIN, ADMIN_DASHBOARD — aapke original jaise hi hain. 
#  Space bachane ke liye yahan nahi likh raha, lekin aapke code mein same paste kar dena)

# Note: Aapke code mein HOME, ABOUT, BOOK, CONTACT, ADMIN_LOGIN, ADMIN_DASHBOARD templates same rakh sakte ho. 
# Sirf upar wala BASE aur routes change hue hain.

# ────────────────────────────────────────────────
# ROUTES
# ────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template_string(BASE, content=HOME, title="Home")

@app.route('/about')
def about():
    return render_template_string(BASE, content=ABOUT, title="About")

@app.route('/services')
def services():
    return render_template_string(BASE, content="""
    <div class="container py-5">
      <h1 class="text-gold text-center mb-5">Our Services</h1>
      <div class="row g-4">
        <div class="col-md-4"><div class="card card-hover"><div class="card-body text-center"><h5>Weddings</h5><p>Full celebration packages</p></div></div></div>
        <div class="col-md-4"><div class="card card-hover"><div class="card-body text-center"><h5>Engagements</h5><p>Elegant functions</p></div></div></div>
        <div class="col-md-4"><div class="card card-hover"><div class="card-body text-center"><h5>Birthdays & More</h5><p>Joyful events</p></div></div></div>
      </div>
    </div>
    """, title="Services")

@app.route('/gallery')
def gallery():
    return render_template_string(BASE, content="""
    <div class="container py-5">
      <h1 class="text-gold text-center mb-5">Gallery</h1>
      <div class="row g-3">
        {% for i in range(1,7) %}
        <div class="col-md-4"><img src="https://picsum.photos/seed/shanvi{{i}}/600/400" class="img-fluid rounded shadow" alt="Event {{i}}"></div>
        {% endfor %}
      </div>
    </div>
    """, title="Gallery")

@app.route('/contact')
def contact():
    return render_template_string(BASE, content=CONTACT, title="Contact")

@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm()
    
    if form.validate_on_submit():
        print("✅ FORM VALID")   # Debug
        existing = Booking.query.filter_by(event_date=form.event_date.data)\
                                 .filter(Booking.status.in_(['Pending', 'Confirmed']))\
                                 .first()
        if existing:
            flash("This date is already reserved. Please choose another date.", "danger")
        else:
            try:
                booking = Booking(
                    name=form.name.data,
                    phone=form.phone.data,
                    event_type=form.event_type.data,
                    event_date=form.event_date.data,
                    guests=form.guests.data,
                    message=form.message.data
                )
                db.session.add(booking)
                db.session.commit()
                flash("Booking request submitted successfully! We will contact you soon.", "success")
                return redirect(url_for('book'))
            except Exception as e:
                print("❌ DB ERROR:", e)
                db.session.rollback()
                flash("There was a database error. Please try again.", "danger")
    else:
        print("❌ FORM ERRORS:", form.errors)   # Important debug

    inner = render_template_string(BOOK, form=form)
    return render_template_string(BASE, content=inner, title="Book Now")


@app.route('/check-date')
def check_date():
    d = request.args.get('date')
    if not d:
        return jsonify({'available': True})
    try:
        dt = datetime.strptime(d, '%Y-%m-%d').date()
        taken = Booking.query.filter_by(event_date=dt)\
                             .filter(Booking.status.in_(['Pending', 'Confirmed']))\
                             .first()
        return jsonify({'available': taken is None})
    except Exception as e:
        print("Check-date error:", e)
        return jsonify({'available': True})


# Admin routes (same as before, bas thoda safe rakha)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin123':
            session['admin'] = True
            flash("Logged in successfully", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Incorrect username or password", "danger")
    inner = render_template_string(ADMIN_LOGIN, form=form)
    return render_template_string(BASE, content=inner, title="Admin Login")


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("You have been logged out", "info")
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("Please log in to access the admin panel", "warning")
        return redirect(url_for('admin_login'))
    bookings = Booking.query.order_by(Booking.event_date.desc()).all()
    inner = render_template_string(ADMIN_DASHBOARD, bookings=bookings)
    return render_template_string(BASE, content=inner, title="Admin Dashboard")


@app.route('/admin/confirm/<int:booking_id>', methods=['POST'])
def confirm_booking(booking_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'Pending':
        booking.status = 'Confirmed'
        db.session.commit()
        flash(f"Booking #{booking_id} has been confirmed", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        db.session.commit()
        flash(f"Booking #{booking_id} has been cancelled", "warning")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash(f"Booking #{booking_id} has been deleted", "danger")
    return redirect(url_for('admin_dashboard'))


# ────────────────────────────────────────────────
# START
# ────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Hotel Shanvi site starting...")
    print("Admin login → http://127.0.0.1:5000/admin/login")
    print("   Username: admin")
    print("   Password: admin123")
    print("Booking page → http://127.0.0.1:5000/book")
    app.run(debug=True, host='0.0.0.0', port=5000)
