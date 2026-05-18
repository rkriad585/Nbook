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
    confirm = (data.get('confirm_password') or '').strip()
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already taken"}), 400
    user = User(username=username, full_name=full_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    session['full_name'] = user.full_name
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
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({"authenticated": True, "username": user.username, "full_name": user.full_name, "email": user.email})
        return jsonify({"authenticated": True, "username": session.get('username')})
    return jsonify({"authenticated": False})

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        if request.is_json: return jsonify({"error": "Not authenticated"}), 401
        return redirect('/auth/login')
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        if request.is_json: return jsonify({"error": "User not found"}), 404
        return redirect('/auth/login')
    if request.method == 'GET':
        return render_template('profile.html', user=user)
    data = request.get_json(silent=True) or request.form
    if 'full_name' in data:
        user.full_name = (data['full_name'] or '').strip()
    if 'email' in data:
        user.email = (data['email'] or '').strip()
    if 'password' in data and data['password'].strip():
        if data['password'].strip() != (data.get('confirm_password') or '').strip():
            if request.is_json: return jsonify({"error": "Passwords do not match"}), 400
        if len(data['password'].strip()) < 4:
            if request.is_json: return jsonify({"error": "Password must be at least 4 characters"}), 400
        user.set_password(data['password'].strip())
    db.session.commit()
    session['full_name'] = user.full_name
    return jsonify({"status": "updated", "user": {"username": user.username, "full_name": user.full_name, "email": user.email}})
