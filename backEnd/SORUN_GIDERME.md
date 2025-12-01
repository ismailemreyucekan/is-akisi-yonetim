# Backend Sorun Giderme Kılavuzu

## 1. Bağımlılıkları Kontrol Edin

```bash
cd backEnd
npm install
```

## 2. .env Dosyasını Kontrol Edin

`backEnd` klasöründe `.env` dosyası olmalı:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=is_akis
DB_USER=postgres
DB_PASSWORD=şifreniz_buraya
PORT=3001
NODE_ENV=development
```

## 3. PostgreSQL Bağlantısını Test Edin

```bash
npm run test-db
```

## 4. Backend'i Başlatın

```bash
npm start
```

## 5. Yaygın Hatalar ve Çözümleri

### Hata: "SASL: SCRAM-SERVER-FIRST-MESSAGE: client password must be a string"

**Çözüm:** PostgreSQL şifre gerektiriyor. İki seçenek:

**Seçenek 1 - Şifre Ayarlayın:**
```sql
psql -U postgres
ALTER USER postgres PASSWORD 'postgres123';
```

Sonra `.env` dosyasına:
```
DB_PASSWORD=postgres123
```

**Seçenek 2 - Trust Authentication:**
`pg_hba.conf` dosyasında:
```
host    all    all    127.0.0.1/32    trust
```
PostgreSQL'i yeniden başlatın.

### Hata: "Cannot find module"

**Çözüm:**
```bash
npm install
```

### Hata: "Port 3001 already in use"

**Çözüm:** Port'u değiştirin veya kullanan uygulamayı kapatın:
```env
PORT=3002
```

### Hata: ".env dosyası bulunamadı"

**Çözüm:** `backEnd` klasöründe `.env` dosyası oluşturun.

## 6. Backend Çalışıyor mu Kontrol Edin

Tarayıcıda veya Postman'de test edin:
```
http://localhost:3001/api/health
```

"OK" mesajı görmelisiniz.

