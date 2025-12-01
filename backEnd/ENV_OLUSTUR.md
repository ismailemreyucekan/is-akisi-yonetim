# .env Dosyası Oluşturma Kılavuzu

## Hızlı Kurulum

`backEnd` klasöründe `.env` dosyası oluşturun ve aşağıdaki içeriği ekleyin:

```env
# Database Configuration
# Not: localdb server adı genellikle localhost ile aynıdır
DB_HOST=localhost
DB_PORT=5432
DB_NAME=is_akis
DB_USER=postgres
# Şifre yoksa boş bırakın veya satırı tamamen kaldırın
DB_PASSWORD=

# Server Configuration
PORT=3001
NODE_ENV=development
```

**Önemli Notlar:**
- `DB_HOST=localhost` - localdb server'ı genellikle localhost'ta çalışır
- `DB_NAME=is_akis` - Görseldeki veritabanı adı
- `DB_PASSWORD=` - Şifre yoksa boş bırakın (satırı kaldırabilirsiniz de)

## Önemli Notlar

1. **DB_PASSWORD**: 
   - Eğer PostgreSQL şifreniz varsa: `DB_PASSWORD=gerçek_şifreniz`
   - Eğer şifre yoksa: `DB_PASSWORD=` (boş bırakın ama satırı ekleyin)

2. **Dosya Konumu**: 
   - `.env` dosyası `backEnd` klasörü içinde olmalı
   - Tam yol: `backEnd/.env`

3. **Dosya Adı**: 
   - Dosya adı tam olarak `.env` olmalı (nokta ile başlamalı)
   - `.env.txt` veya `env` değil, sadece `.env`

## Windows'ta .env Dosyası Oluşturma

### Yöntem 1: Notepad ile
1. `backEnd` klasörüne gidin
2. Yeni bir metin dosyası oluşturun
3. İçeriği yukarıdaki gibi doldurun
4. Dosyayı kaydedin
5. Dosya adını `.env` olarak değiştirin (uzantı olmadan)
6. Windows uyarı verirse "Evet" deyin

### Yöntem 2: PowerShell ile
```powershell
cd backEnd
@"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=is_akis
DB_USER=postgres
DB_PASSWORD=
PORT=3001
NODE_ENV=development
"@ | Out-File -FilePath .env -Encoding utf8
```

### Yöntem 3: VS Code ile
1. VS Code'da `backEnd` klasörünü açın
2. Yeni dosya oluşturun (Ctrl+N)
3. İçeriği yukarıdaki gibi yazın
4. Dosyayı `.env` olarak kaydedin

## Doğrulama

Backend'i başlattığınızda konsolda şunları görmelisiniz:

```
📋 Veritabanı Bağlantı Ayarları:
   Host: localhost
   Port: 5432
   Database: is_akis
   User: postgres
   Password: *** (veya boş - şifre yok)
```

Eğer `.env` dosyası bulunamadı uyarısı görürseniz, dosyanın doğru konumda olduğundan emin olun.

