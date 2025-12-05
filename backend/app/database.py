"""
Veritabanı bağlantı yapılandırması
"""
import psycopg2
from app.logger import log_operation, log_error, log_success

# Ortam değişkeninden parola alınıyor
# psql_password = os.getenv("PSQL_PASSWORD")
psql_password = "12345678"

# Bağlantı bilgileri
db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "is_akis",
    "user": "postgres",
    "password": psql_password
}

def create_identities_table():
    """Kimlik (identities) tablosunu oluşturur"""
    try:
        log_operation("Veritabanı bağlantısı açılıyor")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        log_operation("Identities tablosu oluşturuluyor")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identities (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_type VARCHAR(20) NOT NULL DEFAULT 'user'
            )
        """)
        
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'identities_email_user_type_key'
                ) THEN
                    ALTER TABLE identities 
                    ADD CONSTRAINT identities_email_user_type_key 
                    UNIQUE (email, user_type);
                END IF;
            END $$;
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_identities_email 
            ON identities(email)
        """)
        
        conn.commit()
        log_success("Identities tablosu oluşturuldu")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log_error(f"Tablo oluşturma hatası: {e}")
        return False

if __name__ == "__main__":
    """Script olarak çalıştırıldığında tabloyu oluştur"""
    create_identities_table()

