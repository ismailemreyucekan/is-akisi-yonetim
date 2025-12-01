# İş Akışı Yönetimi Backend API

## Kurulum

1. Bağımlılıkları yükleyin:
```bash
npm install
```

2. `.env` dosyasını oluşturun (`.env.example` dosyasını kopyalayın):
```bash
cp .env.example .env
```

3. `.env` dosyasında veritabanı bilgilerinizi güncelleyin:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=is_akis
DB_USER=postgres
DB_PASSWORD=your_password
```

**Not:** `DB_NAME=is_akis` olarak ayarlayın (mevcut veritabanı adı).

4. PostgreSQL veritabanını oluşturun (eğer yoksa):
```sql
CREATE DATABASE is_akis;
```

**Not:** Eğer `is_akis` veritabanı zaten varsa, bu adımı atlayabilirsiniz.

5. Veritabanı tablosunu oluşturun:
```bash
psql -U postgres -d is_akis -f database/init.sql
```

veya PostgreSQL'e bağlanıp `database/init.sql` dosyasını çalıştırın.

6. Sunucuyu başlatın:
```bash
npm start
```

Geliştirme modu için:
```bash
npm run dev
```

## API Endpoints

- `GET /api/workflows` - Tüm iş akışlarını getir
- `GET /api/workflows/:id` - Tek bir iş akışını getir
- `POST /api/workflows` - Yeni iş akışı oluştur
- `PUT /api/workflows/:id` - İş akışını güncelle
- `DELETE /api/workflows/:id` - İş akışını sil

## Veritabanı Yapısı

### is_akisi Tablosu

- `id` - SERIAL PRIMARY KEY
- `ad` - VARCHAR(255) NOT NULL
- `aciklama` - TEXT
- `adimlar` - JSONB (adım dizisi)
- `baglantilar` - JSONB (bağlantı dizisi)
- `olusturma_tarihi` - TIMESTAMP
- `guncelleme_tarihi` - TIMESTAMP

