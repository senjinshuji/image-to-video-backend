from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.models import ImageJob, ImageJobStatus
from app.schemas import image_job as image_schemas
from app.services import openai_service

router = APIRouter()


async def process_image_generation(job_id: str, db: AsyncSession):
    """
    Background task to process image generation
    """
    # Get job
    result = await db.execute(select(ImageJob).where(ImageJob.id == job_id))
    job = result.scalar_one()
    
    try:
        # Update status to processing
        job.status = ImageJobStatus.PROCESSING
        await db.commit()
        
        # Generate image
        image_url = await openai_service.generate_image(job.prompt, job.size)
        
        # Update job with result
        job.image_url = image_url
        job.status = ImageJobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        
    except Exception as e:
        # Update job with error
        job.status = ImageJobStatus.FAILED
        job.error_message = str(e)
    
    await db.commit()


@router.get("/", response_model=List[image_schemas.ImageJob])
async def list_image_jobs(
    skip: int = 0,
    limit: int = 100,
    row_id: Optional[UUID] = None,
    status: Optional[ImageJobStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List image jobs with optional filtering
    """
    query = select(ImageJob).offset(skip).limit(limit).order_by(ImageJob.created_at.desc())
    
    if row_id:
        query = query.where(ImageJob.row_id == row_id)
    if status:
        query = query.where(ImageJob.status == status)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return jobs


@router.post("/", response_model=image_schemas.ImageJob)
async def create_image_job(
    job_in: image_schemas.ImageJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new image generation job
    """
    job = ImageJob(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start background processing
    background_tasks.add_task(process_image_generation, str(job.id), db)
    
    return job


@router.get("/{job_id}", response_model=image_schemas.ImageJob)
async def get_image_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific image job
    """
    result = await db.execute(select(ImageJob).where(ImageJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Image job not found")
    
    return job


@router.post("/{job_id}/rebuild", response_model=image_schemas.ImageJob)
async def rebuild_image_job(
    job_id: UUID,
    prompt: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new image job with updated prompt
    """
    # Get original job
    result = await db.execute(select(ImageJob).where(ImageJob.id == job_id))
    original_job = result.scalar_one_or_none()
    
    if not original_job:
        raise HTTPException(status_code=404, detail="Image job not found")
    
    # Create new job
    new_job = ImageJob(
        row_id=original_job.row_id,
        prompt=prompt,
        reference_image_url=original_job.reference_image_url,
        size=original_job.size,
        model=original_job.model
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Start background processing
    background_tasks.add_task(process_image_generation, str(new_job.id), db)
    
    return new_job


@router.post("/analyze", response_model=image_schemas.ImageAnalyzeResponse)
async def analyze_image(
    request: image_schemas.ImageAnalyzeRequest
):
    """
    Analyze an image and generate YAML description
    """
    try:
        result = await openai_service.analyze_image(str(request.image_url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/yaml-to-prompt", response_model=image_schemas.YamlToPromptResponse)
async def yaml_to_prompt(
    request: image_schemas.YamlToPromptRequest
):
    """
    Convert YAML to natural language prompt
    """
    try:
        prompt = await openai_service.yaml_to_prompt(request.yaml)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))