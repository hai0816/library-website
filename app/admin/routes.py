from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User, Book, Category, ActivityLog, BorrowRecord
from app.extensions import db
from app.decorators import admin_required
from app.services.activity_service import log_activity
import hashlib

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def _parse_category_id(raw):
    if raw in (None, '', 'none'):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'books': Book.query.count(),
        'categories': Category.query.count(),
        'borrows_active': BorrowRecord.query.filter_by(status='borrowed').count(),
        'borrows_total': BorrowRecord.query.count()
    }
    recent_logs = ActivityLog.query.order_by(ActivityLog.id.desc()).limit(8).all()
    return render_template('admin/dashboard.html', stats=stats, recent_logs=recent_logs)

@bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form.get('password', '123456')
        role = request.form.get('role', 'user')
        full_name = request.form.get('full_name', '').strip() or None
        email = request.form.get('email', '').strip() or None
        hashed_pw = md5_hash(password)
        user = User(username=username, password=hashed_pw, role=role, full_name=full_name, email=email)
        db.session.add(user)
        try:
            db.session.commit()
            log_activity(current_user.id, f"Admin created user: {username}")
            flash('Thêm người dùng thành công', 'success')
        except Exception:
            db.session.rollback()
            flash('Tên đăng nhập đã tồn tại', 'danger')
    users_list = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=users_list)

@bp.route('/users/update/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    username = request.form.get('username', '').strip()
    role = request.form.get('role', user.role)
    full_name = request.form.get('full_name', '').strip() or None
    email = request.form.get('email', '').strip() or None
    password = request.form.get('password', '').strip()

    if not username:
        flash('Tên đăng nhập không được để trống', 'danger')
        return redirect(url_for('admin.users'))

    existing = User.query.filter(User.username == username, User.id != user.id).first()
    if existing:
        flash('Tên đăng nhập đã tồn tại', 'danger')
        return redirect(url_for('admin.users'))

    if user.id == current_user.id and role != 'admin':
        flash('Không thể tự hạ quyền quản trị của chính mình', 'danger')
        return redirect(url_for('admin.users'))

    user.username = username
    user.role = role
    user.full_name = full_name
    user.email = email
    if password:
        user.password = md5_hash(password)
    db.session.commit()
    log_activity(current_user.id, f"Admin updated user ID: {user.id}")
    flash('Cập nhật người dùng thành công', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
# Vulnerable: Missing @admin_required! Privilege Escalation!
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể xóa tài khoản đang đăng nhập', 'danger')
        return redirect(url_for('admin.users'))
    BorrowRecord.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    log_activity(current_user.id if current_user.is_authenticated else None, f"Deleted user ID: {user_id}")
    flash('Đã xóa người dùng', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/books', methods=['GET', 'POST'])
@login_required
@admin_required
def books():
    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        cat_id = _parse_category_id(request.form.get('category_id'))
        description = request.form.get('description', '').strip()
        book = Book(title=title, author=author, category_id=cat_id, description=description or None)
        db.session.add(book)
        db.session.commit()
        log_activity(current_user.id, f"Admin added book: {title}")
        flash('Thêm sách thành công', 'success')
    books_list = Book.query.order_by(Book.id.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/books.html', books=books_list, categories=categories)

@bp.route('/books/update/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    if not title or not author:
        flash('Tiêu đề và tác giả không được để trống', 'danger')
        return redirect(url_for('admin.books'))
    book.title = title
    book.author = author
    book.category_id = _parse_category_id(request.form.get('category_id'))
    book.description = request.form.get('description', '').strip() or None
    available = request.form.get('is_available')
    if available is not None:
        book.is_available = available == '1'
    db.session.commit()
    log_activity(current_user.id, f"Admin updated book ID: {book.id}")
    flash('Cập nhật sách thành công', 'success')
    return redirect(url_for('admin.books'))

@bp.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    BorrowRecord.query.filter_by(book_id=book.id).delete()
    db.session.delete(book)
    db.session.commit()
    log_activity(current_user.id, f"Admin deleted book ID: {book_id}")
    flash('Đã xóa sách', 'success')
    return redirect(url_for('admin.books'))

@bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form['name'].strip()
        cat = Category(name=name)
        db.session.add(cat)
        try:
            db.session.commit()
            log_activity(current_user.id, f"Admin added category: {name}")
            flash('Thêm thể loại thành công', 'success')
        except Exception:
            db.session.rollback()
            flash('Thể loại đã tồn tại', 'danger')
    cats = Category.query.order_by(Category.id.asc()).all()
    return render_template('admin/categories.html', categories=cats)

@bp.route('/categories/update/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def update_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('Tên thể loại không được để trống', 'danger')
        return redirect(url_for('admin.categories'))
    existing = Category.query.filter(Category.name == name, Category.id != cat.id).first()
    if existing:
        flash('Thể loại đã tồn tại', 'danger')
        return redirect(url_for('admin.categories'))
    cat.name = name
    db.session.commit()
    log_activity(current_user.id, f"Admin updated category ID: {cat.id}")
    flash('Cập nhật thể loại thành công', 'success')
    return redirect(url_for('admin.categories'))

@bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    Book.query.filter_by(category_id=cat.id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    log_activity(current_user.id, f"Admin deleted category ID: {cat_id}")
    flash('Đã xóa thể loại', 'success')
    return redirect(url_for('admin.categories'))

@bp.route('/logs')
@login_required
@admin_required
def logs():
    q = request.args.get('q', '').strip()
    query = ActivityLog.query
    if q:
        query = query.filter(ActivityLog.action.like(f'%{q}%'))
    activity_logs = query.order_by(ActivityLog.id.desc()).all()
    return render_template('admin/activity_logs.html', logs=activity_logs, search_query=q)
