from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.video_job import VideoJobStatus, VideoModel


class VideoJobBase(BaseModel):
    source_image_url: HttpUrl
    motion_prompt: str = Field(..., min_length=1)
    model: VideoModel
    duration: int = Field(default=5, ge=1, le=10)


class VideoJobCreate(VideoJobBase):
    row_id: Optional[UUID] = None
    image_job_id: Optional[UUID] = None


class VideoJobUpdate(BaseModel):
    status: Optional[VideoJobStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    video_url: Optional[HttpUrl] = None
    error_message: Optional[str] = None
    external_task_id: Optional[str] = None
    completed_at: Optional[datetime] = None


class VideoJobInDBBase(VideoJobBase):
    id: UUID
    row_id: Optional[UUID]
    image_job_id: Optional[UUID]
    status: VideoJobStatus
    progress: int
    video_url: Optional[HttpUrl]
    error_message: Optional[str]
    external_task_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VideoJob(VideoJobInDBBase):
    pass


class VideoJobInDB(VideoJobInDBBase):
    pass