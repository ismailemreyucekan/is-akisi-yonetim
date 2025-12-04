import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { API_ENDPOINTS } from '../config/api'
import { Plus, RefreshCw } from 'lucide-react'
import './IssueBoard.css'

const STATUSES = [
  { id: 'todo', title: 'To Do' },
  { id: 'in_progress', title: 'In Progress' },
  { id: 'done', title: 'Done' },
]

const IssueBoard = () => {
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [draggingId, setDraggingId] = useState(null)
  const [updatingId, setUpdatingId] = useState(null)

  const loadIssues = async () => {
    try {
      setLoading(true)
      const response = await fetch(API_ENDPOINTS.issues)
      if (!response.ok) throw new Error('Issue listesi yüklenemedi')
      const data = await response.json()
      setIssues(data)
    } catch (error) {
      console.error('Issue board yükleme hatası:', error)
      alert(`Issue board yüklenirken bir hata oluştu: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadIssues()
  }, [])

  const handleDragStart = (issueId) => {
    setDraggingId(issueId)
  }

  const handleDragEnd = () => {
    setDraggingId(null)
  }

  const handleDrop = async (statusId) => {
    if (!draggingId) return

    const issue = issues.find((i) => i.id === draggingId)
    if (!issue || issue.status === statusId) {
      setDraggingId(null)
      return
    }

    // Optimistic update
    const previousIssues = issues
    const updatedIssues = issues.map((i) =>
      i.id === draggingId ? { ...i, status: statusId } : i
    )
    setIssues(updatedIssues)
    setUpdatingId(draggingId)

    try {
      const response = await fetch(`${API_ENDPOINTS.issues}/${draggingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: statusId }),
      })
      if (!response.ok) {
        throw new Error('Durum güncellenemedi')
      }
    } catch (error) {
      console.error('Durum güncelleme hatası:', error)
      alert('Kart taşınırken bir hata oluştu, geri alınıyor.')
      setIssues(previousIssues)
    } finally {
      setDraggingId(null)
      setUpdatingId(null)
    }
  }

  const getIssuesByStatus = (statusId) =>
    issues.filter((issue) => issue.status === statusId)

  return (
    <div className="issue-board-page">
      <div className="page-header">
        <div>
          <h1>Kanban / Scrum Board</h1>
          <p>Issue'larınızı sütun bazlı kart sistemiyle yönetin</p>
        </div>
        <div className="board-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={loadIssues}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            Yenile
          </button>
          <Link to="/issues/new" className="btn btn-primary">
            <Plus size={18} />
            Yeni Issue
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="board-loading">Yükleniyor...</div>
      ) : (
        <div className="board-columns">
          {STATUSES.map((column) => (
            <div
              key={column.id}
              className="board-column"
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(column.id)}
            >
              <div className="board-column-header">
                <h2>{column.title}</h2>
                <span className="column-count">
                  {getIssuesByStatus(column.id).length}
                </span>
              </div>
              <div className="board-column-body">
                {getIssuesByStatus(column.id).length === 0 ? (
                  <p className="column-empty">Bu sütunda kart yok</p>
                ) : (
                  getIssuesByStatus(column.id).map((issue) => (
                    <Link
                      key={issue.id}
                      to={`/issues/${issue.id}`}
                      className={`board-card ${
                        draggingId === issue.id ? 'dragging' : ''
                      } ${updatingId === issue.id ? 'updating' : ''}`}
                      draggable
                      onDragStart={() => handleDragStart(issue.id)}
                      onDragEnd={handleDragEnd}
                    >
                      <h3>{issue.title}</h3>
                      {issue.description && (
                        <p>{issue.description.slice(0, 80)}...</p>
                      )}
                      <div className="board-card-meta">
                        <span className={`priority ${issue.priority || 'medium'}`}>
                          {issue.priority || 'medium'}
                        </span>
                        {issue.assignee && (
                          <span className="assignee">{issue.assignee}</span>
                        )}
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default IssueBoard


