from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Make sure this matches the FK reference
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(120), nullable=False)

    # Method to set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check password hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Required for administrative interface
    def __repr__(self):
        return '<User {}>'.format(self.username)
