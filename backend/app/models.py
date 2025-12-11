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
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='user')  # 'user' veya 'admin'
    # Yeni sütun
    phone_number = db.Column(db.String(20), nullable=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    
    
    
    def __repr__(self):
        return f'<Identity {self.email} ({self.user_type})>'
    
    def to_dict(self):
        """Modeli dictionary'ye dönüştürür"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_type': self.user_type,
            'phone_number': self.phone_number
        }


class Timesheet(db.Model):
    """Kullanıcı timesheet kayıtları"""
    __tablename__ = 'timesheets'

    id = db.Column(db.Integer, primary_key=True)
    identity_id = db.Column(db.Integer, db.ForeignKey('identities.id'), nullable=False, index=True)
    work_date = db.Column(db.Date, nullable=False, index=True)
    project = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)  # eğitim, geliştirme, izin vb
    work_mode = db.Column(db.String(50), nullable=False)       # ofis, uzaktan vb
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Onay Bekliyor')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'identity_id': self.identity_id,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'project': self.project,
            'activity_type': self.activity_type,
            'work_mode': self.work_mode,
            'hours': self.hours,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
