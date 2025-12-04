# İş Akışı Yönetimi Backend (Python/FastAPI)

Bu backend, iş akışı (workflow) ve issue yönetimi için Python FastAPI kullanılarak geliştirilmiştir.

## Özellikler

- ✅ Workflow CRUD işlemleri
- ✅ Issue yönetimi (Task, Bug, Story, Epic)
- ✅ Issue durum yönetimi (To Do → In Progress → Done)
- ✅ Yorum ekleme/silme
- ✅ Alt görev (subtask) yönetimi
- ✅ Dosya ekleme (attachment) - şimdilik URL bazlı
- ✅ In-memory veri saklama (uygulama yeniden başlatıldığında sıfırlanır)

## Kurulum

### 1. Python Sanal Ortamı Oluştur

```bash
python -m venv venv
```

### 2. Sanal Ortamı Aktif Et

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

## Çalıştırma

### Development Modu

```bash
python main.py
```

veya

```bash
uvicorn main:app --reload --port 3001
```

### Production Modu

```bash
uvicorn main:app --host 0.0.0.0 --port 3001
```

## API Endpoints

### Workflows

- `GET /api/workflows` - Tüm iş akışlarını listele
- `GET /api/workflows/{id}` - Tek bir iş akışını getir
- `POST /api/workflows` - Yeni iş akışı oluştur
- `PUT /api/workflows/{id}` - İş akışını güncelle
- `DELETE /api/workflows/{id}` - İş akışını sil

### Issues

- `GET /api/issues` - Tüm issue'ları listele (filtreleme: `?type=bug&status=todo`)
- `GET /api/issues/{id}` - Tek bir issue'yu getir
- `POST /api/issues` - Yeni issue oluştur
- `PUT /api/issues/{id}` - Issue'yu güncelle
- `DELETE /api/issues/{id}` - Issue'yu sil

### Issue Comments

- `POST /api/issues/{id}/comments` - Yorum ekle
- `DELETE /api/issues/{id}/comments/{comment_id}` - Yorum sil

### Issue Subtasks

- `POST /api/issues/{id}/subtasks` - Alt görev ekle
- `PUT /api/issues/{id}/subtasks/{subtask_id}` - Alt görevi güncelle
- `DELETE /api/issues/{id}/subtasks/{subtask_id}` - Alt görevi sil

### Issue Attachments

- `POST /api/issues/{id}/attachments` - Dosya ekle (URL)
- `DELETE /api/issues/{id}/attachments/{attachment_id}` - Dosya sil

## API Dokümantasyonu

FastAPI otomatik olarak interaktif API dokümantasyonu sağlar:

- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## Örnek Request'ler

### Workflow Oluştur

```json
POST /api/workflows
{
  "ad": "Yeni İş Akışı",
  "aciklama": "Açıklama",
  "status": "active",
  "adimlar": [],
  "baglantilar": []
}
```

### Issue Oluştur

```json
POST /api/issues
{
  "title": "Bug: Login hatası",
  "type": "bug",
  "status": "todo",
  "priority": "high",
  "description": "Kullanıcı giriş yapamıyor",
  "assignee": "Ahmet Yılmaz",
  "tags": ["frontend", "urgent"]
}
```

### Yorum Ekle

```json
POST /api/issues/1/comments
{
  "author": "Mehmet Demir",
  "text": "Bu sorunu çözdüm, test edebilirsiniz."
}
```

## Notlar

- Veriler şu an **in-memory** olarak saklanıyor. Uygulama yeniden başlatıldığında tüm veriler sıfırlanır.
- İleride PostgreSQL veya başka bir veritabanı entegrasyonu yapılabilir.
- CORS ayarları şu an tüm origin'lere açık. Production'da spesifik origin'ler belirtilmeli.

