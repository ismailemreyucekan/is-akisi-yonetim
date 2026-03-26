
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.logger import log_success, log_error


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            log_success("Tablolar oluşturuldu/kontrol edildi")
        except Exception as e:
            log_error(f"Tablolar oluşturulurken hata oluştu: {e}")
            raise

