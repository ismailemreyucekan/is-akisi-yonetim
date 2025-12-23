import { useEffect, useState } from 'react'
import './LoginPage.css'

const API_URL = 'http://localhost:5000/api'

const UserDashboard = ({ user, onLogout }) => {
  const [timesheets, setTimesheets] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedMonth, setSelectedMonth] = useState(new Date())
  const [formData, setFormData] = useState({
    work_date: new Date().toISOString().split('T')[0],
    project: '',
    activity_type: '',
    work_mode: 'Ofis',
    hours: '',
    description: '',
  })
  const [durationHours, setDurationHours] = useState('')
  const [durationMinutes, setDurationMinutes] = useState('0')
  const [showModal, setShowModal] = useState(false)
  const [modalDate, setModalDate] = useState(new Date())
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const activityOptions = [
    'Geliştirme',
    'Eğitim',
    'İzin',
    'Toplantı',
    'Destek',
    'Analiz',
  ]

  const projectOptions = [
    'Portal Geliştirme',
    'Mobil Uygulama',
    'Raporlama',
    'Altyapı',
    'Ar-Ge',
  ]

  const getMonthRange = (dateObj) => {
    const start = new Date(dateObj.getFullYear(), dateObj.getMonth(), 1)
    const end = new Date(dateObj.getFullYear(), dateObj.getMonth() + 1, 0)
    return { start, end }
  }

  const formatDateKey = (d) => {
    if (!d) return ''
    const date = typeof d === 'string' ? new Date(d) : d
    return date.toISOString().split('T')[0]
  }

  const buildMonthDays = (dateObj) => {
    const { start, end } = getMonthRange(dateObj)
    const startWeekDay = (start.getDay() + 6) % 7 // Pazartesi
    const days = []
    for (let i = 0; i < startWeekDay; i++) days.push({ label: '', date: null, currentMonth: false })
    for (let d = 1; d <= end.getDate(); d++) {
      const dayDate = new Date(start.getFullYear(), start.getMonth(), d)
      days.push({ label: d, date: dayDate, currentMonth: true })
    }
    while (days.length % 7 !== 0) days.push({ label: '', date: null, currentMonth: false })
    return days
  }

  const dayNames = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
  // Hafta içi gri, Cumartesi lila, Pazar pembe
  const dayColors = ['#f5f6fa', '#f5f6fa', '#f5f6fa', '#f5f6fa', '#f5f6fa', '#f7f7ff', '#fff5f5']

  const getTimesheetStatusClass = (status) => {
    switch (status) {
      case 'Taslak':
        return 'pill-draft'
      case 'Onay Bekliyor':
        return 'pill-pending'
      case 'Onaylandı':
        return 'pill-success'
      case 'Reddedildi':
        return 'pill-danger'
      default:
        return 'pill-muted'
    }
  }

  const fetchTimesheets = async (month = selectedMonth) => {
    try {
      setLoading(true)
      const { start, end } = getMonthRange(month)
      const params = new URLSearchParams({
        user_id: user.id,
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0],
        include_drafts: 'true',
      })
      const res = await fetch(`${API_URL}/timesheets?${params.toString()}`)
      const data = await res.json()
      if (data.success) setTimesheets(data.timesheets || [])
    } catch (err) {
      console.error(err)
      setError('Timesheet listelenemedi')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTimesheets(selectedMonth)
  }, [selectedMonth])

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const openDayModal = (dateObj) => {
    if (!dateObj) return
    const iso = dateObj.toISOString().split('T')[0]
    setModalDate(dateObj)
    setFormData((prev) => ({ ...prev, work_date: iso }))
    setDurationHours('')
    setDurationMinutes('0')
    setError('')
    setSuccess('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    const totalHours = Number(durationHours || 0) + Number(durationMinutes || 0) / 60
    if (!formData.project || !formData.activity_type || !formData.work_mode || totalHours <= 0 || !formData.work_date) {
      setError('Tüm zorunlu alanları doldurun ve süreyi girin')
      return
    }
    try {
      const res = await fetch(`${API_URL}/timesheets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          hours: totalHours,
          identity_id: user.id,
        }),
      })
      const data = await res.json()
      if (data.success) {
        setSuccess('Timesheet kaydedildi')
        await fetchTimesheets(selectedMonth)
        setFormData((prev) => ({
          ...prev,
          project: '',
          activity_type: '',
          description: '',
        }))
        setDurationHours('')
        setDurationMinutes('0')
        setShowModal(false)
      } else {
        setError(data.message || 'Kaydedilemedi')
      }
    } catch (err) {
      console.error(err)
      setError('Kaydetme sırasında hata')
    }
  }

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">İ</div>
          <div>
            <div className="brand-title">İş Akış Yönetim Sistemi</div>
            <div className="brand-subtitle">Timesheet</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-item active">
            <span className="nav-icon">⏱️</span>
            <span>Timesheet</span>
          </div>
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            {user.first_name?.[0]}
            {user.last_name?.[0]}
          </div>
          <div className="user-meta">
            <div className="user-name">
              {user.first_name} {user.last_name}
            </div>
            <div className="user-role">kullanıcı</div>
          </div>
        </div>
      </aside>

      <main className="admin-main">
        <header className="main-header">
          <div>
            <p className="page-kicker">Günlük girişlerinizi kaydedin</p>
            <h1 className="page-title">Timesheet</h1>
          </div>
          <div className="header-actions">
            <button className="ghost-button" onClick={onLogout}>
              Çıkış
            </button>
          </div>
        </header>

        <section className="table-card">
          <div className="table-toolbar">
            <div className="toolbar-left">
              <p className="page-kicker">Kayıtlarınız</p>
              <h2 className="page-title" style={{ fontSize: '20px', margin: 0 }}>Takvim</h2>
            </div>
          </div>

          {loading ? (
            <div className="loading-state">Timesheet yükleniyor...</div>
          ) : (
            <>
              <div className="calendar-grid">
                {['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'].map((d) => (
                  <div key={d} className="calendar-head">{d}</div>
                ))}
                {buildMonthDays(selectedMonth).map((day, idx) => {
                  const key = day.date ? formatDateKey(day.date) : `empty-${idx}`
                  const entries = day.date ? timesheets.filter((t) => formatDateKey(t.work_date) === formatDateKey(day.date)) : []
                  const totalHours = entries.reduce((sum, e) => sum + (e.hours || 0), 0)
                  const dow = day.date ? (day.date.getDay() + 6) % 7 : idx % 7
                  return (
                    <div
                      key={key}
                      className={`calendar-cell ${day.currentMonth ? '' : 'calendar-cell--muted'}`}
                      onClick={() => day.currentMonth && openDayModal(day.date)}
                      style={{ cursor: day.currentMonth ? 'pointer' : 'default', background: day.currentMonth ? (dayColors[dow] || '#f8fafc') : undefined }}
                    >
                      <div className="calendar-cell-header">
                        <div className="calendar-date-block">
                          <div className="calendar-date">{day.label}</div>
                          <div className="calendar-dayname">{day.date ? dayNames[dow] : ''}</div>
                        </div>
                        {totalHours > 0 && (
                          <div className="day-hours-badge">
                            {totalHours.toFixed(1)}s
                          </div>
                        )}
                      </div>
                      <div className="calendar-entries">
                        {entries.slice(0, 2).map((t) => (
                          <div
                            key={t.id}
                            className={`calendar-entry ${
                              t.status === 'Taslak'
                                ? 'status-draft'
                                : t.status === 'Onay Bekliyor'
                                ? 'status-pending'
                                : t.status === 'Onaylandı'
                                ? 'status-success'
                                : t.status === 'Reddedildi'
                                ? 'status-danger'
                                : ''
                            }`}
                          >
                            <div className="entry-title">{t.project}</div>
                            <div className="entry-meta">
                              <span>{t.hours} saat</span>
                              <span className={`pill pill-status ${getTimesheetStatusClass(t.status)}`}>
                                {t.status}
                              </span>
                            </div>
                            <div className="entry-desc">
                              {t.description || t.activity_type}
                              {t.status === 'Reddedildi' && t.reject_reason ? ` • Neden: ${t.reject_reason}` : ''}
                            </div>
                            {t.status === 'Taslak' && (
                              <div className="entry-actions">
                                <button
                                  className="ghost-button"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    setShowModal(true)
                                    setModalDate(new Date(t.work_date))
                                    setFormData({
                                      work_date: t.work_date.split('T')[0],
                                      project: t.project,
                                      activity_type: t.activity_type,
                                      work_mode: t.work_mode,
                                      description: t.description || '',
                                    })
                                    const hrs = Math.floor(t.hours)
                                    const mins = Math.round((t.hours - hrs) * 60)
                                    setDurationHours(String(hrs))
                                    setDurationMinutes(String(mins))
                                  }}
                                >
                                  Düzenle
                                </button>
                                <button
                                  className="primary-button"
                                  onClick={async (e) => {
                                    e.stopPropagation()
                                    try {
                                      await fetch(`${API_URL}/timesheets/${t.id}`, {
                                        method: 'PUT',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ status: 'Onay Bekliyor' })
                                      })
                                      await fetchTimesheets(selectedMonth)
                                    } catch (err) {
                                      console.error(err)
                                    }
                                  }}
                                >
                                  Onaya Gönder
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                        {entries.length > 2 && (
                          <div className="entry-more">+{entries.length - 2} kayıt</div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
              {timesheets.length === 0 && (
                <div className="loading-state">Bu ay için timesheet kaydı bulunamadı</div>
              )}
            </>
          )}
        </section>
      </main>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Timesheet Ekle ({modalDate?.toLocaleDateString('tr-TR')})</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form className="modal-form" onSubmit={handleSubmit}>
              {error && <div className="error-message">{error}</div>}
              {success && <div className="error-message" style={{ background: '#ecfdf3', borderColor: '#86efac', color: '#16a34a' }}>{success}</div>}

              <div className="form-group">
                <label>Tarih *</label>
                <input type="date" name="work_date" value={formData.work_date} onChange={handleInputChange} required />
              </div>

              <div className="form-group">
                <label>Proje *</label>
                <select name="project" value={formData.project} onChange={handleInputChange} required>
                  <option value="">Seçiniz</option>
                  {projectOptions.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Aktivite Tipi *</label>
                <select name="activity_type" value={formData.activity_type} onChange={handleInputChange} required>
                  <option value="">Seçiniz</option>
                  {activityOptions.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Çalışma Şekli *</label>
                <select name="work_mode" value={formData.work_mode} onChange={handleInputChange} required>
                  <option value="Ofis">Ofis</option>
                  <option value="Uzaktan">Uzaktan</option>
                  
                </select>
              </div>

              <div className="form-group">
                <label>Çalışılan Süre *</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    placeholder="Saat"
                    value={durationHours}
                    onChange={(e) => setDurationHours(e.target.value)}
                    style={{ flex: 1 }}
                    required
                  />
                  <input
                    type="number"
                    min="0"
                    max="59"
                    step="1"
                    placeholder="Dakika"
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(e.target.value)}
                    style={{ width: '90px' }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Açıklama</label>
                <textarea
                  className="textarea"
                  rows={3}
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Yapılan iş / not"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="ghost-button" onClick={() => setShowModal(false)}>Kapat</button>
                <button type="submit" className="primary-button">Kaydet</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserDashboard

