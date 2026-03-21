from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kargahar_wale_digital_2026_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kargahar_leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===================== COMMON UI COMPONENTS =====================
CSS = """
:root {
    --primary: #6366f1;
    --accent: #a855f7;
}
body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #0a0a0a;
    color: #e0e0e0;
    line-height: 1.6;
}
.navbar {
    background: rgba(10,10,10,0.95) !important;
    backdrop-filter: blur(20px);
}
.hero {
    height: 100vh;
    background: linear-gradient(rgba(10,10,10,0.8), rgba(10,10,10,0.9)),
                url('https://drive.google.com/uc?export=view&id=15k2crrrMjAYRBvh5z8w5q-NgfVJP-Cre')
                center/cover no-repeat;
    display: flex;
    align-items: center;
}
.gradient-text {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.service-card {
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: #111;
    border: 1px solid #222;
}
.service-card:hover {
    transform: translateY(-15px);
    box-shadow: 0 25px 50px -12px rgb(99 102 241 / 0.5);
    border-color: var(--primary);
}
.btn-primary {
    background: linear-gradient(45deg, #6366f1, #a855f7);
    border: none;
}
.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(99,102,241,0.4);
}
.section-title:after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
}
.whatsapp-float {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: #25d366;
    color: white;
    width: 65px;
    height: 65px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    box-shadow: 0 10px 30px rgba(37,211,102,0.5);
    z-index: 9999;
    transition: all 0.3s;
}
.whatsapp-float:hover {
    transform: scale(1.15);
}
.table-dark th {
    background: #1a1a1a;
}
"""

NAVBAR = """
<nav class="navbar navbar-expand-lg navbar-dark sticky-top">
    <div class="container">
        <a class="navbar-brand fw-bold fs-3 gradient-text" href="/">Kargahar Wale Digital</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="nav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item"><a class="nav-link px-4" href="/">Home</a></li>
                <li class="nav-item"><a class="nav-link px-4" href="/about">About</a></li>
                <li class="nav-item"><a class="nav-link px-4" href="/services">Services</a></li>
                <li class="nav-item"><a class="nav-link px-4" href="/contact">Contact</a></li>
                <li class="nav-item"><a class="nav-link px-4 text-warning" href="/admin/login"><i class="fas fa-shield-alt"></i> Admin</a></li>
            </ul>
        </div>
    </div>
</nav>
"""

FOOTER = """
<footer class="bg-black py-5 border-top border-secondary mt-5">
    <div class="container">
        <div class="row">
            <div class="col-lg-4">
                <h4 class="gradient-text fw-bold">Kargahar Wale Digital</h4>
                <p class="text-white-50">Premium Digital Marketing Agency • Kargahar, Bihar 821107</p>
            </div>
            <div class="col-lg-2 col-6">
                <h6 class="fw-bold text-white">Quick Links</h6>
                <ul class="list-unstyled">
                    <li><a href="/" class="text-white-50 text-decoration-none">Home</a></li>
                    <li><a href="/about" class="text-white-50 text-decoration-none">About</a></li>
                    <li><a href="/services" class="text-white-50 text-decoration-none">Services</a></li>
                    <li><a href="/contact" class="text-white-50 text-decoration-none">Contact</a></li>
                </ul>
            </div>
            <div class="col-lg-3 col-6">
                <h6 class="fw-bold text-white">Services</h6>
                <ul class="list-unstyled text-white-50">
                    <li>SEO Optimization</li>
                    <li>Social Media Marketing</li>
                    <li>Website Development</li>
                    <li>Google Ads / PPC</li>
                    <li>Lead Generation</li>
                </ul>
            </div>
            <div class="col-lg-3">
                <h6 class="fw-bold text-white">Contact</h6>
                <p class="text-white-50 mb-1"><i class="fas fa-map-marker-alt"></i> Kargahar, Rohtas, Bihar 821107</p>
                <p class="text-white-50 mb-1"><i class="fas fa-envelope"></i> rsonup75@gmail.com</p>
                <p class="text-white-50"><i class="fas fa-phone"></i> +91 82100 12345</p>
            </div>
        </div>
        <hr class="my-4 border-secondary">
        <div class="text-center text-white-50 small">
            © 2026 Kargahar Wale Digital • Made with ❤️ in Bihar, India
        </div>
    </div>
</footer>
"""

WHATSAPP = """
<a href="https://wa.me/918210012345?text=Hello%20Kargahar%20Wale%20Digital" target="_blank" class="whatsapp-float">
    <i class="fab fa-whatsapp"></i>
</a>
"""

JS = """
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        if (a.getAttribute('href').length > 1) {
            e.preventDefault();
            document.querySelector(a.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
        }
    });
});
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => new bootstrap.Alert(alert).close());
}, 5000);
"""

BASE_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
    <meta name="description" content="Kargahar Wale Digital - Premium Digital Marketing Agency in Kargahar, Bihar">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <style>{CSS}</style>
