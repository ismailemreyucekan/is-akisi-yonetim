import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, AlertTriangle, Bug, Flag, User } from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'
import './IssueList.css'

const IssueList = () => {
  const [issues, setIssues] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchIssues = async () => {
      try {
        setLoading(true)
        const response = await fetch(API_ENDPOINTS.issues)

        if (!response.ok) {
          throw new Error('Issue listesi yüklenemedi')
        }

        const data = await response.json()
        setIssues(data)
      } catch (error) {
        console.error('Issue listesi yükleme hatası:', error)
        alert(`Issue listesi yüklenirken bir hata oluştu: ${error.message}`)
      } finally {
        setLoading(false)
      }
    }

    fetchIssues()
  }, [])

  const getTypeLabel = (type) => {
    switch (type) {
      case 'bug':
        return 'Bug'
      case 'story':
        return 'Story'
      case 'epic':
        return 'Epic'
      default:
        return 'Task'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'in_progress':
        return 'In Progress'
      case 'done':
        return 'Done'
      default:
        return 'To Do'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'in_progress':
        return 'status-in-progress'
      case 'done':
        return 'status-done'
      default:
        return 'status-todo'
    }
  }

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 'high':
        return 'Yüksek'
      case 'critical':
        return 'Kritik'
      case 'low':
        return 'Düşük'
      default:
        return 'Orta'
    }
  }

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high'
      case 'critical':
        return 'priority-critical'
      case 'low':
        return 'priority-low'
      default:
        return 'priority-medium'
    }
  }

  const filteredIssues = issues.filter((issue) => {
    const matchesSearch =
      issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (issue.description || '').toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus =
      statusFilter === 'all' ? true : issue.status === statusFilter

    const matchesType =
      typeFilter === 'all' ? true : issue.type === typeFilter

    return matchesSearch && matchesStatus && matchesType
  })

  if (loading) {
    return (
      <div className="issue-list-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    )
  }

  return (
    <div className="issue-list-page">
      <div className="page-header">
        <div>
          <h1>Issue Yönetimi</h1>
          <p>Task, Bug, Story ve Epic iş kalemlerini buradan yönetebilirsiniz</p>
        </div>
        <div className="page-header-actions">
          <Link to="/issues/board" className="btn btn-secondary">
            Kanban / Scrum Board
          </Link>
          <Link to="/issues/new" className="btn btn-primary">
            <Plus size={18} />
            Yeni Issue
          </Link>
        </div>
      </div>

      <div className="issue-filters">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Issue ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tüm Durumlar</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="all">Tüm Tipler</option>
            <option value="task">Task</option>
            <option value="bug">Bug</option>
            <option value="story">Story</option>
            <option value="epic">Epic</option>
          </select>
        </div>
      </div>

      {filteredIssues.length === 0 ? (
        <div className="empty-state">
          <p>
            {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
              ? 'Filtrelere göre issue bulunamadı'
              : 'Henüz issue oluşturulmamış'}
          </p>
          {!searchTerm && statusFilter === 'all' && typeFilter === 'all' && (
            <Link to="/issues/new" className="btn btn-primary">
              <Plus size={18} />
              İlk Issue'yu Oluştur
            </Link>
          )}
        </div>
      ) : (
        <div className="issues-grid">
          {filteredIssues.map((issue) => (
            <Link
              key={issue.id}
              to={`/issues/${issue.id}`}
              className="issue-card"
            >
              <div className="issue-card-header">
                <div className="issue-title-row">
                  {issue.type === 'bug' ? (
                    <Bug size={18} className="issue-type-icon bug" />
                  ) : issue.type === 'epic' ? (
                    <Flag size={18} className="issue-type-icon epic" />
                  ) : (
                    <AlertTriangle size={18} className="issue-type-icon task" />
                  )}
                  <h3>{issue.title}</h3>
                </div>
                <span className={`status-badge ${getStatusClass(issue.status)}`}>
                  {getStatusLabel(issue.status)}
                </span>
              </div>
              <p className="issue-description">
                {issue.description || 'Açıklama yok'}
              </p>
              <div className="issue-meta">
                <span className={`priority-badge ${getPriorityClass(issue.priority)}`}>
                  {getPriorityLabel(issue.priority)}
                </span>
                <span className="assignee">
                  <User size={14} />
                  {issue.assignee || 'Atanmadı'}
                </span>
                <span>
                  Oluşturulma:{' '}
                  {new Date(issue.createdAt).toLocaleDateString('tr-TR')}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default IssueList


