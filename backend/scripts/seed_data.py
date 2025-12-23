
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from app import create_app
from app.models import db, Identity
from app.logger import log_operation, log_success

def hash_password(password):
    
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_data():
   
    app = create_app()
    with app.app_context():
        log_operation("Seed data işlemi başlatıldı")
        
        users_data = [
            ('ismail.yucekan@vbt.com.tr', 'user123', 'Kullanıcı', 'Bir', 'user'),
            ('serkan.demirci@vbt.com.tr', 'user123', 'Kullanıcı', 'İki', 'user'),
        ]
        
        admins_data = [
            ('admin@example.com', 'admin123', 'Admin', 'Kullanıcı', 'admin'),
        ]
        
        for email, password, first_name, last_name, user_type in users_data + admins_data:
            existing_identity = Identity.query.filter_by(email=email, user_type=user_type).first()
            if not existing_identity:
                password_hash = hash_password(password)
                identity = Identity(
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=user_type
                )
                db.session.add(identity)
                log_success(f"Kullanıcı eklendi: {first_name} {last_name} ({email})")
        
        db.session.commit()
        log_success("Seed data işlemi tamamlandı")

if __name__ == "__main__":
    seed_data()

