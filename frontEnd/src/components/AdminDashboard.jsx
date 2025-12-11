import { useState, useEffect } from 'react'
import './LoginPage.css'

const API_URL = 'http://localhost:5000/api'

const AdminDashboard = ({ user, onLogout }) => {
  const [users, setUsers] = useState([])
  const [filteredUsers, setFilteredUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    user_type: 'user',
    phone_number: ''
  })
  const [error, setError] = useState('')
  const [timesheets, setTimesheets] = useState([])
  const [timesheetLoading, setTimesheetLoading] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState(null)
  const [selectedMonth, setSelectedMonth] = useState(new Date())
  const [activeSection, setActiveSection] = useState('users') // 'users' | 'timesheet'

  // Kullanıcıları yükle
  useEffect(() => {
    fetchUsers()
  }, [])

  // Arama filtresi
  useEffect(() => {
    if (searchTerm) {
      const filtered = users.filter(u => {
        const fullName = `${u.first_name} ${u.last_name}`.toLowerCase()
        const email = u.email.toLowerCase()
        const search = searchTerm.toLowerCase()
        return fullName.includes(search) || email.includes(search)
      })
      setFilteredUsers(filtered)
    } else {
      setFilteredUsers(users)
    }
  }, [searchTerm, users])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/users`)
      const data = await response.json()
      
      if (data.success) {
        setUsers(data.users)
        setFilteredUsers(data.users)
        if (!selectedUserId && data.users.length > 0) {
          setSelectedUserId(data.users[0].id)
        }
        if (activeSection === 'timesheet' && (selectedUserId || data.users[0]?.id)) {
          const targetId = selectedUserId || data.users[0].id
          await fetchTimesheets(targetId, selectedMonth)
        }
      }
    } catch (err) {
      console.error('Kullanıcılar yüklenirken hata:', err)
      setError('Kullanıcılar yüklenirken bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (userToEdit = null) => {
    if (userToEdit) {
      setEditingUser(userToEdit)
      setFormData({
        email: userToEdit.email,
        password: '',
        first_name: userToEdit.first_name,
        last_name: userToEdit.last_name,
        user_type: userToEdit.user_type,
        phone_number: userToEdit.phone_number || ''
      })
    } else {
      setEditingUser(null)
      setFormData({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        user_type: 'user',
        phone_number: ''
      })
    }
    setShowModal(true)
    setError('')
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingUser(null)
    setFormData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      user_type: 'user',
      phone_number: ''
    })
    setError('')
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    try {
      if (editingUser) {
        // Güncelleme
        const updateData = { ...formData }
        if (!updateData.password) {
          delete updateData.password
        }
        
        const response = await fetch(`${API_URL}/users/${editingUser.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateData)
        })

        const data = await response.json()
        
        if (data.success) {
          await fetchUsers()
          handleCloseModal()
        } else {
          setError(data.message || 'Kullanıcı güncellenirken bir hata oluştu')
        }
      } else {
        // Yeni kullanıcı
        if (!formData.password) {
          setError('Şifre gereklidir')
          return
        }

        const response = await fetch(`${API_URL}/users`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        })

        const data = await response.json()
        
        if (data.success) {
          await fetchUsers()
          handleCloseModal()
        } else {
          setError(data.message || 'Kullanıcı oluşturulurken bir hata oluştu')
        }
      }
    } catch (err) {
      console.error('Form gönderim hatası:', err)
      setError('Bir hata oluştu. Lütfen tekrar deneyin.')
    }
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) {
      return
    }

    try {
      const response = await fetch(`${API_URL}/users/${userId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      
      if (data.success) {
        await fetchUsers()
      } else {
        alert(data.message || 'Kullanıcı silinirken bir hata oluştu')
      }
    } catch (err) {
      console.error('Silme hatası:', err)
      alert('Bir hata oluştu. Lütfen tekrar deneyin.')
    }
  }

  const getRoleLabel = (userType) => {
    return userType === 'admin' ? 'Admin' : 'Kullanıcı'
  }

  const getStatusLabel = (isActive) => {
    return isActive ? 'Aktif' : 'Pasif'
  }

  const getTimesheetStatusClass = (status) => {
    if (status === 'Onaylandı') return 'pill-success'
    if (status === 'Onay Bekliyor') return 'pill-info'
    return 'pill-muted'
  }

  const formatDate = (iso) => {
    try {
      return new Date(iso).toLocaleDateString('tr-TR')
    } catch (_) {
      return iso
    }
  }

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
    const startWeekDay = (start.getDay() + 6) % 7 // Pazartesi başlasın
    const days = []

    for (let i = 0; i < startWeekDay; i++) {
      days.push({ label: '', date: null, currentMonth: false })
    }

    for (let d = 1; d <= end.getDate(); d++) {
      const dayDate = new Date(start.getFullYear(), start.getMonth(), d)
      days.push({
        label: d,
        date: dayDate,
        currentMonth: true,
      })
    }

    while (days.length % 7 !== 0) {
      days.push({ label: '', date: null, currentMonth: false })
    }

    return days
  }

  const fetchTimesheets = async (userId, month = selectedMonth) => {
    if (!userId) return
    try {
      setTimesheetLoading(true)
      const { start, end } = getMonthRange(month)
      const params = new URLSearchParams({
        user_id: userId,
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0],
      })
      const response = await fetch(`${API_URL}/timesheets?${params.toString()}`)
      const data = await response.json()
      if (data.success) {
        setTimesheets(data.timesheets || [])
      }
    } catch (err) {
      console.error('Timesheet yüklenirken hata:', err)
    } finally {
      setTimesheetLoading(false)
    }
  }

  useEffect(() => {
    if (activeSection === 'timesheet' && selectedUserId) {
      fetchTimesheets(selectedUserId, selectedMonth)
    }
  }, [activeSection, selectedUserId, selectedMonth])

  const activeUsers = users.filter(u => u.is_active).length
  const totalUsers = users.length

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">İ</div>
          <div>
            <div className="brand-title">İş Akış Yönetim Sistemi</div>
            <div className="brand-subtitle">İş Akış Yönetim Sistemi</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div
            className={`nav-item ${activeSection === 'schema' ? 'active' : ''}`}
            onClick={() => setActiveSection('schema')}
          >
            <span className="nav-icon">🗂️</span>
            <span>Şema</span>
          </div>
          <div
            className={`nav-item ${activeSection === 'timesheet' ? 'active' : ''}`}
            onClick={() => setActiveSection('timesheet')}
          >
            <span className="nav-icon">⏱️</span>
            <span>Timesheet</span>
          </div>
          <div
            className={`nav-item ${activeSection === 'users' ? 'active' : ''}`}
            onClick={() => setActiveSection('users')}
          >
            <span className="nav-icon">👥</span>
            <span>Kullanıcı Yönetimi</span>
          </div>
          <div
            className={`nav-item ${activeSection === 'auth' ? 'active' : ''}`}
            onClick={() => setActiveSection('auth')}
          >
            <span className="nav-icon">🔐</span>
            <span>Yetkilendirme</span>
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
            <div className="user-role">admin</div>
          </div>
        </div>
      </aside>

      <main className="admin-main">
        <header className="main-header">
          <div>
            <p className="page-kicker">
              {activeSection === 'timesheet'
                ? 'Tüm kullanıcıların günlük girişlerini görüntüleyin'
                : 'Tüm kullanıcıları görüntüleyin ve yönetin'}
            </p>
            <h1 className="page-title">
              {activeSection === 'timesheet' ? 'Timesheet' : 'Kullanıcı Yönetimi'}
            </h1>
          </div>
          <div className="header-actions">
            <button className="ghost-button" onClick={onLogout}>
              Çıkış
            </button>
          </div>
        </header>

        {activeSection === 'users' && (
          <>
            <section className="stats-row">
              <div className="stat-card">
                <p className="stat-label">Toplam Kullanıcı</p>
                <div className="stat-value">{totalUsers}</div>
              </div>
              <div className="stat-card success">
                <p className="stat-label">Aktif Kullanıcı</p>
                <div className="stat-value">{activeUsers}</div>
              </div>
            </section>

            <section className="table-card">
              <div className="table-toolbar">
                <div className="search-box">
                  <span className="nav-icon">🔍</span>
                  <input 
                    type="text" 
                    placeholder="Kullanıcı ara..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <button className="primary-button" onClick={() => handleOpenModal()}>
                  + Yeni Kullanıcı
                </button>
              </div>

              {loading ? (
                <div className="loading-state">Yükleniyor...</div>
              ) : (
                <>
                  <div className="table-scroll">
                    <table className="user-table">
                      <thead>
                        <tr>
                          <th>Kullanıcı</th>
                          <th>Email</th>
                          <th>Rol</th>
                          <th>Durum</th>
                          <th>İşlemler</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredUsers.length === 0 ? (
                          <tr>
                            <td colSpan="5" style={{ textAlign: 'center', padding: '40px' }}>
                              Kullanıcı bulunamadı
                            </td>
                          </tr>
                        ) : (
                          filteredUsers.map((u) => (
                            <tr key={u.id}>
                              <td>
                                <div className="user-cell">
                                  <div className="user-avatar small">
                                    {u.first_name?.[0] || ''}{u.last_name?.[0] || ''}
                                  </div>
                                  <span>{u.first_name} {u.last_name}</span>
                                </div>
                              </td>
                              <td>{u.email}</td>
                              <td>
                                <span className={`pill ${u.user_type === 'admin' ? 'pill-admin' : 'pill-user'}`}>
                                  {getRoleLabel(u.user_type)}
                                </span>
                              </td>
                              <td>
                                <span className={`pill pill-status ${u.is_active ? 'pill-success' : 'pill-muted'}`}>
                                  {getStatusLabel(u.is_active)}
                                </span>
                              </td>
                              <td className="actions-cell">
                                <button 
                                  className="icon-button" 
                                  onClick={() => handleOpenModal(u)}
                                  title="Düzenle"
                                >
                                  ✏️
                                </button>
                                <button 
                                  className="icon-button danger" 
                                  onClick={() => handleDelete(u.id)}
                                  title="Sil"
                                >
                                  🗑️
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="table-footer">
                    <span>Toplam {filteredUsers.length} kullanıcı • Sayfa 1/1</span>
                    <div className="pager">
                      <button className="ghost-button" disabled>Önceki</button>
                      <button className="ghost-button" disabled>Sonraki</button>
                    </div>
                  </div>
                </>
              )}
            </section>
          </>
        )}

        {activeSection === 'timesheet' && (
          <section className="table-card">
            <div className="table-toolbar timesheet-toolbar">
              <div className="toolbar-left">
                <p className="page-kicker">Günlük girdiler</p>
                <h2 className="page-title" style={{ fontSize: '20px', margin: 0 }}>Timesheet</h2>
              </div>
              <div className="toolbar-right">
                <select
                  className="select-input"
                  value={selectedUserId || ''}
                  onChange={(e) => setSelectedUserId(Number(e.target.value))}
                >
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.first_name} {u.last_name}
                    </option>
                  ))}
                </select>
                <div className="month-switcher">
                  <button
                    className="ghost-button"
                    onClick={() => setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1, 1))}
                  >
                    ←
                  </button>
                  <div className="month-label">
                    {selectedMonth.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' })}
                  </div>
                  <button
                    className="ghost-button"
                    onClick={() => setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1, 1))}
                  >
                    →
                  </button>
                </div>
              </div>
            </div>

            {timesheetLoading ? (
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
                    return (
                      <div
                        key={key}
                        className={`calendar-cell ${day.currentMonth ? '' : 'calendar-cell--muted'}`}
                      >
                        <div className="calendar-date">{day.label}</div>
                        <div className="calendar-entries">
                          {entries.slice(0, 2).map((t) => (
                            <div key={t.id} className="calendar-entry">
                              <div className="entry-title">{t.project}</div>
                              <div className="entry-meta">
                                <span>{t.hours} saat</span>
                                <span className={`pill pill-status ${getTimesheetStatusClass(t.status)}`}>
                                  {t.status}
                                </span>
                              </div>
                              <div className="entry-desc">{t.description || t.activity_type}</div>
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
        )}
      </main>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingUser ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı'}</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="modal-form">
              {error && (
                <div className="error-message">{error}</div>
              )}
              
              <div className="form-group">
                <label>Ad *</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Soyad *</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>E-posta *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Şifre {editingUser ? '(Boş bırakırsanız değişmez)' : '*'}</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required={!editingUser}
                />
              </div>

              <div className="form-group">
                <label>Telefon</label>
                <input
                  type="text"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Rol *</label>
                <select
                  name="user_type"
                  value={formData.user_type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="user">Kullanıcı</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="ghost-button" onClick={handleCloseModal}>
                  İptal
                </button>
                <button type="submit" className="primary-button">
                  {editingUser ? 'Güncelle' : 'Oluştur'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminDashboard
