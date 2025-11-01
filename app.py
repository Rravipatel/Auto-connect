import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_compress import Compress
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', template_folder='templates')
Compress(app)
# IMPORTANT: change this secret key for production; keep it secret
app.secret_key = os.environ.get('AXIS_SECRET') or 'dev-secret-key-please-change'

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.json')

# Ensure data dir and files
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)
if not os.path.exists(FEEDBACK_FILE):
    open(FEEDBACK_FILE, 'a', encoding='utf-8').close()

def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    user = session.get('user_email')
    return render_template('home.html', user=user)

# AUTH: Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        if not email or not password:
            return render_template('signup.html', error='Email and password required.')
        users = load_users()
        if email in users:
            return render_template('signup.html', error='Account already exists.')
        users[email] = {
            'password_hash': generate_password_hash(password),
            'role': role,
            'created_at': datetime.utcnow().isoformat()
        }
        save_users(users)
        session['user_email'] = email
        session['user_role'] = role
        return redirect(url_for('home'))
    return render_template('signup.html')

# AUTH: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        users = load_users()
        user = users.get(email)
        if user and check_password_hash(user.get('password_hash',''), password):
            session['user_email'] = email
            session['user_role'] = user.get('role','student')
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Feedback route (ajax or form)
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name','').strip(),
            'email': request.form.get('email','').strip(),
            'role': request.form.get('role','').strip(),
            'rating': request.form.get('rating','').strip(),
            'message': request.form.get('message','').strip(),
            'timestamp': datetime.utcnow().isoformat()
        }
        with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        # Return JSON for AJAX submit
        return jsonify(status='success', message='Feedback received.')
    return render_template('feedback.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')

# sitemap.xml generator route
@app.route('/sitemap.xml')
def sitemap():
    pages = []
    pages.append({'loc': request.url_root.rstrip('/') + url_for('home'), 'changefreq': 'daily', 'priority': '0.9'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('login'), 'changefreq': 'monthly', 'priority': '0.6'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('signup'), 'changefreq': 'monthly', 'priority': '0.6'})
    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    return app.response_class(sitemap_xml, mimetype='application/xml')

# robots.txt served from static
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# mock upcoming AI features API (for demo)
@app.route('/api/upcoming-ai')
def api_ai():
    features = [
        "AI-powered ride scheduling",
        "Voice booking assistant",
        "Predictive wait time analytics",
        "Driver heatmaps and routing optimization"
    ]
    return jsonify({'features': features})

if __name__ == '__main__':
    app.run(debug=True)
