import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Save, ArrowLeft, Plus, Trash2, X, CheckCircle } from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'
import './WorkflowEditor.css'

const WorkflowEditor = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [workflowName, setWorkflowName] = useState('')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [workflowStatus, setWorkflowStatus] = useState('draft')
  const [steps, setSteps] = useState([])
  const [connections, setConnections] = useState([]) // [{ id, fromStepId, toStepId }]
  const [loading, setLoading] = useState(false)
  const [draggedStep, setDraggedStep] = useState(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [connectingFrom, setConnectingFrom] = useState(null) // Bağlantı başlatılan adım ID'si
  const [hoveredConnection, setHoveredConnection] = useState(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [showAddStepModal, setShowAddStepModal] = useState(false)
  const [newStepData, setNewStepData] = useState({
    type: 'task',
    name: '',
    description: '',
  })
  const canvasRef = useRef(null)

  useEffect(() => {
    const fetchWorkflow = async () => {
      if (id && id !== 'new') {
        try {
          setLoading(true)
          const response = await fetch(`${API_ENDPOINTS.workflows}/${id}`)
          
          if (!response.ok) {
            const contentType = response.headers.get('content-type')
            if (contentType && contentType.includes('application/json')) {
              const errorData = await response.json()
              throw new Error(errorData.error || `İş akışı yüklenemedi (${response.status})`)
            } else {
              throw new Error(`Backend hatası: ${response.status}. Backend'in çalıştığından emin olun.`)
            }
          }
          
          const data = await response.json()
          
          setWorkflowName(data.ad || '')
          setWorkflowDescription(data.aciklama || '')
          setWorkflowStatus(data.status || 'draft')
          
          // JSONB'den gelen verileri parse et
          const parsedSteps = Array.isArray(data.adimlar) 
            ? data.adimlar 
            : (typeof data.adimlar === 'string' ? JSON.parse(data.adimlar) : [])
          
          const parsedConnections = Array.isArray(data.baglantilar)
            ? data.baglantilar
            : (typeof data.baglantilar === 'string' ? JSON.parse(data.baglantilar) : [])
          
          setSteps(parsedSteps)
          setConnections(parsedConnections)
        } catch (error) {
          console.error('İş akışı yükleme hatası:', error)
          alert('İş akışı yüklenirken bir hata oluştu')
        } finally {
          setLoading(false)
        }
      } else {
        // Yeni iş akışı için boş başla
        setSteps([])
        setConnections([])
        setWorkflowStatus('draft')
      }
    }

    fetchWorkflow()
  }, [id])

  const handleSave = async () => {
    if (!workflowName.trim()) {
      alert('Lütfen iş akışı adını girin')
      return
    }

    setLoading(true)
    
    try {
      const workflowData = {
        ad: workflowName.trim(),
        aciklama: workflowDescription.trim() || null,
        adimlar: steps,
        baglantilar: connections,
        status: workflowStatus,
      }

      let response
      if (id && id !== 'new') {
        // Güncelleme
        response = await fetch(`${API_ENDPOINTS.workflows}/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(workflowData),
        })
      } else {
        // Yeni oluşturma
        response = await fetch(API_ENDPOINTS.workflows, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(workflowData),
        })
      }

      if (!response.ok) {
        // Response'un JSON olup olmadığını kontrol et
        const contentType = response.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Kayıt işlemi başarısız (${response.status})`)
        } else {
          const text = await response.text()
          throw new Error(`Backend hatası: ${response.status} - ${text.substring(0, 100)}`)
        }
      }

      const savedWorkflow = await response.json()
      alert('İş akışı başarıyla kaydedildi!')
      navigate('/workflows')
    } catch (error) {
      console.error('Kayıt hatası:', error)
      alert(`Kayıt işlemi başarısız: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const openAddStepModal = () => {
    setNewStepData({
      type: 'task',
      name: '',
      description: '',
    })
    setShowAddStepModal(true)
  }

  const closeAddStepModal = () => {
    setShowAddStepModal(false)
    setNewStepData({
      type: 'task',
      name: '',
      description: '',
    })
  }

  const handleAddStep = () => {
    if (!newStepData.name.trim()) {
      alert('Lütfen adım başlığını girin')
      return
    }

    // Başlangıç ve bitiş adımlarını bul
    const startStep = steps.find((step) => step.type === 'start')
    const endStep = steps.find((step) => step.type === 'end')
    
    let newPosition
    let updatedEndPosition = null

    // Eğer hiç adım yoksa, merkeze yerleştir
    if (steps.length === 0) {
      newPosition = {
        x: 300,
        y: 200,
      }
    } else if (!startStep || !endStep) {
      // Başlangıç veya bitiş yoksa, son adımdan sonra yerleştir
      const lastStep = steps[steps.length - 1]
      newPosition = {
        x: lastStep.position.x + 250,
        y: lastStep.position.y,
      }
    } else {
      // Başlangıç ve bitiş arasındaki adımları bul (sadece task ve approval tipindeki)
      const middleSteps = steps.filter(
        (step) => step.type !== 'start' && step.type !== 'end'
      )

      if (middleSteps.length === 0) {
        // Başlangıç ve bitiş arasında adım yoksa, ortaya yerleştir
        const midX = (startStep.position.x + endStep.position.x) / 2
        newPosition = {
          x: midX,
          y: startStep.position.y,
        }
      } else {
        // Son adımdan sonra yerleştir
        const lastMiddleStep = middleSteps[middleSteps.length - 1]
        const stepSpacing = 200 // Adımlar arası mesafe
        newPosition = {
          x: lastMiddleStep.position.x + stepSpacing,
          y: startStep.position.y,
        }
        
        // Eğer bitiş adımına çok yakınsa, bitiş adımını sağa kaydır
        if (newPosition.x + 200 >= endStep.position.x) {
          const newEndX = newPosition.x + stepSpacing + 200
          updatedEndPosition = {
            ...endStep.position,
            x: newEndX,
          }
        }
      }
    }

    const newStep = {
      id: Date.now().toString(),
      name: newStepData.name.trim(),
      type: newStepData.type,
      description: newStepData.description.trim(),
      position: newPosition,
    }

    // Eğer başlangıç veya bitiş adımı ekleniyorsa, direkt ekle
    if (newStepData.type === 'start' || newStepData.type === 'end') {
      // Aynı tip adım zaten varsa uyar
      const existingStep = steps.find((step) => step.type === newStepData.type)
      if (existingStep) {
        alert(`${newStepData.type === 'start' ? 'Başlangıç' : 'Bitiş'} adımı zaten mevcut!`)
        return
      }
      setSteps([...steps, newStep])
    } else {
      // Görev veya onay adımı ekleniyorsa, başlangıç ve bitiş arasına ekle
      if (startStep && endStep) {
        const endIndex = steps.findIndex((step) => step.id === endStep.id)
        const newSteps = [...steps]
        newSteps.splice(endIndex, 0, newStep)
        
        // Eğer bitiş adımının pozisyonunu güncellememiz gerekiyorsa
        if (updatedEndPosition) {
          const endStepIndex = newSteps.findIndex((step) => step.id === endStep.id)
          newSteps[endStepIndex] = {
            ...endStep,
            position: updatedEndPosition,
          }
        }
        
        setSteps(newSteps)
      } else {
        setSteps([...steps, newStep])
      }
    }

    closeAddStepModal()
  }

  const deleteStep = (stepId) => {
    if (steps.length <= 2) {
      alert('En az bir başlangıç ve bir bitiş adımı olmalıdır')
      return
    }
    setSteps(steps.filter((step) => step.id !== stepId))
    // Adım silindiğinde ilgili bağlantıları da sil
    setConnections(connections.filter(
      (conn) => conn.fromStepId !== stepId && conn.toStepId !== stepId
    ))
  }

  const deleteConnection = (connectionId) => {
    setConnections(connections.filter((conn) => conn.id !== connectionId))
  }

  const handleConnectionPointClick = (stepId, isOutput) => {
    if (connectingFrom) {
      // Bağlantıyı tamamla
      if (connectingFrom !== stepId) {
        const newConnection = {
          id: `conn-${connectingFrom}-${stepId}-${Date.now()}`,
          fromStepId: connectingFrom,
          toStepId: stepId,
        }
        // Aynı bağlantı zaten var mı kontrol et
        const exists = connections.some(
          (conn) => conn.fromStepId === connectingFrom && conn.toStepId === stepId
        )
        if (!exists) {
          setConnections([...connections, newConnection])
        }
      }
      setConnectingFrom(null)
    } else if (isOutput) {
      // Bağlantı başlat (sadece çıkış noktasından)
      setConnectingFrom(stepId)
    }
  }

  const updateStep = useCallback((stepId, updates) => {
    setSteps((prevSteps) =>
      prevSteps.map((step) =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    )
  }, [])

  const getStepColor = (type) => {
    switch (type) {
      case 'start':
        return '#10b981'
      case 'end':
        return '#ef4444'
      case 'approval':
        return '#f59e0b'
      default:
        return '#3b82f6'
    }
  }

  const handleMouseDown = (e, step) => {
    // Input alanına tıklandığında sürükleme başlamasın
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
      return
    }

    e.preventDefault()
    const canvasRect = canvasRef.current.getBoundingClientRect()
    const stepRect = e.currentTarget.getBoundingClientRect()
    
    setDraggedStep(step.id)
    setDragOffset({
      x: e.clientX - stepRect.left,
      y: e.clientY - stepRect.top,
    })
  }

  const handleMouseMove = useCallback((e) => {
    if (!draggedStep || !canvasRef.current) return

    const canvasRect = canvasRef.current.getBoundingClientRect()
    const newX = e.clientX - canvasRect.left - dragOffset.x
    const newY = e.clientY - canvasRect.top - dragOffset.y

    // Canvas sınırları içinde kalmasını sağla
    const stepWidth = 200 // min-width değeri
    const stepHeight = 100 // yaklaşık yükseklik
    const boundedX = Math.max(0, Math.min(newX, canvasRect.width - stepWidth))
    const boundedY = Math.max(0, Math.min(newY, canvasRect.height - stepHeight))

    updateStep(draggedStep, {
      position: { x: boundedX, y: boundedY },
    })
  }, [draggedStep, dragOffset, updateStep])

  const handleMouseUp = useCallback(() => {
    setDraggedStep(null)
    setDragOffset({ x: 0, y: 0 })
  }, [])

  useEffect(() => {
    if (draggedStep) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [draggedStep, handleMouseMove, handleMouseUp])

  // Mouse pozisyonunu takip et (bağlantı oluşturma için)
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (connectingFrom && canvasRef.current) {
        const canvasRect = canvasRef.current.getBoundingClientRect()
        setMousePosition({
          x: e.clientX - canvasRect.left,
          y: e.clientY - canvasRect.top,
        })
      }
    }

    if (connectingFrom) {
      document.addEventListener('mousemove', handleMouseMove)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
      }
    }
  }, [connectingFrom])

  // Bağlantı noktası pozisyonunu hesapla
  const getConnectionPointPosition = useCallback((step, isOutput) => {
    const stepWidth = 200
    const stepHeight = 120
    
    if (isOutput) {
      // Çıkış noktası (sağ orta)
      return {
        x: step.position.x + stepWidth,
        y: step.position.y + stepHeight / 2,
      }
    } else {
      // Giriş noktası (sol orta)
      return {
        x: step.position.x,
        y: step.position.y + stepHeight / 2,
      }
    }
  }, [])

  // İki adım arasındaki bağlantı noktalarını hesapla
  const getConnectionPoints = useCallback((fromStep, toStep) => {
    const fromPoint = getConnectionPointPosition(fromStep, true)
    const toPoint = getConnectionPointPosition(toStep, false)
    return {
      fromX: fromPoint.x,
      fromY: fromPoint.y,
      toX: toPoint.x,
      toY: toPoint.y,
    }
  }, [getConnectionPointPosition])

  return (
    <div className="workflow-editor">
      <div className="editor-header">
        <button onClick={() => navigate('/workflows')} className="btn-icon">
          <ArrowLeft size={20} />
        </button>
        <div className="editor-title">
          <h1>{id === 'new' ? 'Yeni İş Akışı' : 'İş Akışı Düzenle'}</h1>
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

      <div className="editor-content">
        <div className="workflow-info">
          <div className="form-group">
            <label>İş Akışı Adı</label>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              placeholder="İş akışı adını girin"
            />
          </div>
          <div className="form-group">
            <label>Açıklama</label>
            <textarea
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              placeholder="İş akışı açıklamasını girin"
              rows={3}
            />
          </div>
          <div className="form-group">
            <label>Durum</label>
            <select
              value={workflowStatus}
              onChange={(e) => setWorkflowStatus(e.target.value)}
            >
              <option value="draft">Taslak</option>
              <option value="active">Aktif</option>
              <option value="pending">Beklemede</option>
              <option value="completed">Tamamlandı</option>
            </select>
          </div>
        </div>

        <div className="workflow-canvas-container">
          <div className="canvas-header">
            <h2>İş Akışı Tasarımı</h2>
            <button onClick={openAddStepModal} className="btn btn-secondary">
              <Plus size={18} />
              Adım Ekle
            </button>
          </div>
          <div 
            className="workflow-canvas"
            ref={canvasRef}
            onClick={(e) => {
              // Canvas'a tıklandığında bağlantı modunu iptal et
              if (connectingFrom && e.target === e.currentTarget) {
                setConnectingFrom(null)
              }
            }}
          >
            {/* Dinamik ok bağlantıları */}
            <svg className="workflow-connections" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 1 }}>
              {/* Bağlantı çizgileri */}
              {connections.map((connection) => {
                const fromStep = steps.find((s) => s.id === connection.fromStepId)
                const toStep = steps.find((s) => s.id === connection.toStepId)
                
                if (!fromStep || !toStep) return null
                
                const { fromX, fromY, toX, toY } = getConnectionPoints(fromStep, toStep)
                
                // Ok başı için açı hesapla
                const angle = Math.atan2(toY - fromY, toX - fromX)
                const arrowLength = 10
                const arrowAngle = Math.PI / 6
                
                const arrowX1 = toX - arrowLength * Math.cos(angle - arrowAngle)
                const arrowY1 = toY - arrowLength * Math.sin(angle - arrowAngle)
                const arrowX2 = toX - arrowLength * Math.cos(angle + arrowAngle)
                const arrowY2 = toY - arrowLength * Math.sin(angle + arrowAngle)
                
                const isHovered = hoveredConnection === connection.id
                
                return (
                  <g 
                    key={connection.id}
                    style={{ pointerEvents: 'all', cursor: 'pointer' }}
                    onMouseEnter={() => setHoveredConnection(connection.id)}
                    onMouseLeave={() => setHoveredConnection(null)}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (window.confirm('Bu bağlantıyı silmek istediğinize emin misiniz?')) {
                        deleteConnection(connection.id)
                      }
                    }}
                  >
                    <line
                      x1={fromX}
                      y1={fromY}
                      x2={toX}
                      y2={toY}
                      stroke={isHovered ? "#ef4444" : "#9ca3af"}
                      strokeWidth={isHovered ? "3" : "2.5"}
                      markerEnd="url(#arrowhead)"
                      style={{ filter: isHovered ? 'none' : 'drop-shadow(0 1px 1px rgba(0,0,0,0.1))' }}
                    />
                    <polygon
                      points={`${toX},${toY} ${arrowX1},${arrowY1} ${arrowX2},${arrowY2}`}
                      fill={isHovered ? "#ef4444" : "#9ca3af"}
                    />
                    {isHovered && (
                      <circle
                        cx={(fromX + toX) / 2}
                        cy={(fromY + toY) / 2}
                        r="8"
                        fill="#ef4444"
                        stroke="white"
                        strokeWidth="2"
                      />
                    )}
                  </g>
                )
              })}
              
              {/* Bağlantı oluşturma çizgisi */}
              {connectingFrom && (() => {
                const fromStep = steps.find((s) => s.id === connectingFrom)
                if (!fromStep) return null
                
                const fromPoint = getConnectionPointPosition(fromStep, true)
                
                // Ok başı için açı hesapla
                const angle = Math.atan2(mousePosition.y - fromPoint.y, mousePosition.x - fromPoint.x)
                const arrowLength = 10
                const arrowAngle = Math.PI / 6
                
                const arrowX1 = mousePosition.x - arrowLength * Math.cos(angle - arrowAngle)
                const arrowY1 = mousePosition.y - arrowLength * Math.sin(angle - arrowAngle)
                const arrowX2 = mousePosition.x - arrowLength * Math.cos(angle + arrowAngle)
                const arrowY2 = mousePosition.y - arrowLength * Math.sin(angle + arrowAngle)
                
                return (
                  <g style={{ pointerEvents: 'none' }}>
                    <line
                      x1={fromPoint.x}
                      y1={fromPoint.y}
                      x2={mousePosition.x}
                      y2={mousePosition.y}
                      stroke="#3b82f6"
                      strokeWidth="2.5"
                      strokeDasharray="5,5"
                    />
                    {/* Ok başı */}
                    <polygon
                      points={`${mousePosition.x},${mousePosition.y} ${arrowX1},${arrowY1} ${arrowX2},${arrowY2}`}
                      fill="#3b82f6"
                    />
                  </g>
                )
              })()}
              
              {/* Ok başı marker tanımı */}
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="3"
                  orient="auto"
                >
                  <polygon points="0 0, 10 3, 0 6" fill="#9ca3af" />
                </marker>
              </defs>
            </svg>

            {/* Boş canvas mesajı */}
            {steps.length === 0 && (
              <div className="empty-canvas-message">
                <Plus size={48} />
                <h3>İş Akışına Başlayın</h3>
                <p>İlk adımınızı eklemek için yukarıdaki "Adım Ekle" butonuna tıklayın</p>
              </div>
            )}

            {/* Adımlar */}
            {steps.map((step) => {
              const outputPoint = getConnectionPointPosition(step, true)
              const inputPoint = getConnectionPointPosition(step, false)
              const isConnectingFromThis = connectingFrom === step.id
              
              return (
                <div
                  key={step.id}
                  className={`workflow-step ${draggedStep === step.id ? 'dragging' : ''}`}
                  style={{
                    left: step.position.x,
                    top: step.position.y,
                    borderColor: getStepColor(step.type),
                    zIndex: draggedStep === step.id ? 1000 : 10,
                  }}
                  onMouseDown={(e) => handleMouseDown(e, step)}
                >
                  <div className="step-header">
                    <span
                      className="step-type-badge"
                      style={{ background: getStepColor(step.type) }}
                    >
                      {step.type === 'start'
                        ? 'Başlangıç'
                        : step.type === 'end'
                        ? 'Bitiş'
                        : step.type === 'approval'
                        ? 'Onay'
                        : 'Görev'}
                    </span>
                    {step.type !== 'start' && step.type !== 'end' && (
                      <button
                        onClick={() => deleteStep(step.id)}
                        className="step-delete-btn"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                  <input
                    type="text"
                    value={step.name}
                    onChange={(e) =>
                      updateStep(step.id, { name: e.target.value })
                    }
                    className="step-name-input"
                  />
                  
                  {/* Bağlantı noktaları */}
                  {step.type !== 'end' && (
                    <div
                      className={`connection-point connection-output ${isConnectingFromThis ? 'active' : ''}`}
                      style={{
                        left: outputPoint.x - step.position.x - 6,
                        top: outputPoint.y - step.position.y - 6,
                      }}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleConnectionPointClick(step.id, true)
                      }}
                      title="Bağlantı oluştur (tıkla)"
                    />
                  )}
                  {step.type !== 'start' && (
                    <div
                      className={`connection-point connection-input ${connectingFrom ? 'ready' : ''}`}
                      style={{
                        left: inputPoint.x - step.position.x - 6,
                        top: inputPoint.y - step.position.y - 6,
                      }}
                      onClick={(e) => {
                        e.stopPropagation()
                        if (connectingFrom) {
                          handleConnectionPointClick(step.id, false)
                        }
                      }}
                      title={connectingFrom ? "Bağlantıyı tamamla (tıkla)" : "Giriş noktası"}
                    />
                  )}
                </div>
              )
            })}
            
            {/* Bağlantı oluşturma modu bilgisi */}
            {connectingFrom && (
              <div className="connection-mode-hint">
                Bağlantı oluşturma modu: Bir adımın giriş noktasına tıklayın
                <button
                  onClick={() => setConnectingFrom(null)}
                  className="cancel-connection-btn"
                >
                  <X size={16} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Adım Ekleme Modal */}
      {showAddStepModal && (
        <div className="modal-overlay" onClick={closeAddStepModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Yeni Adım Ekle</h2>
              <button onClick={closeAddStepModal} className="modal-close-btn">
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Adım Tipi</label>
                <div className="step-type-selector">
                  <button
                    type="button"
                    className={`step-type-option step-type-start ${newStepData.type === 'start' ? 'active' : ''}`}
                    onClick={() => setNewStepData({ ...newStepData, type: 'start' })}
                  >
                    {newStepData.type === 'start' && <CheckCircle size={18} />}
                    <span>Başlangıç</span>
                  </button>
                  <button
                    type="button"
                    className={`step-type-option step-type-task ${newStepData.type === 'task' ? 'active' : ''}`}
                    onClick={() => setNewStepData({ ...newStepData, type: 'task' })}
                  >
                    {newStepData.type === 'task' && <CheckCircle size={18} />}
                    <span>Görev</span>
                  </button>
                  <button
                    type="button"
                    className={`step-type-option step-type-approval ${newStepData.type === 'approval' ? 'active' : ''}`}
                    onClick={() => setNewStepData({ ...newStepData, type: 'approval' })}
                  >
                    {newStepData.type === 'approval' && <CheckCircle size={18} />}
                    <span>Onay</span>
                  </button>
                  <button
                    type="button"
                    className={`step-type-option step-type-end ${newStepData.type === 'end' ? 'active' : ''}`}
                    onClick={() => setNewStepData({ ...newStepData, type: 'end' })}
                  >
                    {newStepData.type === 'end' && <CheckCircle size={18} />}
                    <span>Bitiş</span>
                  </button>
                </div>
              </div>
              <div className="form-group">
                <label>Başlık *</label>
                <input
                  type="text"
                  value={newStepData.name}
                  onChange={(e) => setNewStepData({ ...newStepData, name: e.target.value })}
                  placeholder="Adım başlığını girin"
                  className="modal-input"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Açıklama</label>
                <textarea
                  value={newStepData.description}
                  onChange={(e) => setNewStepData({ ...newStepData, description: e.target.value })}
                  placeholder="Adım açıklamasını girin (isteğe bağlı)"
                  rows={4}
                  className="modal-textarea"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={closeAddStepModal} className="btn btn-secondary">
                İptal
              </button>
              <button onClick={handleAddStep} className="btn btn-primary">
                <Plus size={18} />
                Adım Ekle
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorkflowEditor

