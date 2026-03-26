"""
Timesheet settings varsayılanlarını ekler.

Bu script, duplikasyon azaltmak için `backend/scripts/seed_data.py` içindeki
seed fonksiyonlarını wrapper olarak çağırır.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.logger import log_operation, log_success, log_error
from scripts.seed_data import seed_timesheet_settings


def create_table():
    """Timesheet settings tablosu ve varsayılan verileri oluşturur."""
    app = create_app()
    with app.app_context():
        log_operation("Timesheet settings tablosu oluşturuluyor...")

        try:
            db.create_all()
            seed_timesheet_settings()
            db.session.commit()
            log_success("Timesheet settings varsayılanları eklendi")
        except Exception as e:
            db.session.rollback()
            log_error(f"Timesheet settings ekleme hatası: {e}")
            raise


if __name__ == "__main__":
    create_table()
