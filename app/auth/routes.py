import hashlib
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.extensions import db
from app.models import User
from app.services.activity_service import log_activity

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vulnerable: Weak hash, no brute-force protection
        hashed_pw = md5_hash(password)
        
        # Vulnerable: SQLi potential if we didn't use ORM, but let's make it raw SQL to satisfy requirements
        # Execute raw SQL for authentication to allow SQL injection!
        from sqlalchemy import text
        query = f"SELECT id, username, role FROM user WHERE username='{username}' AND password='{hashed_pw}'"
        result = db.session.execute(text(query)).fetchone()
        
        if result:
            user = User.query.get(result[0])
            login_user(user)
            log_activity(user.id, f"User logged in: {username}")
            return redirect(url_for('main.index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vulnerable: No password complexity check, MD5 used
        hashed_pw = md5_hash(password)
        
        # Vulnerable: Stored XSS if username has HTML
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        try:
            db.session.commit()
            log_activity(user.id, f"New user registered: {username}")
            flash('Đăng ký thành công. Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('Tên đăng nhập đã tồn tại', 'danger')
            
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    log_activity(current_user.id if current_user.is_authenticated else None, "User logged out")
    logout_user()
    return redirect(url_for('main.index'))
