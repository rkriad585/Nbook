from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from core import db
from core.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    data = request.get_json(silent=True) or request.form
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({"status": "registered", "username": user.username})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    data = request.get_json(silent=True) or request.form
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({"status": "logged_in", "username": user.username})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "logged_out"})

@auth_bp.route('/me')
def me():
    if 'user_id' in session:
        return jsonify({"authenticated": True, "username": session.get('username')})
    return jsonify({"authenticated": False})
