"""
Timesheet settings tablosunu oluşturur
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, TimesheetSetting
from app.logger import log_operation, log_success

def create_table():
    """Timesheet settings tablosunu oluşturur"""
    app = create_app()
    with app.app_context():
        log_operation("Timesheet settings tablosu oluşturuluyor...")
        
        try:
            # Tabloyu oluştur
            db.create_all()
            log_success("Tablo oluşturuldu/kontrol edildi")
            
            # Varsayılan verileri ekle
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
            
            db.session.commit()
            log_success("Timesheet settings tablosu ve varsayılan veriler başarıyla oluşturuldu!")
            
        except Exception as e:
            db.session.rollback()
            log_operation(f"Hata: {e}")
            raise

if __name__ == "__main__":
    create_table()
