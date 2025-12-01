import express from 'express'

const router = express.Router()

// Geçici bellek içi (in-memory) veri yapısı
// Uygulama yeniden başlatıldığında bu veriler sıfırlanır.
let workflows = []
let nextId = 1

// Route'ların yüklendiğini logla
console.log('✅ Workflows router (in-memory) yüklendi')

// Tüm iş akışlarını getir
router.get('/', (req, res) => {
  console.log('📥 GET /api/workflows isteği alındı (in-memory)')
  res.json(workflows)
})

// Tek bir iş akışını getir
router.get('/:id', (req, res) => {
  const { id } = req.params
  const workflow = workflows.find(w => w.id === Number(id))

  if (!workflow) {
    return res.status(404).json({ error: 'İş akışı bulunamadı' })
  }

  res.json(workflow)
})

// Yeni iş akışı oluştur (in-memory)
router.post('/', (req, res) => {
  console.log('📥 POST /api/workflows isteği alındı (in-memory)')
  console.log('   Body:', JSON.stringify(req.body, null, 2))
  
  const { ad, aciklama, adimlar, baglantilar, status } = req.body

  if (!ad) {
    return res.status(400).json({ error: 'İş akışı adı gereklidir' })
  }

  const now = new Date().toISOString()

  const newWorkflow = {
    id: nextId++,
    ad,
    aciklama: aciklama || null,
    adimlar: adimlar || [],
    baglantilar: baglantilar || [],
    status: status || 'draft',
    olusturma_tarihi: now,
    guncelleme_tarihi: now
  }

  workflows.unshift(newWorkflow)

  res.status(201).json(newWorkflow)
})

// İş akışını güncelle (in-memory)
router.put('/:id', (req, res) => {
  const { id } = req.params
  const { ad, aciklama, adimlar, baglantilar, status } = req.body

  if (!ad) {
    return res.status(400).json({ error: 'İş akışı adı gereklidir' })
  }

  const index = workflows.findIndex(w => w.id === Number(id))

  if (index === -1) {
    return res.status(404).json({ error: 'İş akışı bulunamadı' })
  }

  const existing = workflows[index]
  const now = new Date().toISOString()

  const updated = {
    ...existing,
    ad,
    aciklama: aciklama ?? existing.aciklama,
    adimlar: adimlar ?? existing.adimlar,
    baglantilar: baglantilar ?? existing.baglantilar,
    status: status ?? existing.status ?? 'draft',
    guncelleme_tarihi: now
  }

  workflows[index] = updated

  res.json(updated)
})

// İş akışını sil (in-memory)
router.delete('/:id', (req, res) => {
  const { id } = req.params
  const index = workflows.findIndex(w => w.id === Number(id))

  if (index === -1) {
    return res.status(404).json({ error: 'İş akışı bulunamadı' })
  }

  const [deleted] = workflows.splice(index, 1)

  res.json({ message: 'İş akışı başarıyla silindi', id: deleted.id })
})

export default router

