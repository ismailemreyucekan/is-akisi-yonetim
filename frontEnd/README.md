# İş Akışı Yönetim Sistemi - Frontend

Modern bir iş akışı (workflow) yönetim sistemi frontend uygulaması.

## Teknolojiler

- **React 18** - UI kütüphanesi
- **JavaScript (JSX)** - React bileşenleri
- **Vite** - Build tool ve dev server
- **React Router** - Sayfa yönlendirme
- **Lucide React** - İkon kütüphanesi

## Kurulum

```bash
# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev

# Production build
npm run build

# Build önizleme
npm run preview
```

## Proje Yapısı

```
src/
├── components/       # Yeniden kullanılabilir bileşenler
│   └── Layout.jsx   # Ana layout bileşeni
├── pages/           # Sayfa bileşenleri
│   ├── Dashboard.jsx
│   ├── WorkflowList.jsx
│   └── WorkflowEditor.jsx
├── App.jsx          # Ana uygulama bileşeni
├── main.jsx         # Uygulama giriş noktası
└── index.css        # Global stiller
```

## Özellikler

- 📊 **Dashboard** - İş akışı istatistikleri ve genel bakış
- 📋 **İş Akışı Listesi** - Tüm iş akışlarını görüntüleme ve yönetme
- ✏️ **İş Akışı Editörü** - Görsel iş akışı tasarımı ve düzenleme
- 🎨 **Modern UI/UX** - Kullanıcı dostu arayüz tasarımı
- 🔍 **Arama** - İş akışlarında arama özelliği
- 📱 **Responsive** - Mobil uyumlu tasarım

## Lisans

MIT
