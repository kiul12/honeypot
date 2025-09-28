from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    theme_preference = db.Column(db.String(10), default='light', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class AttackerProfile(db.Model):
    __tablename__ = 'attacker_profiles'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), index=True, nullable=False)
    user_agent = db.Column(db.String(255))
    asn = db.Column(db.String(32))
    isp = db.Column(db.String(128))
    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    tags = db.Column(db.JSON, nullable=True)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    attacks = db.relationship('AttackEvent', backref='attacker', lazy=True)


class AttackEvent(db.Model):
    __tablename__ = 'attack_events'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), index=True, nullable=False)
    method = db.Column(db.String(16))
    path = db.Column(db.String(255))
    headers = db.Column(db.JSON)
    payload = db.Column(db.JSON)
    honeypot_service = db.Column(db.String(64))
    signature = db.Column(db.String(128))
    severity = db.Column(db.String(16))

    attacker_id = db.Column(db.Integer, db.ForeignKey('attacker_profiles.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'method': self.method,
            'path': self.path,
            'headers': self.headers,
            'payload': self.payload,
            'honeypot_service': self.honeypot_service,
            'signature': self.signature,
            'severity': self.severity,
            'attacker_id': self.attacker_id,
        }


