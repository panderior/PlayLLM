from play_llm_flask import db, bcrypt
from sqlalchemy import Numeric, DateTime, Enum as SQLEnum
from datetime import datetime, timezone
from play_llm_flask.constants import ADMIN_USER, REGULAR_USER
from enum import Enum as PyEnum
import secrets


class RoleEnum(PyEnum):
    regular = REGULAR_USER
    admin   = ADMIN_USER

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=True) 
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        SQLEnum(RoleEnum, name='user_roles'),
        nullable=False,
        default=RoleEnum.regular
    )
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(
        DateTime(timezone=True),
        nullable=True
    ) 
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, plaintext):
        self.password_hash = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def verify_password(self, plaintext):
        return bcrypt.check_password_hash(self.password_hash, plaintext)

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(
        db.String(128),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: secrets.token_urlsafe(48)
    )
    verification_code = db.Column(
        db.String(6),
        nullable=True
    )
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    is_expired = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    user = db.relationship('User', backref='sessions', lazy='joined')
    
    def generate_verification_code(self):
        """Call when you need a new 6-digit code."""
        code = f"{secrets.randbelow(10**6):06d}"
        self.verification_code = code
        return code