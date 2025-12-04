from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models import Issue, IssueCreate, IssueUpdate
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/issues", tags=["issues"])

# Geçici bellek içi (in-memory) veri yapısı
issues: List[dict] = []
next_issue_id = 1

print("✅ Issues router (in-memory) yüklendi")


@router.get("/", response_model=List[Issue])
async def get_issues(
    type: Optional[str] = None,
    status: Optional[str] = None,
    assignee: Optional[str] = None
):
    """Tüm issue'ları getir (filtreleme ile)"""
    filtered = issues
    
    if type:
        filtered = [i for i in filtered if i["type"] == type]
    if status:
        filtered = [i for i in filtered if i["status"] == status]
    if assignee:
        filtered = [i for i in filtered if i.get("assignee") == assignee]
    
    return filtered


@router.get("/{issue_id}", response_model=Issue)
async def get_issue(issue_id: int):
    """Tek bir issue'yu getir"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    return issue


@router.post("/", response_model=Issue, status_code=201)
async def create_issue(issue_data: IssueCreate):
    """Yeni issue oluştur"""
    global next_issue_id
    print("📥 POST /api/issues isteği alındı")
    
    if not issue_data.title:
        raise HTTPException(status_code=400, detail="Issue başlığı gereklidir")
    
    if issue_data.type not in ["task", "bug", "story", "epic"]:
        raise HTTPException(status_code=400, detail="Geçersiz issue tipi")
    
    if issue_data.status and issue_data.status not in ["todo", "in_progress", "done"]:
        raise HTTPException(status_code=400, detail="Geçersiz durum")
    
    now = datetime.now().isoformat()
    
    new_issue = {
        "id": next_issue_id,
        "title": issue_data.title,
        "type": issue_data.type,
        "status": issue_data.status or "todo",
        "priority": issue_data.priority or "medium",
        "description": issue_data.description,
        "assignee": issue_data.assignee,
        "tags": issue_data.tags or [],
        "attachments": [],
        "comments": [],
        "subtasks": [],
        "parentIssueId": issue_data.parentIssueId,
        "createdAt": now,
        "updatedAt": now
    }
    
    next_issue_id += 1
    issues.insert(0, new_issue)
    
    return new_issue


@router.put("/{issue_id}", response_model=Issue)
async def update_issue(issue_id: int, issue_data: IssueUpdate):
    """Issue'yu güncelle"""
    index = next((i for i, issue in enumerate(issues) if issue["id"] == issue_id), -1)
    
    if index == -1:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    existing = issues[index]
    now = datetime.now().isoformat()
    
    # Sadece gönderilen alanları güncelle
    updated = {**existing}
    if issue_data.title is not None:
        updated["title"] = issue_data.title
    if issue_data.type is not None:
        if issue_data.type not in ["task", "bug", "story", "epic"]:
            raise HTTPException(status_code=400, detail="Geçersiz issue tipi")
        updated["type"] = issue_data.type
    if issue_data.status is not None:
        if issue_data.status not in ["todo", "in_progress", "done"]:
            raise HTTPException(status_code=400, detail="Geçersiz durum")
        updated["status"] = issue_data.status
    if issue_data.priority is not None:
        updated["priority"] = issue_data.priority
    if issue_data.description is not None:
        updated["description"] = issue_data.description
    if issue_data.assignee is not None:
        updated["assignee"] = issue_data.assignee
    if issue_data.tags is not None:
        updated["tags"] = issue_data.tags
    if issue_data.parentIssueId is not None:
        updated["parentIssueId"] = issue_data.parentIssueId
    
    updated["updatedAt"] = now
    issues[index] = updated
    
    return updated


@router.delete("/{issue_id}")
async def delete_issue(issue_id: int):
    """Issue'yu sil"""
    index = next((i for i, issue in enumerate(issues) if issue["id"] == issue_id), -1)
    
    if index == -1:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    deleted = issues.pop(index)
    
    return {"message": "Issue başarıyla silindi", "id": deleted["id"]}


# Comment endpoints
@router.post("/{issue_id}/comments")
async def add_comment(issue_id: int, comment_data: dict):
    """Issue'ya yorum ekle"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    new_comment = {
        "id": str(uuid.uuid4()),
        "author": comment_data.get("author", "Anonim"),
        "text": comment_data.get("text", ""),
        "createdAt": datetime.now().isoformat()
    }
    
    issue["comments"].append(new_comment)
    issue["updatedAt"] = datetime.now().isoformat()
    
    return new_comment


@router.delete("/{issue_id}/comments/{comment_id}")
async def delete_comment(issue_id: int, comment_id: str):
    """Issue'dan yorum sil"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    issue["comments"] = [c for c in issue["comments"] if c["id"] != comment_id]
    issue["updatedAt"] = datetime.now().isoformat()
    
    return {"message": "Yorum silindi"}


# Subtask endpoints
@router.post("/{issue_id}/subtasks")
async def add_subtask(issue_id: int, subtask_data: dict):
    """Issue'ya alt görev ekle"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    new_subtask = {
        "id": str(uuid.uuid4()),
        "title": subtask_data.get("title", ""),
        "done": False
    }
    
    issue["subtasks"].append(new_subtask)
    issue["updatedAt"] = datetime.now().isoformat()
    
    return new_subtask


@router.put("/{issue_id}/subtasks/{subtask_id}")
async def update_subtask(issue_id: int, subtask_id: str, subtask_data: dict):
    """Alt görevi güncelle (done durumu veya title)"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    subtask = next((s for s in issue["subtasks"] if s["id"] == subtask_id), None)
    
    if not subtask:
        raise HTTPException(status_code=404, detail="Alt görev bulunamadı")
    
    if "title" in subtask_data:
        subtask["title"] = subtask_data["title"]
    if "done" in subtask_data:
        subtask["done"] = subtask_data["done"]
    
    issue["updatedAt"] = datetime.now().isoformat()
    
    return subtask


@router.delete("/{issue_id}/subtasks/{subtask_id}")
async def delete_subtask(issue_id: int, subtask_id: str):
    """Alt görevi sil"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    issue["subtasks"] = [s for s in issue["subtasks"] if s["id"] != subtask_id]
    issue["updatedAt"] = datetime.now().isoformat()
    
    return {"message": "Alt görev silindi"}


# Attachment endpoints
@router.post("/{issue_id}/attachments")
async def add_attachment(issue_id: int, attachment_data: dict):
    """Issue'ya dosya ekle (şimdilik sadece URL)"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    new_attachment = {
        "id": str(uuid.uuid4()),
        "fileName": attachment_data.get("fileName", ""),
        "url": attachment_data.get("url", "")
    }
    
    issue["attachments"].append(new_attachment)
    issue["updatedAt"] = datetime.now().isoformat()
    
    return new_attachment


@router.delete("/{issue_id}/attachments/{attachment_id}")
async def delete_attachment(issue_id: int, attachment_id: str):
    """Dosyayı sil"""
    issue = next((i for i in issues if i["id"] == issue_id), None)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue bulunamadı")
    
    issue["attachments"] = [a for a in issue["attachments"] if a["id"] != attachment_id]
    issue["updatedAt"] = datetime.now().isoformat()
    
    return {"message": "Dosya silindi"}

