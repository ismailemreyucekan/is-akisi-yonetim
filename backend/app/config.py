
import os
from app.database import db_config

class Config:
    
    # SQLAlchemy veritabanı URI'si
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  
    
    # Flask yapılandırması
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

