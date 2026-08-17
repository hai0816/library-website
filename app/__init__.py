import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(app.root_path), 'instance'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.user.routes import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.admin.routes import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        _ensure_user_profile_columns()

    return app


def _ensure_user_profile_columns():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if 'user' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('user')}
    if 'full_name' not in cols:
        db.session.execute(text('ALTER TABLE user ADD COLUMN full_name VARCHAR(150)'))
    if 'email' not in cols:
        db.session.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(150)'))
    db.session.commit()
