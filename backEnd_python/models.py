from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Workflow Models
class WorkflowStep(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    position: dict


class WorkflowConnection(BaseModel):
    id: str
    fromStepId: str
    toStepId: str


class WorkflowCreate(BaseModel):
    ad: str
    aciklama: Optional[str] = None
    adimlar: List[dict] = []
    baglantilar: List[dict] = []
    status: Optional[str] = "draft"


class WorkflowUpdate(BaseModel):
    ad: str
    aciklama: Optional[str] = None
    adimlar: Optional[List[dict]] = None
    baglantilar: Optional[List[dict]] = None
    status: Optional[str] = None


class Workflow(BaseModel):
    id: int
    ad: str
    aciklama: Optional[str] = None
    adimlar: List[dict] = []
    baglantilar: List[dict] = []
    status: str = "draft"
    olusturma_tarihi: str
    guncelleme_tarihi: str


# Issue Models
class Attachment(BaseModel):
    id: str
    fileName: str
    url: str


class Comment(BaseModel):
    id: str
    author: str
    text: str
    createdAt: str


class Subtask(BaseModel):
    id: str
    title: str
    done: bool = False


class IssueCreate(BaseModel):
    title: str
    type: str  # 'task', 'bug', 'story', 'epic'
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"  # 'low', 'medium', 'high', 'critical'
    description: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = []
    parentIssueId: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    parentIssueId: Optional[int] = None


class Issue(BaseModel):
    id: int
    title: str
    type: str
    status: str
    priority: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = []
    attachments: List[dict] = []
    comments: List[dict] = []
    subtasks: List[dict] = []
    parentIssueId: Optional[int] = None
    createdAt: str
    updatedAt: str

