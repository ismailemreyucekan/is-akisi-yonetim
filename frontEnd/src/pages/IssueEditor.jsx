import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Save,
  ArrowLeft,
  Bug,
  Flag,
  AlertTriangle,
  User,
  MessageSquare,
  ListChecks,
  Paperclip,
  Plus,
  Trash2,
} from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'
import './IssueEditor.css'

const IssueEditor = () => {
  const { id } = useParams()
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [type, setType] = useState('task')
  const [status, setStatus] = useState('todo')
  const [priority, setPriority] = useState('medium')
  const [description, setDescription] = useState('')
  const [assignee, setAssignee] = useState('')
  const [tags, setTags] = useState('')

  const [comments, setComments] = useState([])
  const [subtasks, setSubtasks] = useState([])
  const [attachments, setAttachments] = useState([])

  const [newComment, setNewComment] = useState('')
  const [newSubtask, setNewSubtask] = useState('')
  const [newAttachmentName, setNewAttachmentName] = useState('')
  const [newAttachmentUrl, setNewAttachmentUrl] = useState('')

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchIssue = async () => {
      if (id && id !== 'new') {
        try {
          setLoading(true)
          const response = await fetch(`${API_ENDPOINTS.issues}/${id}`)

          if (!response.ok) {
            throw new Error('Issue yüklenemedi')
          }

          const data = await response.json()
          setTitle(data.title || '')
          setType(data.type || 'task')
          setStatus(data.status || 'todo')
          setPriority(data.priority || 'medium')
          setDescription(data.description || '')
          setAssignee(data.assignee || '')
          setTags((data.tags || []).join(', '))
          setComments(data.comments || [])
          setSubtasks(data.subtasks || [])
          setAttachments(data.attachments || [])
        } catch (error) {
          console.error('Issue yükleme hatası:', error)
          alert('Issue yüklenirken bir hata oluştu')
        } finally {
          setLoading(false)
        }
      } else {
        setTitle('')
        setType('task')
        setStatus('todo')
        setPriority('medium')
        setDescription('')
        setAssignee('')
        setTags('')
        setComments([])
        setSubtasks([])
        setAttachments([])
      }
    }

    fetchIssue()
  }, [id])

  const handleSave = async () => {
    if (!title.trim()) {
      alert('Lütfen issue başlığını girin')
      return
    }

    setLoading(true)

    try {
      const payload = {
        title: title.trim(),
        type,
        status,
        priority,
        description: description.trim() || null,
        assignee: assignee.trim() || null,
        tags: tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
      }

      const isUpdate = id && id !== 'new'

      const response = await fetch(
        isUpdate ? `${API_ENDPOINTS.issues}/${id}` : API_ENDPOINTS.issues,
        {
          method: isUpdate ? 'PUT' : 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      )

      if (!response.ok) {
        const text = await response.text()
        throw new Error(`Kayıt başarısız: ${response.status} - ${text}`)
      }

      await response.json()
      alert('Issue başarıyla kaydedildi!')
      navigate('/issues')
    } catch (error) {
      console.error('Kayıt hatası:', error)
      alert(`Kayıt işlemi başarısız: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const refreshIssue = async () => {
    if (!id || id === 'new') return
    try {
      const response = await fetch(`${API_ENDPOINTS.issues}/${id}`)
      if (!response.ok) return
      const data = await response.json()
      setComments(data.comments || [])
      setSubtasks(data.subtasks || [])
      setAttachments(data.attachments || [])
    } catch {
      // Sessizce yut
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim() || !id || id === 'new') return
    try {
      const response = await fetch(`${API_ENDPOINTS.issues}/${id}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newComment }),
      })
      if (!response.ok) throw new Error('Yorum eklenemedi')
      const created = await response.json()
      setComments([...comments, created])
      setNewComment('')
    } catch (error) {
      console.error('Yorum ekleme hatası:', error)
      alert('Yorum eklenirken bir hata oluştu')
    }
  }

  const handleDeleteComment = async (commentId) => {
    if (!id || id === 'new') return
    try {
      const response = await fetch(
        `${API_ENDPOINTS.issues}/${id}/comments/${commentId}`,
        { method: 'DELETE' }
      )
      if (!response.ok) throw new Error('Yorum silinemedi')
      setComments(comments.filter((c) => c.id !== commentId))
    } catch (error) {
      console.error('Yorum silme hatası:', error)
      alert('Yorum silinirken bir hata oluştu')
    }
  }

  const handleAddSubtask = async () => {
    if (!newSubtask.trim() || !id || id === 'new') return
    try {
      const response = await fetch(`${API_ENDPOINTS.issues}/${id}/subtasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newSubtask }),
      })
      if (!response.ok) throw new Error('Alt görev eklenemedi')
      const created = await response.json()
      setSubtasks([...subtasks, created])
      setNewSubtask('')
    } catch (error) {
      console.error('Alt görev ekleme hatası:', error)
      alert('Alt görev eklenirken bir hata oluştu')
    }
  }

  const toggleSubtaskDone = async (subtask) => {
    if (!id || id === 'new') return
    try {
      const response = await fetch(
        `${API_ENDPOINTS.issues}/${id}/subtasks/${subtask.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ done: !subtask.done }),
        }
      )
      if (!response.ok) throw new Error('Alt görev güncellenemedi')
      const updated = await response.json()
      setSubtasks(
        subtasks.map((s) => (s.id === updated.id ? updated : s))
      )
    } catch (error) {
      console.error('Alt görev güncelleme hatası:', error)
      alert('Alt görev güncellenirken bir hata oluştu')
    }
  }

  const handleDeleteSubtask = async (subtaskId) => {
    if (!id || id === 'new') return
    try {
      const response = await fetch(
        `${API_ENDPOINTS.issues}/${id}/subtasks/${subtaskId}`,
        { method: 'DELETE' }
      )
      if (!response.ok) throw new Error('Alt görev silinemedi')
      setSubtasks(subtasks.filter((s) => s.id !== subtaskId))
    } catch (error) {
      console.error('Alt görev silme hatası:', error)
      alert('Alt görev silinirken bir hata oluştu')
    }
  }

  const handleAddAttachment = async () => {
    if (!newAttachmentUrl.trim() || !id || id === 'new') return
    try {
      const response = await fetch(
        `${API_ENDPOINTS.issues}/${id}/attachments`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            fileName: newAttachmentName || newAttachmentUrl,
            url: newAttachmentUrl,
          }),
        }
      )
      if (!response.ok) throw new Error('Dosya eklenemedi')
      const created = await response.json()
      setAttachments([...attachments, created])
      setNewAttachmentName('')
      setNewAttachmentUrl('')
    } catch (error) {
      console.error('Dosya ekleme hatası:', error)
      alert('Dosya eklenirken bir hata oluştu')
    }
  }

  const handleDeleteAttachment = async (attachmentId) => {
    if (!id || id === 'new') return
    try {
      const response = await fetch(
        `${API_ENDPOINTS.issues}/${id}/attachments/${attachmentId}`,
        { method: 'DELETE' }
      )
      if (!response.ok) throw new Error('Dosya silinemedi')
      setAttachments(attachments.filter((a) => a.id !== attachmentId))
    } catch (error) {
      console.error('Dosya silme hatası:', error)
      alert('Dosya silinirken bir hata oluştu')
    }
  }

  return (
    <div className="issue-editor">
      <div className="editor-header">
        <button onClick={() => navigate('/issues')} className="btn-icon">
          <ArrowLeft size={20} />
        </button>
        <div className="editor-title">
          <h1>{id === 'new' ? 'Yeni Issue' : 'Issue Düzenle'}</h1>
        </div>
        <button
          onClick={handleSave}
          className="btn btn-primary"
          disabled={loading}
        >
          <Save size={18} />
          {loading ? 'Kaydediliyor...' : 'Kaydet'}
        </button>
      </div>

      <div className="issue-editor-content">
        <div className="issue-main">
          <div className="form-group">
            <label>Başlık *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Issue başlığını girin"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Tip</label>
              <div className="type-selector">
                <button
                  type="button"
                  className={`type-option ${
                    type === 'task' ? 'active' : ''
                  }`}
                  onClick={() => setType('task')}
                >
                  <AlertTriangle size={16} />
                  <span>Task</span>
                </button>
                <button
                  type="button"
                  className={`type-option ${type === 'bug' ? 'active' : ''}`}
                  onClick={() => setType('bug')}
                >
                  <Bug size={16} />
                  <span>Bug</span>
                </button>
                <button
                  type="button"
                  className={`type-option ${
                    type === 'story' ? 'active' : ''
                  }`}
                  onClick={() => setType('story')}
                >
                  <ListChecks size={16} />
                  <span>Story</span>
                </button>
                <button
                  type="button"
                  className={`type-option ${type === 'epic' ? 'active' : ''}`}
                  onClick={() => setType('epic')}
                >
                  <Flag size={16} />
                  <span>Epic</span>
                </button>
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Durum</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            </div>
            <div className="form-group">
              <label>Öncelik</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="low">Düşük</option>
                <option value="medium">Orta</option>
                <option value="high">Yüksek</option>
                <option value="critical">Kritik</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Atanan Kişi</label>
              <div className="assignee-input">
                <User size={16} />
                <input
                  type="text"
                  value={assignee}
                  onChange={(e) => setAssignee(e.target.value)}
                  placeholder="Örn: Ahmet Yılmaz"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Etiketler</label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="Örn: frontend, urgent (virgülle ayırın)"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Açıklama</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Issue detay açıklamasını girin"
              rows={6}
            />
          </div>
        </div>

        <div className="issue-side">
          <section className="panel">
            <div className="panel-header">
              <MessageSquare size={16} />
              <h2>Yorumlar</h2>
            </div>
            {!id || id === 'new' ? (
              <p className="panel-empty">
                Yorum eklemek için önce issue'yu kaydedin.
              </p>
            ) : (
              <>
                <div className="comment-list">
                  {comments.length === 0 ? (
                    <p className="panel-empty">Henüz yorum yok.</p>
                  ) : (
                    comments.map((comment) => (
                      <div key={comment.id} className="comment-item">
                        <div className="comment-header">
                          <span className="comment-author">
                            {comment.author || 'Anonim'}
                          </span>
                          <button
                            className="btn-icon"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                        <p className="comment-text">{comment.text}</p>
                        <span className="comment-date">
                          {new Date(comment.createdAt).toLocaleString('tr-TR')}
                        </span>
                      </div>
                    ))
                  )}
                </div>
                <div className="comment-input">
                  <textarea
                    rows={2}
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Yorum ekle..."
                  />
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={handleAddComment}
                  >
                    <Plus size={16} />
                    Ekle
                  </button>
                </div>
              </>
            )}
          </section>

          <section className="panel">
            <div className="panel-header">
              <ListChecks size={16} />
              <h2>Alt Görevler</h2>
            </div>
            {!id || id === 'new' ? (
              <p className="panel-empty">
                Alt görev eklemek için önce issue'yu kaydedin.
              </p>
            ) : (
              <>
                <div className="subtask-list">
                  {subtasks.length === 0 ? (
                    <p className="panel-empty">Henüz alt görev yok.</p>
                  ) : (
                    subtasks.map((subtask) => (
                      <div key={subtask.id} className="subtask-item">
                        <label>
                          <input
                            type="checkbox"
                            checked={subtask.done}
                            onChange={() => toggleSubtaskDone(subtask)}
                          />
                          <span
                            className={
                              subtask.done ? 'subtask-done' : undefined
                            }
                          >
                            {subtask.title}
                          </span>
                        </label>
                        <button
                          className="btn-icon"
                          onClick={() => handleDeleteSubtask(subtask.id)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
                <div className="subtask-input">
                  <input
                    type="text"
                    value={newSubtask}
                    onChange={(e) => setNewSubtask(e.target.value)}
                    placeholder="Alt görev başlığı..."
                  />
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={handleAddSubtask}
                  >
                    <Plus size={16} />
                    Ekle
                  </button>
                </div>
              </>
            )}
          </section>

          <section className="panel">
            <div className="panel-header">
              <Paperclip size={16} />
              <h2>Ekler</h2>
            </div>
            {!id || id === 'new' ? (
              <p className="panel-empty">
                Dosya eklemek için önce issue'yu kaydedin.
              </p>
            ) : (
              <>
                <div className="attachment-list">
                  {attachments.length === 0 ? (
                    <p className="panel-empty">Henüz dosya eklenmemiş.</p>
                  ) : (
                    attachments.map((attachment) => (
                      <div key={attachment.id} className="attachment-item">
                        <a
                          href={attachment.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {attachment.fileName || attachment.url}
                        </a>
                        <button
                          className="btn-icon"
                          onClick={() =>
                            handleDeleteAttachment(attachment.id)
                          }
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
                <div className="attachment-input">
                  <input
                    type="text"
                    value={newAttachmentName}
                    onChange={(e) => setNewAttachmentName(e.target.value)}
                    placeholder="Dosya adı (isteğe bağlı)"
                  />
                  <input
                    type="text"
                    value={newAttachmentUrl}
                    onChange={(e) => setNewAttachmentUrl(e.target.value)}
                    placeholder="Dosya URL'si"
                  />
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={handleAddAttachment}
                  >
                    <Plus size={16} />
                    Ekle
                  </button>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

export default IssueEditor


