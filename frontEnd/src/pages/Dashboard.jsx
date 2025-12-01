import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Workflow, CheckCircle, Clock, AlertCircle, Plus } from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'
import './Dashboard.css'

const Dashboard = () => {
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    pending: 0,
    completed: 0,
  })
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(API_ENDPOINTS.workflows)

        if (!response.ok) {
          throw new Error('İş akışları yüklenemedi')
        }

        const data = await response.json()

        // Backend'den gelen veriyi Dashboard için formatla
        const formattedWorkflows = data.map((workflow) => ({
          id: workflow.id.toString(),
          name: workflow.ad,
          description: workflow.aciklama || '',
          status: workflow.status || 'draft',
          createdAt: workflow.olusturma_tarihi,
          updatedAt: workflow.guncelleme_tarihi,
        }))

        setWorkflows(formattedWorkflows)

        const total = formattedWorkflows.length
        const active = formattedWorkflows.filter((w) => w.status === 'active').length
        const pending = formattedWorkflows.filter((w) => w.status === 'pending').length
        const completed = formattedWorkflows.filter((w) => w.status === 'completed').length

        setStats({
          total,
          active,
          pending,
          completed,
        })
      } catch (err) {
        console.error('Dashboard istatistikleri yüklenemedi:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <Link to="/workflows/new" className="btn btn-primary">
          <Plus size={18} />
          Yeni İş Akışı Oluştur
        </Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <Workflow size={24} color="#3b82f6" />
          </div>
          <div className="stat-content">
            <h3>Toplam İş Akışı</h3>
            <p className="stat-value">{stats.total}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7' }}>
            <Clock size={24} color="#f59e0b" />
          </div>
          <div className="stat-content">
            <h3>Bekleyen</h3>
            <p className="stat-value">{stats.pending}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#d1fae5' }}>
            <CheckCircle size={24} color="#10b981" />
          </div>
          <div className="stat-content">
            <h3>Tamamlanan</h3>
            <p className="stat-value">{stats.completed}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fee2e2' }}>
            <AlertCircle size={24} color="#ef4444" />
          </div>
          <div className="stat-content">
            <h3>Aktif</h3>
            <p className="stat-value">{stats.active}</p>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Son İş Akışları</h2>
        {loading ? (
          <div className="workflow-list">
            <p className="empty-state">Yükleniyor...</p>
          </div>
        ) : error ? (
          <div className="workflow-list">
            <p className="empty-state">
              Dashboard verileri yüklenemedi: {error}
            </p>
          </div>
        ) : workflows.length === 0 ? (
          <div className="workflow-list">
            <p className="empty-state">
              Henüz iş akışı bulunmamaktadır. Yeni bir iş akışı oluşturmak için{' '}
              <Link to="/workflows/new">buraya tıklayın</Link>.
            </p>
          </div>
        ) : (
          <div className="workflow-list">
            {workflows.slice(0, 5).map((workflow) => (
              <Link
                key={workflow.id}
                to={`/workflows/${workflow.id}`}
                className="dashboard-workflow-item"
              >
                <div className="dashboard-workflow-main">
                  <h3>{workflow.name}</h3>
                  <p>{workflow.description || 'Açıklama yok'}</p>
                </div>
                <div className="dashboard-workflow-meta">
                  <span>
                    Oluşturulma:{' '}
                    {new Date(workflow.createdAt).toLocaleDateString('tr-TR')}
                  </span>
                  <span>
                    Güncelleme:{' '}
                    {new Date(workflow.updatedAt).toLocaleDateString('tr-TR')}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

