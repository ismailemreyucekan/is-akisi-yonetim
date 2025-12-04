from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models import Workflow, WorkflowCreate, WorkflowUpdate
from datetime import datetime

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Geçici bellek içi (in-memory) veri yapısı
# Uygulama yeniden başlatıldığında bu veriler sıfırlanır.
workflows: List[dict] = []
next_id = 1

print("✅ Workflows router (in-memory) yüklendi")


@router.get("/", response_model=List[Workflow])
async def get_workflows():
    """Tüm iş akışlarını getir"""
    print("📥 GET /api/workflows isteği alındı (in-memory)")
    return workflows


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: int):
    """Tek bir iş akışını getir"""
    workflow = next((w for w in workflows if w["id"] == workflow_id), None)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="İş akışı bulunamadı")
    
    return workflow


@router.post("/", response_model=Workflow, status_code=201)
async def create_workflow(workflow_data: WorkflowCreate):
    """Yeni iş akışı oluştur"""
    global next_id
    print("📥 POST /api/workflows isteği alındı (in-memory)")
    print(f"   Body: {workflow_data.model_dump_json(indent=2)}")
    
    if not workflow_data.ad:
        raise HTTPException(status_code=400, detail="İş akışı adı gereklidir")
    
    now = datetime.now().isoformat()
    
    new_workflow = {
        "id": next_id,
        "ad": workflow_data.ad,
        "aciklama": workflow_data.aciklama,
        "adimlar": workflow_data.adimlar or [],
        "baglantilar": workflow_data.baglantilar or [],
        "status": workflow_data.status or "draft",
        "olusturma_tarihi": now,
        "guncelleme_tarihi": now
    }
    
    next_id += 1
    workflows.insert(0, new_workflow)
    
    return new_workflow


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: int, workflow_data: WorkflowUpdate):
    """İş akışını güncelle"""
    index = next((i for i, w in enumerate(workflows) if w["id"] == workflow_id), -1)
    
    if index == -1:
        raise HTTPException(status_code=404, detail="İş akışı bulunamadı")
    
    existing = workflows[index]
    now = datetime.now().isoformat()
    
    updated = {
        **existing,
        "ad": workflow_data.ad,
        "aciklama": workflow_data.aciklama if workflow_data.aciklama is not None else existing.get("aciklama"),
        "adimlar": workflow_data.adimlar if workflow_data.adimlar is not None else existing.get("adimlar", []),
        "baglantilar": workflow_data.baglantilar if workflow_data.baglantilar is not None else existing.get("baglantilar", []),
        "status": workflow_data.status if workflow_data.status is not None else existing.get("status", "draft"),
        "guncelleme_tarihi": now
    }
    
    workflows[index] = updated
    
    return updated


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: int):
    """İş akışını sil"""
    index = next((i for i, w in enumerate(workflows) if w["id"] == workflow_id), -1)
    
    if index == -1:
        raise HTTPException(status_code=404, detail="İş akışı bulunamadı")
    
    deleted = workflows.pop(index)
    
    return {"message": "İş akışı başarıyla silindi", "id": deleted["id"]}

