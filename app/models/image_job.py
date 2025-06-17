from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base_class import Base


class ImageJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageJob(Base):
    __tablename__ = "image_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    row_id = Column(UUID(as_uuid=True), ForeignKey("rows.id"), nullable=True)
    
    # Input
    prompt = Column(Text, nullable=False)
    reference_image_url = Column(String, nullable=True)
    yaml_content = Column(Text, nullable=True)
    
    # Output
    image_url = Column(String, nullable=True)
    
    # Status
    status = Column(Enum(ImageJobStatus), default=ImageJobStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    model = Column(String, default="gpt-image-1", nullable=False)
    size = Column(String, default="1024x1024", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    row = relationship("Row", back_populates="image_jobs")
    video_jobs = relationship("VideoJob", back_populates="source_image", cascade="all, delete-orphan")