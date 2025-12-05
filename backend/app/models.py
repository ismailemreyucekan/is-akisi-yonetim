"""
Veritabanı modelleri
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Identity(db.Model):
    """Kimlik modeli - Tüm kullanıcılar ve adminler için tek tablo"""
    __tablename__ = 'identities'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='user')  # 'user' veya 'admin'
    
    def __repr__(self):
        return f'<Identity {self.email} ({self.user_type})>'
    
    def to_dict(self):
        """Modeli dictionary'ye dönüştürür"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_type': self.user_type
        }

