import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.user import bp
from app.extensions import db
from app.models import Book, BorrowRecord, User
from app.services.activity_service import log_activity
import hashlib
from datetime import datetime

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', 'profile')

        if action == 'avatar' and 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Vulnerable: No file extension check (Arbitrary File Upload), Path Traversal
                filename = file.filename  # Not using secure_filename intentionally
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))

                current_user.avatar = filename
                db.session.commit()
                log_activity(current_user.id, f"Updated avatar to {filename}")
                flash('Đã cập nhật ảnh đại diện', 'success')
            else:
                flash('Vui lòng chọn tệp ảnh', 'danger')
        else:
            username = request.form.get('username', '').strip()
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()

            if not username:
                flash('Tên đăng nhập không được để trống', 'danger')
                return render_template('user/profile.html')

            existing = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existing:
                flash('Tên đăng nhập đã được sử dụng', 'danger')
                return render_template('user/profile.html')

            current_user.username = username
            current_user.full_name = full_name or None
            current_user.email = email or None
            db.session.commit()
            log_activity(current_user.id, f"Updated profile: {username}")
            flash('Đã cập nhật hồ sơ', 'success')

    return render_template('user/profile.html')

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if md5_hash(current_password) != current_user.password:
            flash('Mật khẩu hiện tại không đúng', 'danger')
            return render_template('user/change_password.html')

        if not new_password:
            flash('Vui lòng nhập mật khẩu mới', 'danger')
            return render_template('user/change_password.html')

        if new_password != confirm_password:
            flash('Xác nhận mật khẩu không khớp', 'danger')
            return render_template('user/change_password.html')

        current_user.password = md5_hash(new_password)
        db.session.commit()
        log_activity(current_user.id, "Changed password")
        flash('Đổi mật khẩu thành công', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/change_password.html')

@bp.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    already = BorrowRecord.query.filter_by(
        user_id=current_user.id, book_id=book.id, status='borrowed'
    ).first()
    if already:
        flash('Bạn đang mượn cuốn sách này', 'danger')
        return redirect(url_for('main.book_detail', book_id=book.id))

    if book.is_available:
        record = BorrowRecord(user_id=current_user.id, book_id=book.id)
        book.is_available = False
        db.session.add(record)
        db.session.commit()
        log_activity(current_user.id, f"Borrowed book ID: {book.id}")
        flash('Mượn sách thành công', 'success')
    else:
        flash('Sách hiện không còn để mượn', 'danger')
    return redirect(url_for('main.book_detail', book_id=book.id))

@bp.route('/return', methods=['POST'])
@login_required
def return_book():
    record_id = request.form['record_id']
    # Vulnerable: IDOR (Insecure Direct Object Reference)
    # Doesn't check if record belongs to current_user!
    record = BorrowRecord.query.get_or_404(record_id)
    if record.status == 'borrowed':
        record.status = 'returned'
        record.return_date = datetime.utcnow()
        
        book = Book.query.get(record.book_id)
        if book:
            book.is_available = True
            
        db.session.commit()
        log_activity(current_user.id, f"Returned book ID: {record.book_id} (Record: {record_id})")
        flash('Trả sách thành công', 'success')
    return redirect(url_for('user.borrow_history'))

@bp.route('/history')
@login_required
def borrow_history():
    records = BorrowRecord.query.filter_by(user_id=current_user.id).order_by(BorrowRecord.id.desc()).all()
    return render_template('user/borrow_history.html', records=records)
