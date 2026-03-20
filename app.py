from flask import Flask, render_template_string, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here_change_in_production'  # ← yeh zaroor change karna

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shanvi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DEBUG MODE (production mein False kar dena)
app.config['DEBUG'] = True
# app.config['PROPAGATE_EXCEPTIONS'] = True   # ← uncomment if needed

db = SQLAlchemy(app)

# ====================== MODELS ======================
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    event_date = db.Column(db.Date, nullable=False)
    event_type = db.Column(db.String(50))
    guests = db.Column(db.Integer)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.name} - {self.event_date}>'

# Create tables
with app.app_context():
    db.create_all()

# ====================== FORMS ======================
class BookingForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone Number')
    event_date = DateField('Event Date', validators=[DataRequired()])   # format hataya!
    event_type = StringField('Event Type (Wedding, Birthday, etc.)')
    guests = StringField('Number of Guests')
    message = TextAreaField('Additional Message')
    submit = SubmitField('Book Now')

# ====================== TEMPLATES (as strings) ======================

HOME = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shanvi Events - Home</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <h1 class="text-center mb-4">Welcome to Shanvi Events</h1>
        <p class="text-center lead">Aapke sapno ki shaadi aur events ko yaadgaar banayein</p>
        <div class="text-center mt-5">
            <a href="/book" class="btn btn-primary btn-lg">Book Your Event Now</a>
            <a href="/about" class="btn btn-outline-secondary btn-lg ms-3">About Us</a>
        </div>
    </div>
</body>
</html>
"""

BOOK = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Event - Shanvi Events</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <h2 class="text-center mb-4">Book Your Event</h2>
                
                {% if success %}
                <div class="alert alert-success text-center">
                    <strong>Booking Successful!</strong><br>
                    Thank you {{ name }}. We will contact you soon.
                </div>
                {% endif %}

                <div class="card shadow">
                    <div class="card-body">
                        <form method="POST">
                            {{ form.hidden_tag() }}
                            
                            <div class="mb-3">
                                {{ form.name.label(class="form-label") }}
                                {{ form.name(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.email.label(class="form-label") }}
                                {{ form.email(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.phone.label(class="form-label") }}
                                {{ form.phone(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.event_date.label(class="form-label") }}
                                {{ form.event_date(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.event_type.label(class="form-label") }}
                                {{ form.event_type(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.guests.label(class="form-label") }}
                                {{ form.guests(class="form-control") }}
                            </div>
                            
                            <div class="mb-3">
                                {{ form.message.label(class="form-label") }}
                                {{ form.message(class="form-control", rows="4") }}
                            </div>
                            
                            {{ form.submit(class="btn btn-primary w-100") }}
                        </form>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ABOUT = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us - Shanvi Events</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <h1 class="text-center">About Shanvi Events</h1>
        <p class="lead text-center mt-4">Hum aapke har event ko perfect banane ke liye committed hain.</p>
        <div class="text-center mt-5">
            <a href="/book" class="btn btn-primary">Book Now</a>
        </div>
    </div>
</body>
</html>
"""

CONTACT = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact - Shanvi Events</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <h1 class="text-center">Contact Us</h1>
        <p class="text-center">Call: +91-XXXXXXXXXX | Email: info@shanvievents.com</p>
    </div>
</body>
</html>
"""

# ====================== ROUTES ======================

@app.route('/')
def home():
    return render_template_string(HOME)

@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm()
    success = False
    name = ""

    if form.validate_on_submit():
        try:
            new_booking = Booking(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                event_date=form.event_date.data,
                event_type=form.event_type.data,
                guests=form.guests.data,
                message=form.message.data
            )
            db.session.add(new_booking)
            db.session.commit()
            
            success = True
            name = form.name.data
            form = BookingForm()  # reset form after success
            
        except Exception as e:
            print("Database Error:", str(e))   # terminal mein dikhega
            # yahan flash message add kar sakte ho baad mein

    # Agar error aaye to terminal mein red text dikhega
    return render_template_string(BOOK, form=form, success=success, name=name)

@app.route('/about')
def about():
    return render_template_string(ABOUT)

@app.route('/contact')
def contact():
    return render_template_string(CONTACT)

# ====================== RUN ======================
if __name__ == '__main__':
    print("DB PATH:", os.path.join(basedir, 'shanvi.db'))
    app.run(debug=True)   # ← yeh debug=True rakho