</head>
<body>
    {NAVBAR}
    {{{{ body_content | safe }}}}
    {FOOTER}
    {WHATSAPP}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>{JS}</script>
</body>
</html>
"""

# ===================== PUBLIC ROUTES =====================

@app.route('/')
def home():
    body = """
    <section class="hero text-center">
        <div class="container position-relative z-3">
            <h1 class="display-3 fw-bold mb-4 gradient-text">Kargahar Wale Digital</h1>
            <p class="lead fs-4 mb-5">Your Local Digital Growth Partner in Bihar</p>
            <div class="d-flex justify-content-center gap-3">
                <a href="/services" class="btn btn-primary btn-lg px-5">Our Services</a>
                <a href="/contact" class="btn btn-outline-light btn-lg px-5">Get Free Quote</a>
            </div>
        </div>
    </section>

    <div class="py-4 bg-black text-center border-bottom">
        <div class="container">
            <span class="text-white-50">Serving Bihar Businesses • 500+ Successful Campaigns • 98% Retention</span>
        </div>
    </div>

    <section class="py-5 bg-dark">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="display-5 fw-bold section-title">Our Services</h2>
            </div>
            <div class="row g-4">
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 text-center h-100">
                        <i class="fas fa-search fa-4x mb-4 text-primary"></i>
                        <h4>SEO Optimization</h4>
                        <p class="text-white-50">Rank #1 on Google in Bihar</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 text-center h-100">
                        <i class="fab fa-instagram fa-4x mb-4 text-pink"></i>
                        <h4>Social Media Marketing</h4>
                        <p class="text-white-50">Instagram &amp; Facebook Growth</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 text-center h-100">
                        <i class="fas fa-chart-line fa-4x mb-4 text-success"></i>
                        <h4>Google Ads &amp; PPC</h4>
                        <p class="text-white-50">Targeted Lead Generation</p>
                    </div>
                </div>
            </div>
            <div class="text-center mt-5">
                <a href="/services" class="btn btn-primary btn-lg">View All Services →</a>
            </div>
        </div>
    </section>
    """
    return render_template_string(BASE_TEMPLATE, title="Kargahar Wale Digital | Home", body_content=body)


@app.route('/about')
def about():
    body = """
    <section class="py-5">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h2 class="display-5 fw-bold mb-4">About Kargahar Wale Digital</h2>
                    <p class="lead text-white-50">Founded in Kargahar, Bihar, we are a premium digital marketing agency helping local businesses dominate online.</p>
                    <div class="mt-5">
                        <h5 class="fw-bold">Our Mission</h5>
                        <p class="text-white-50">Empower every business in Bihar with world-class digital strategies.</p>
                        <h5 class="fw-bold mt-4">Our Vision</h5>
                        <p class="text-white-50">Make Kargahar the digital hub of Bihar.</p>
                    </div>
                </div>
                <div class="col-lg-6">
                    <img src="https://picsum.photos/id/201/800/600" class="img-fluid rounded-4 shadow" alt="About Us">
                </div>
            </div>
        </div>
    </section>
    """
    return render_template_string(BASE_TEMPLATE, title="About Us | Kargahar Wale Digital", body_content=body)


@app.route('/services')
def services():
    body = """
    <section class="py-5 bg-dark">
        <div class="container">
            <h2 class="display-5 fw-bold text-center mb-5 section-title">Our Premium Services</h2>
            <div class="row g-5">
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 h-100">
                        <i class="fas fa-search fa-4x mb-4 text-primary"></i>
                        <h4 class="fw-bold">SEO Optimization</h4>
                        <p class="text-white-50">Local &amp; national SEO that gets you on page 1 of Google. Monthly reports and guaranteed results.</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 h-100">
                        <i class="fab fa-instagram fa-4x mb-4 text-pink"></i>
                        <h4 class="fw-bold">Social Media Marketing</h4>
                        <p class="text-white-50">Full management of Instagram, Facebook, YouTube &amp; LinkedIn. Viral campaigns for Bihar audience.</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 h-100">
                        <i class="fas fa-ad fa-4x mb-4 text-success"></i>
                        <h4 class="fw-bold">Google Ads &amp; PPC</h4>
                        <p class="text-white-50">ROI-focused paid campaigns. Only pay for real leads.</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 h-100">
                        <i class="fas fa-laptop-code fa-4x mb-4 text-info"></i>
                        <h4 class="fw-bold">Website Development</h4>
                        <p class="text-white-50">Modern, fast, SEO-ready websites that convert visitors into customers.</p>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="service-card p-5 rounded-4 h-100">
                        <i class="fas fa-users fa-4x mb-4 text-warning"></i>
                        <h4 class="fw-bold">Lead Generation</h4>
                        <p class="text-white-50">Daily qualified leads delivered directly to your WhatsApp or email.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """
    return render_template_string(BASE_TEMPLATE, title="Services | Kargahar Wale Digital", body_content=body)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        if name and email and message:
            new_lead = Lead(name=name, email=email, phone=phone, message=message)
            db.session.add(new_lead)
            db.session.commit()
            flash('Thank you! Your message has been received. We will contact you soon.', 'success')
            return redirect('/contact')
        else:
            flash('Please fill all required fields.', 'danger')
    
    body = """
    <section class="py-5">
        <div class="container">
            <div class="row">
                <div class="col-lg-6">
                    <h2 class="display-5 fw-bold mb-4">Get In Touch</h2>
                    <form method="POST">
                        <div class="mb-3">
                            <input type="text" name="name" class="form-control bg-dark text-white border-secondary" placeholder="Your Name *" required>
                        </div>
                        <div class="mb-3">
                            <input type="email" name="email" class="form-control bg-dark text-white border-secondary" placeholder="Email Address *" required>
                        </div>
                        <div class="mb-3">
                            <input type="tel" name="phone" class="form-control bg-dark text-white border-secondary" placeholder="Phone Number">
                        </div>
                        <div class="mb-3">
                            <textarea name="message" rows="6" class="form-control bg-dark text-white border-secondary" placeholder="Your Message *" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary btn-lg w-100">Send Message</button>
                    </form>
                </div>
                
                <div class="col-lg-6">
                    <div class="mt-4">
                        <h5 class="fw-bold">Our Location</h5>

                            <iframe 
                                width="100%" 
                                height="380" 
                                style="border:0;border-radius:12px;" 
                                loading="lazy" 
                                allowfullscreen
                                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d28898.20250775592!2d83.90157907258843!3d25.126381381385176!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x398dc0724cd8e5ad%3A0xc3986741a57985d2!2sKargahar%2C%20Bihar%20821107!5e0!3m2!1sen!2sin!4v1774053455421!5m2!1sen!2sin">
                            </iframe>

                            
                    
                </div>
            </div>
        </div>
    </section>
    """
    return render_template_string(BASE_TEMPLATE, title="Contact Us | Kargahar Wale Digital", body_content=body)


# ===================== ADMIN ROUTES =====================

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login | Kargahar Wale Digital</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <style>{{ CSS }}</style>
</head>
<body class="bg-black">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card bg-dark border-secondary mt-5">
                    <div class="card-body p-5">
                        <h3 class="text-center gradient-text mb-4">Admin Login</h3>
                        {% with messages = get_flashed_messages(with_categories=True) %}
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
                            <div class="mb-3">
                                <input type="text" name="username" class="form-control bg-black text-white" placeholder="Username" required>
                            </div>
                            <div class="mb-4">
                                <input type="password" name="password" class="form-control bg-black text-white" placeholder="Password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 py-3">Login to Dashboard</button>
                        </form>
                    </div>
                </div>
                <p class="text-center text-white-50 mt-3 small">Default: admin / admin123</p>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard | Kargahar Wale Digital</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <style>{{ CSS }}</style>
</head>
<body class="bg-black">
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand fw-bold">Kargahar Wale Digital - Admin</span>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container py-5">
        <h2 class="fw-bold mb-4">
    All Leads <span class="badge bg-primary">{{ leads|length }}</span>
</h2>
        
        {% with messages = get_flashed_messages(with_categories=True) %}
            {% if messages %}
                {% for category, msg in messages %}
                    <div class="alert alert-{{ category }}">{{ msg }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="table-responsive">
            <table class="table table-dark table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Message</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr>
                        <td>{{ lead.id }}</td>
                        <td>{{ lead.name }}</td>
                        <td>{{ lead.email }}</td>
                        <td>{{ lead.phone or '-' }}</td>
                        <td><small>{{ lead.message[:80] }}{% if lead.message|length > 80 %}...{% endif %}</small></td>
                        <td>{{ lead.created_at.strftime('%d %b %Y') }}</td>
                        <td>
                            <a href="/admin/delete/{{ lead.id }}" onclick="return confirm('Delete this lead permanently?')" class="btn btn-danger btn-sm">
                                <i class="fas fa-trash"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% if not leads %}
        <div class="text-center py-5 text-white-50">
            <i class="fas fa-inbox fa-3x mb-3"></i>
            <p>No leads yet</p>
        </div>
        {% endif %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['admin_logged_in'] = True
            flash('Welcome back, Admin!', 'success')
            return redirect('/admin')
        flash('Invalid credentials', 'danger')
    return render_template_string(ADMIN_LOGIN_TEMPLATE, CSS=CSS)


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, leads=leads, CSS=CSS)


@app.route('/admin/delete/<int:lead_id>')
def delete_lead(lead_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    lead = Lead.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted successfully', 'success')
    return redirect('/admin')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'info')
    return redirect('/admin/login')


# ===================== INIT DB =====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
