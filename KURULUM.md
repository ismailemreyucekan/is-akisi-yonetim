# İş Akışı Yönetimi - Kurulum Kılavuzu

## Gereksinimler

- Node.js (v16 veya üzeri)
- PostgreSQL (v12 veya üzeri)
- npm veya yarn

## 1. Backend Kurulumu

### Adım 1: Bağımlılıkları Yükleyin

```bash
cd backEnd
npm install
```

### Adım 2: Veritabanını Oluşturun

PostgreSQL'e bağlanın ve veritabanını oluşturun (eğer yoksa):

```sql
CREATE DATABASE is_akis;
```

**Not:** Eğer `is_akis` veritabanı zaten varsa (görseldeki gibi), bu adımı atlayabilirsiniz.

### Adım 3: Tabloyu Oluşturun

```bash
psql -U postgres -d is_akis -f database/init.sql
```

veya PostgreSQL yönetim aracınızda (pgAdmin, DBeaver vb.) `is_akis` veritabanına bağlanıp `database/init.sql` dosyasını çalıştırın.

veya PostgreSQL'e bağlanıp `database/init.sql` dosyasını çalıştırın.

### Adım 4: Ortam Değişkenlerini Ayarlayın

`backEnd` klasöründe `.env` dosyası oluşturun:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=is_akis
DB_USER=postgres
DB_PASSWORD=your_password

# Server Configuration
PORT=3001
NODE_ENV=development
```

**Önemli:** `DB_NAME=is_akis` olarak ayarlayın (görseldeki veritabanı adı).

### Adım 5: Backend'i Başlatın

```bash
npm start
```

Geliştirme modu için:
```bash
npm run dev
```

Backend `http://localhost:3001` adresinde çalışacaktır.

## 2. Frontend Kurulumu

### Adım 1: Bağımlılıkları Yükleyin

```bash
cd frontEnd
npm install
```

### Adım 2: Frontend'i Başlatın

```bash
npm run dev
```

Frontend `http://localhost:5173` (veya başka bir port) adresinde çalışacaktır.

## 3. Veritabanı Yapısı

### is_akisi Tablosu

- `id` - SERIAL PRIMARY KEY (Otomatik artan ID)
- `ad` - VARCHAR(255) NOT NULL (İş akışı adı)
- `aciklama` - TEXT (İş akışı açıklaması)
- `adimlar` - JSONB (Adım dizisi - JSON formatında)
- `baglantilar` - JSONB (Bağlantı dizisi - JSON formatında)
- `olusturma_tarihi` - TIMESTAMP (Oluşturulma tarihi)
- `guncelleme_tarihi` - TIMESTAMP (Güncelleme tarihi)

### Örnek Veri Yapısı

**adimlar (JSONB):**
```json
[
  {
    "id": "1",
    "name": "Başlangıç",
    "type": "start",
    "description": "İş akışı başlangıcı",
    "position": { "x": 100, "y": 100 }
  },
  {
    "id": "2",
    "name": "Görev 1",
    "type": "task",
    "description": "İlk görev",
    "position": { "x": 300, "y": 100 }
  }
]
```

**baglantilar (JSONB):**
```json
[
  {
    "id": "conn-1-2",
    "fromStepId": "1",
    "toStepId": "2"
  }
]
```

## 4. API Endpoints

### İş Akışları

- `GET /api/workflows` - Tüm iş akışlarını getir
- `GET /api/workflows/:id` - Tek bir iş akışını getir
- `POST /api/workflows` - Yeni iş akışı oluştur
- `PUT /api/workflows/:id` - İş akışını güncelle
- `DELETE /api/workflows/:id` - İş akışını sil

### Örnek Kullanım

**Yeni iş akışı oluştur:**
```bash
curl -X POST http://localhost:3001/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "ad": "Test İş Akışı",
    "aciklama": "Test açıklaması",
    "adimlar": [],
    "baglantilar": []
  }'
```

## 5. Sorun Giderme

### Backend bağlantı hatası

- PostgreSQL servisinin çalıştığından emin olun
- `.env` dosyasındaki veritabanı bilgilerini kontrol edin
- Veritabanının oluşturulduğundan emin olun

### CORS hatası

- Backend'de CORS middleware'inin aktif olduğundan emin olun
- Frontend ve backend portlarının farklı olduğundan emin olun

### Veritabanı hatası

- PostgreSQL kullanıcı adı ve şifresinin doğru olduğundan emin olun
- Veritabanı tablosunun oluşturulduğundan emin olun
- `database/init.sql` dosyasını çalıştırdığınızdan emin olun

## 6. Notlar

- Backend ve Frontend aynı anda çalışmalıdır
- Backend varsayılan olarak 3001 portunda çalışır
- Frontend API çağrılarını `http://localhost:3001` adresine yapar
- Veritabanı bağlantı bilgileri `.env` dosyasında saklanır (güvenlik için `.gitignore`'a eklenmiştir)

