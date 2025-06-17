from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.row import RowStatus


class RowBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    google_sheet_row_id: Optional[str] = None


class RowCreate(RowBase):
    pass


class RowUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[RowStatus] = None


class RowInDBBase(RowBase):
    id: UUID
    status: RowStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Row(RowInDBBase):
    pass


class RowInDB(RowInDBBase):
    pass