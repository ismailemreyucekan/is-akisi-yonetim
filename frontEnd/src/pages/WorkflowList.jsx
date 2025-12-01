import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Edit, Trash2, Play } from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'
import './WorkflowList.css'

const WorkflowList = () => {
  const [workflows, setWorkflows] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        setLoading(true)
        const response = await fetch(API_ENDPOINTS.workflows)
        
        if (!response.ok) {
          throw new Error('İş akışları yüklenemedi')
        }
        
        const data = await response.json()
        
        // Backend'den gelen verileri formatla
        const formattedWorkflows = data.map((workflow) => ({
          id: workflow.id.toString(),
          name: workflow.ad,
          description: workflow.aciklama || '',
          status: workflow.status || 'draft', // Backend'deki status alanı
          createdAt: workflow.olusturma_tarihi,
          updatedAt: workflow.guncelleme_tarihi,
        }))
        
        setWorkflows(formattedWorkflows)
      } catch (error) {
        console.error('İş akışları yükleme hatası:', error)
        // Daha detaylı hata mesajı
        if (error.message.includes('Failed to fetch') || error.message.includes('Unexpected token')) {
          alert('Backend\'e bağlanılamıyor. Lütfen backend\'in çalıştığından emin olun (port 3002)')
        } else {
          alert(`İş akışları yüklenirken bir hata oluştu: ${error.message}`)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchWorkflows()
  }, [])

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'status-active'
      case 'pending':
        return 'status-pending'
      case 'completed':
        return 'status-completed'
      default:
        return 'status-draft'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'active':
        return 'Aktif'
      case 'pending':
        return 'Beklemede'
      case 'completed':
        return 'Tamamlandı'
      default:
        return 'Taslak'
    }
  }

  const handleDelete = async (workflowId, workflowName) => {
    if (!window.confirm(`"${workflowName}" iş akışını silmek istediğinize emin misiniz?`)) {
      return
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.workflows}/${workflowId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('İş akışı silinemedi')
      }

      // Listeden kaldır
      setWorkflows(workflows.filter((w) => w.id !== workflowId))
      alert('İş akışı başarıyla silindi')
    } catch (error) {
      console.error('Silme hatası:', error)
      alert('İş akışı silinirken bir hata oluştu')
    }
  }

  if (loading) {
    return (
      <div className="workflow-list-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    )
  }

  return (
    <div className="workflow-list-page">
      <div className="page-header">
        <div>
          <h1>İş Akışları</h1>
          <p>Oluşturduğunuz tüm iş akışlarını buradan yönetebilirsiniz</p>
        </div>
        <Link to="/workflows/new" className="btn btn-primary">
          <Plus size={18} />
          Yeni İş Akışı
        </Link>
      </div>

      <div className="search-bar">
        <Search size={20} />
        <input
          type="text"
          placeholder="İş akışı ara..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {filteredWorkflows.length === 0 ? (
        <div className="empty-state">
          <p>
            {searchTerm
              ? 'Arama sonucu bulunamadı'
              : 'Henüz iş akışı bulunmamaktadır'}
          </p>
          {!searchTerm && (
            <Link to="/workflows/new" className="btn btn-primary">
              <Plus size={18} />
              İlk İş Akışını Oluştur
            </Link>
          )}
        </div>
      ) : (
        <div className="workflows-grid">
          {filteredWorkflows.map((workflow) => (
            <div key={workflow.id} className="workflow-card">
              <div className="workflow-card-header">
                <h3>{workflow.name}</h3>
                <span className={`status-badge ${getStatusColor(workflow.status)}`}>
                  {getStatusText(workflow.status)}
                </span>
              </div>
              <p className="workflow-description">{workflow.description}</p>
              <div className="workflow-meta">
                <span>Oluşturulma: {new Date(workflow.createdAt).toLocaleDateString('tr-TR')}</span>
                <span>Güncelleme: {new Date(workflow.updatedAt).toLocaleDateString('tr-TR')}</span>
              </div>
              <div className="workflow-actions">
                <Link
                  to={`/workflows/${workflow.id}`}
                  className="btn-icon"
                  title="Düzenle"
                >
                  <Edit size={18} />
                </Link>
                <button className="btn-icon" title="Çalıştır">
                  <Play size={18} />
                </button>
                <button 
                  className="btn-icon btn-danger" 
                  title="Sil"
                  onClick={() => handleDelete(workflow.id, workflow.name)}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default WorkflowList

