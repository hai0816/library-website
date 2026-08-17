from flask import render_template, request
from app.main import bp
from app.models import Book, Category, User, BorrowRecord
from app.extensions import db
from sqlalchemy import text

@bp.route('/')
def index():
    recent_books = Book.query.order_by(Book.id.desc()).limit(8).all()
    stats = {
        'books': Book.query.count(),
        'users': User.query.count(),
        'borrows': BorrowRecord.query.count()
    }
    return render_template('main/index.html', recent_books=recent_books, stats=stats)

@bp.route('/books')
def books():
    categories = Category.query.all()
    search_query = request.args.get('q', '')
    category_id = request.args.get('category', '', type=str)
    
    if search_query:
        # Vulnerable: SQL Injection & Reflected XSS
        # Using raw SQL string formatting
        query = f"SELECT * FROM book WHERE title LIKE '%{search_query}%' OR author LIKE '%{search_query}%'"
        result = db.session.execute(text(query)).fetchall()
        books = [Book.query.get(b[0]) for b in result if Book.query.get(b[0])]
    elif category_id:
        books = Book.query.filter_by(category_id=category_id).all()
    else:
        books = Book.query.all()
        
    return render_template('main/books.html', books=books, categories=categories, search_query=search_query)

@bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('main/book_detail.html', book=book)
