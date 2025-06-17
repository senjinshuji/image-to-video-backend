from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base_class import Base


class RowStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Row(Base):
    __tablename__ = "rows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_sheet_row_id = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(RowStatus), default=RowStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    image_jobs = relationship("ImageJob", back_populates="row", cascade="all, delete-orphan")
    video_jobs = relationship("VideoJob", back_populates="row", cascade="all, delete-orphan")