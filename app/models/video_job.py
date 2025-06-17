from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base_class import Base


class VideoJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoModel(str, enum.Enum):
    KLING = "kling"
    VEO = "veo"


class VideoJob(Base):
    __tablename__ = "video_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    row_id = Column(UUID(as_uuid=True), ForeignKey("rows.id"), nullable=True)
    image_job_id = Column(UUID(as_uuid=True), ForeignKey("image_jobs.id"), nullable=True)
    
    # Input
    source_image_url = Column(String, nullable=False)
    motion_prompt = Column(Text, nullable=False)
    duration = Column(Integer, default=5, nullable=False)
    
    # Model
    model = Column(Enum(VideoModel), nullable=False)
    external_task_id = Column(String, nullable=True, index=True)  # KLING task ID or Veo job ID
    
    # Output
    video_url = Column(String, nullable=True)
    
    # Status
    status = Column(Enum(VideoJobStatus), default=VideoJobStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    row = relationship("Row", back_populates="video_jobs")
    source_image = relationship("ImageJob", back_populates="video_jobs")