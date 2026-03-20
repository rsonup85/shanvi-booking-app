from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime, date
import os

app = Flask(__name__)

# Security - use environment variable in production
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Persistent storage on Render (use disk mount /data)
db_path = os.path.join('/data', 'shanvi.db') if os.path.exists('/data') else 'sqlite:///shanvi.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    guests     = db.Column(db.Integer, nullable=False)
    message    = db.Column(db.Text)
    status     = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ────────────────────────────────────────────────
# FORMS
# ────────────────────────────────────────────────
class BookingForm(FlaskForm):
    name       = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone      = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    event_type = SelectField('Event Type', choices=[
        ('Wedding', 'Wedding'), ('Birthday', 'Birthday'),
        ('Engagement', 'Engagement'), ('Corporate', 'Corporate'), ('Other', 'Other')
    ], validators=[DataRequired()])
    event_date = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired()])
    guests     = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=3000)])
    message    = TextAreaField('Message / Special Requirements')

    def validate_event_date(self, field):
        if field.data < date.today():
            raise ValidationError("Cannot select a past date")

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# ────────────────────────────────────────────────
# MINIMAL BOOKING TEMPLATE (only this page)
# ────────────────────────────────────────────────
BOOK_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Book Event - Hotel Shanvi</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    :root { --gold: #d4af37; --dark-gold: #b8972e; }
    .text-gold { color: var(--gold) !important; }
    .btn-gold  { background: var(--gold); color: black; font-weight: 600; }
    .btn-gold:hover { background: var(--dark-gold); }
  </style>
</head>
<body class="bg-light py-5">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card shadow-lg">
          <div class="card-header bg-gold text-dark text-center py-4">
            <h3>Book Your Event</h3>
            <a href="/" class="btn btn-link">← Back to Main Website</a>
          </div>
          <div class="card-body p-5">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, msg in messages %}
                  <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                    {{ msg }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                  </div>
                {% endfor %}
              {% endif %}
            {% endwith %}
            <form method="POST">
              {{ form.hidden_tag() }}
              <div class="mb-4">{{ form.name.label(class="form-label fw-bold") }}{{ form.name(class="form-control form-control-lg") }}</div>
              <div class="mb-4">{{ form.phone.label(class="form-label fw-bold") }}{{ form.phone(class="form-control form-control-lg") }}</div>
              <div class="mb-4">{{ form.event_type.label(class="form-label fw-bold") }}{{ form.event_type(class="form-select form-select-lg") }}</div>
              <div class="mb-4">{{ form.event_date.label(class="form-label fw-bold") }}{{ form.event_date(class="form-control form-control-lg", id="event_date") }}</div>
              <div class="mb-4">{{ form.guests.label(class="form-label fw-bold") }}{{ form.guests(class="form-control form-control-lg") }}</div>
              <div class="mb-4">{{ form.message.label(class="form-label fw-bold") }}{{ form.message(class="form-control", rows=4) }}</div>
              <button type="submit" class="btn btn-gold btn-lg w-100 py-3">Submit Request</button>
            </form>
          </div>
        </div>
      </div>
    </div>
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
# ROUTES (only booking + admin + api)
# ────────────────────────────────────────────────

@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm()
    if form.validate_on_submit():
        existing = Booking.query.filter_by(event_date=form.event_date.data)\
                                 .filter(Booking.status.in_(['Pending', 'Confirmed']))\
                                 .first()
        if existing:
            flash("This date is already reserved. Please choose another date.", "danger")
        else:
            booking = Booking(
                name       = form.name.data,
                phone      = form.phone.data,
                event_type = form.event_type.data,
                event_date = form.event_date.data,
                guests     = form.guests.data,
                message    = form.message.data
            )
            db.session.add(booking)
            db.session.commit()
            flash("Booking request submitted successfully! We will contact you soon.", "success")
            return redirect(url_for('book'))
    return render_template_string(BOOK_TEMPLATE, form=form)

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
    except ValueError:
        return jsonify({'available': True, 'error': 'Invalid date format'})
    except Exception as e:
        return jsonify({'available': True, 'error': str(e)}), 500

# ────────────────────────────────────────────────
# ADMIN PART (keep same as before)
# ────────────────────────────────────────────────

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login - Hotel Shanvi</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    :root { --gold: #d4af37; --dark-gold: #b8972e; }
    .text-gold { color: var(--gold) !important; }
    .btn-gold  { background: var(--gold); color: black; }
  </style>
</head>
<body class="bg-light py-5">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-lg">
          <div class="card-header bg-dark text-white text-center py-4">
            <h3>Admin Panel Login</h3>
          </div>
          <div class="card-body p-5">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, msg in messages %}
                  <div class="alert alert-{{ category }}">{{ msg }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}
            <form method="POST">
              {{ form.hidden_tag() }}
              <div class="mb-4">{{ form.username.label }}{{ form.username(class="form-control") }}</div>
              <div class="mb-4">{{ form.password.label }}{{ form.password(class="form-control") }}</div>
              <button type="submit" class="btn btn-gold w-100">Sign In</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Add your ADMIN_LOGIN, ADMIN_DASHBOARD templates and routes here (same as original)
# Just use render_template_string(ADMIN_LOGIN_TEMPLATE, form=form) etc.

# Admin credentials from env (secure!)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # CHANGE THIS!

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == ADMIN_USERNAME and form.password.data == ADMIN_PASSWORD:
            session['admin'] = True
            flash("Logged in successfully", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Incorrect credentials", "danger")
    return render_template_string(ADMIN_LOGIN_TEMPLATE, form=form)

# ... rest of admin routes (dashboard, confirm, cancel, delete) same as your original code ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)