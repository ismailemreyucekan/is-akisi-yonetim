"""
Eski yöntem: Kullanıcı ve admin tablolarını oluşturur
NOT: Migration kullanılıyorsa bu dosya gerekli değildir.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from app.database import db_config

def create_tables():
    """Kimlik tablosunu oluşturur"""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Kimlik tablosu (users ve admins için tek tablo)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identities (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_type VARCHAR(20) NOT NULL DEFAULT 'user'
            )
        """)
        
        # Email ve user_type kombinasyonu için unique index
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_identities_email_user_type 
            ON identities(email, user_type)
        """)
        
        conn.commit()
        print("Kimlik tablosu başarıyla oluşturuldu!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    create_tables()

