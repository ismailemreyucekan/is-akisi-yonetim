# Veritabanı Tablosu Oluşturma

500 hatası alıyorsanız, muhtemelen `is_akisi` tablosu oluşturulmamıştır.

## Hızlı Çözüm

### Yöntem 1: pgAdmin veya DBeaver ile

1. PostgreSQL yönetim aracınızı açın (pgAdmin, DBeaver, vb.)
2. `is_akis` veritabanına bağlanın
3. SQL Editor/Query Tool açın
4. `database/init.sql` dosyasının içeriğini kopyalayıp yapıştırın
5. Çalıştırın (F5 veya Execute)

### Yöntem 2: psql Komut Satırı ile

```bash
psql -U postgres -d is_akis -f database/init.sql
```

### Yöntem 3: Manuel SQL

PostgreSQL'e bağlanın ve şu SQL'i çalıştırın:

```sql
-- İş Akışları tablosu
CREATE TABLE IF NOT EXISTS is_akisi (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    aciklama TEXT,
    adimlar JSONB NOT NULL DEFAULT '[]'::jsonb,
    baglantilar JSONB NOT NULL DEFAULT '[]'::jsonb,
    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Güncelleme tarihi için trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.guncelleme_tarihi = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_is_akisi_updated_at 
    BEFORE UPDATE ON is_akisi
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_is_akisi_ad ON is_akisi(ad);
CREATE INDEX IF NOT EXISTS idx_is_akisi_olusturma_tarihi ON is_akisi(olusturma_tarihi);
```

## Doğrulama

Tablo oluşturulduktan sonra, backend terminalinde şunu görmelisiniz:

```
✅ Veritabanı bağlantısı başarılı
✅ 0 iş akışı bulundu
```

Veya PostgreSQL'de kontrol edin:

```sql
SELECT * FROM is_akisi;
```

Boş bir tablo görmelisiniz (henüz veri yok).

