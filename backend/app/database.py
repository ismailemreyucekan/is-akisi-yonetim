"""
Veritabanı bağlantı yapılandırması
NOT: Artık Alembic migration'ları kullanılıyor. 
Tablo oluşturma için: alembic upgrade head
"""
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

