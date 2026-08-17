from app import create_app
from app.extensions import db
from app.models import User, Category, Book
import os
import hashlib

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=hashlib.md5('admin123'.encode()).hexdigest(),
                role='admin',
                full_name='Quản trị viên',
                email='admin@libnet.vn'
            )
            db.session.add(admin)

            samples = [
                ('Văn học', [
                    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Tiểu thuyết kinh điển về giấc mơ Mỹ.'),
                    ('Số đỏ', 'Vũ Trọng Phụng', 'Tác phẩm trào phúng nổi tiếng của văn học Việt Nam.'),
                ]),
                ('Khoa học', [
                    ('A Brief History of Time', 'Stephen Hawking', 'Giới thiệu vũ trụ học dành cho độc giả phổ thông.'),
                    ('Sapiens', 'Yuval Noah Harari', 'Lược sử loài người từ thời đồ đá đến hiện đại.'),
                ]),
                ('Công nghệ', [
                    ('Clean Code', 'Robert C. Martin', 'Nguyên tắc viết mã nguồn dễ đọc và dễ bảo trì.'),
                    ('The Pragmatic Programmer', 'Andrew Hunt', 'Kỹ năng thực hành cho lập trình viên chuyên nghiệp.'),
                ]),
            ]
            for cat_name, books in samples:
                cat = Category(name=cat_name)
                db.session.add(cat)
                db.session.flush()
                for title, author, desc in books:
                    db.session.add(Book(title=title, author=author, description=desc, category_id=cat.id))

            db.session.commit()
            print("Database initialized with default admin (admin / admin123).")

if __name__ == '__main__':
    instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'library.db')
    if not os.path.exists(db_path):
        init_db()
    else:
        with app.app_context():
            if User.query.count() == 0:
                init_db()
    app.run(debug=True)
