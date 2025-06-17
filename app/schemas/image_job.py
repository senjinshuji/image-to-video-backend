from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.image_job import ImageJobStatus


class ImageJobBase(BaseModel):
    prompt: str = Field(..., min_length=1)
    reference_image_url: Optional[HttpUrl] = None
    size: str = Field(default="1024x1024", pattern="^(1024x1024|1792x1024|1024x1792)$")


class ImageJobCreate(ImageJobBase):
    row_id: Optional[UUID] = None


class ImageJobUpdate(BaseModel):
    status: Optional[ImageJobStatus] = None
    image_url: Optional[HttpUrl] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class ImageJobInDBBase(ImageJobBase):
    id: UUID
    row_id: Optional[UUID]
    status: ImageJobStatus
    image_url: Optional[HttpUrl]
    error_message: Optional[str]
    model: str
    yaml_content: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ImageJob(ImageJobInDBBase):
    pass


class ImageJobInDB(ImageJobInDBBase):
    pass


# Request/Response models
class ImageAnalyzeRequest(BaseModel):
    image_url: HttpUrl


class ImageAnalyzeResponse(BaseModel):
    yaml: str
    preview: dict


class YamlToPromptRequest(BaseModel):
    yaml: str


class YamlToPromptResponse(BaseModel):
    prompt: str