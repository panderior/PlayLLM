from play_llm_flask import db, bcrypt
from sqlalchemy import Numeric, DateTime, Enum as SQLEnum
from datetime import datetime, timezone
from play_llm_flask.constants import ADMIN_USER, REGULAR_USER,USER_ACTION,MODEL_ACTION
from enum import Enum as PyEnum
import secrets

# enums
class UserRoleEnum(PyEnum):
    regular = REGULAR_USER
    admin   = ADMIN_USER

class UserGameActionRoleEnum(PyEnum):
    user  = USER_ACTION
    model = MODEL_ACTION
    
# models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=True) 
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        SQLEnum(UserRoleEnum, name='user_roles'),
        nullable=False,
        default=UserRoleEnum.regular
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
    
class Model(db.Model):
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    owner_user = db.relationship('User', backref='models', lazy='joined')

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    owner_user = db.relationship('User', backref='games', lazy='joined')
    
class GameAction(db.Model):
    __tablename__ = 'game_actions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    game_id = db.Column(
        db.Integer, 
        db.ForeignKey('games.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    game = db.relationship('Game', backref='actions', lazy='joined')

class GameActionScore(db.Model):
    __tablename__ = 'game_action_scores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(
        db.Integer, 
        db.ForeignKey('games.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    self_action_id = db.Column(
        db.Integer, 
        db.ForeignKey('game_actions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    opponent_action_id = db.Column(
        db.Integer, 
        db.ForeignKey('game_actions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    game = db.relationship('Game', backref='action_scores', lazy='joined')

    self_action = db.relationship(
        'GameAction',
        foreign_keys=[self_action_id],
        backref='self_action_scores',
        lazy='joined'
    )

    opponent_action = db.relationship(
        'GameAction',
        foreign_keys=[opponent_action_id],
        backref='opponent_action_scores',
        lazy='joined'
    )

class UserGame(db.Model):
    __tablename__ = 'user_games'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(
        db.Integer, 
        db.ForeignKey('games.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    session_id = db.Column(
        db.Integer, 
        db.ForeignKey('sessions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    model_id = db.Column(
        db.Integer, 
        db.ForeignKey('models.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    rounds = db.Column(db.Integer, nullable=False)
    user_score = db.Column(db.Float, default=0.0)
    model_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    session = db.relationship('Session', backref='user_games', lazy='joined')
    game = db.relationship('Game', backref='user_games', lazy='joined')
    model = db.relationship('Model', backref='user_games', lazy='joined')

class UserGameAction(db.Model):
    __tablename__ = 'user_game_actions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_game_id = db.Column(
        db.Integer, 
        db.ForeignKey('user_games.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    action_id = db.Column(
        db.Integer, 
        db.ForeignKey('game_actions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    owner_role = db.Column(
        SQLEnum(UserGameActionRoleEnum, name='user_game_action_roles'),
        nullable=False
    )
    round_number = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    user_game = db.relationship('UserGame', backref='user_game_actions', lazy='joined')
    action = db.relationship('GameAction', backref='user_game_actions', lazy='joined')