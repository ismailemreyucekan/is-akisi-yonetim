
import os

class Config:
    
    # SQLAlchemy veritabanı URI'si - doğrudan değerlerle oluştur
    # database.py'den import yerine doğrudan burada tanımlıyoruz
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:12345678@localhost:5432/is_akis"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  
    
    # Flask yapılandırması
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

