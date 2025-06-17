from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models import Row
from app.schemas import row as row_schemas

router = APIRouter()


@router.get("/", response_model=List[row_schemas.Row])
async def list_rows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all rows with optional filtering
    """
    query = select(Row).offset(skip).limit(limit)
    
    if status:
        query = query.where(Row.status == status)
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    return rows


@router.post("/", response_model=row_schemas.Row)
async def create_row(
    row_in: row_schemas.RowCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new row
    """
    row = Row(**row_in.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    
    return row


@router.get("/{row_id}", response_model=row_schemas.Row)
async def get_row(
    row_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific row by ID
    """
    result = await db.execute(select(Row).where(Row.id == row_id))
    row = result.scalar_one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    
    return row


@router.patch("/{row_id}", response_model=row_schemas.Row)
async def update_row(
    row_id: UUID,
    row_update: row_schemas.RowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a row
    """
    result = await db.execute(select(Row).where(Row.id == row_id))
    row = result.scalar_one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    
    # Update only provided fields
    update_data = row_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(row, field, value)
    
    await db.commit()
    await db.refresh(row)
    
    return row


@router.delete("/{row_id}")
async def delete_row(
    row_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a row
    """
    result = await db.execute(select(Row).where(Row.id == row_id))
    row = result.scalar_one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    
    await db.delete(row)
    await db.commit()
    
    return {"message": "Row deleted successfully"}