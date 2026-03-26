
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from app import create_app
from app.models import db, Identity, TimesheetSetting
from app.logger import log_operation, log_success

def hash_password(password):
    
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_data():
   
    app = create_app()
    with app.app_context():
        log_operation("Seed data işlemi başlatıldı")
        
        # Önce tabloları oluştur (yoksa)
        try:
            db.create_all()
            log_success("Tablolar oluşturuldu/kontrol edildi")
        except Exception as e:
            log_operation(f"Tablolar zaten mevcut veya hata: {e}")
        
        users_data = [
            ('ismail.yucekan@vbt.com.tr', 'user123', 'Kullanıcı', 'Bir', 'user'),
            ('serkan.demirci@vbt.com.tr', 'user123', 'Kullanıcı', 'İki', 'user'),
        ]
        
        admins_data = [
            ('admin@example.com', 'admin123', 'Admin', 'Kullanıcı', 'admin'),
        ]
        
        for email, password, first_name, last_name, user_type in users_data + admins_data:
            existing_identity = Identity.query.filter_by(email=email).first()
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
            else:
                log_operation(f"Kullanıcı zaten mevcut: {email}")
        
        # Timesheet ayarları için varsayılan veriler
        default_projects = [
            'Portal Geliştirme',
            'Mobil Uygulama',
            'Raporlama',
            'Altyapı',
            'Ar-Ge',
        ]
        
        default_activity_types = [
            'Geliştirme',
            'Eğitim',
            'İzin',
            'Toplantı',
            'Destek',
            'Analiz',
        ]
        
        default_work_modes = [
            'Ofis',
            'Uzaktan',
        ]
        
        # Projeleri ekle
        for idx, project in enumerate(default_projects):
            existing = TimesheetSetting.query.filter_by(setting_type='project', value=project).first()
            if not existing:
                setting = TimesheetSetting(
                    setting_type='project',
                    value=project,
                    is_active=True,
                    display_order=idx
                )
                db.session.add(setting)
                log_success(f"Proje eklendi: {project}")
        
        # Aktivite tiplerini ekle
        for idx, activity in enumerate(default_activity_types):
            existing = TimesheetSetting.query.filter_by(setting_type='activity_type', value=activity).first()
            if not existing:
                setting = TimesheetSetting(
                    setting_type='activity_type',
                    value=activity,
                    is_active=True,
                    display_order=idx
                )
                db.session.add(setting)
                log_success(f"Aktivite tipi eklendi: {activity}")
        
        # Çalışma şekillerini ekle
        for idx, work_mode in enumerate(default_work_modes):
            existing = TimesheetSetting.query.filter_by(setting_type='work_mode', value=work_mode).first()
            if not existing:
                setting = TimesheetSetting(
                    setting_type='work_mode',
                    value=work_mode,
                    is_active=True,
                    display_order=idx
                )
                db.session.add(setting)
                log_success(f"Çalışma şekli eklendi: {work_mode}")
        
        try:
            db.session.commit()
            log_success("Seed data işlemi tamamlandı")
        except Exception as e:
            db.session.rollback()
            log_operation(f"Hata: {e}")
            raise

if __name__ == "__main__":
    seed_data()

