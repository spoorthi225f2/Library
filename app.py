from flask import Flask, render_template, redirect, url_for, flash, session
from flask_jwt_extended import JWTManager
from database import init_db, seed_data
from auth import auth_bp
from admin import admin_bp
from member import member_bp
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(member_bp)

@app.before_request
def startup():
    """Initialize database on first run."""
    if not os.path.exists('library.db'):
        init_db()
        seed_data()

@app.route('/')
def index():
    """Home page - redirect to appropriate dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('member.dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
