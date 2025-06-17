from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import asyncio

from app.db.session import get_db
from app.models import VideoJob, VideoJobStatus, VideoModel
from app.schemas import video_job as video_schemas
from app.services import kling_service

router = APIRouter()


async def process_video_generation(job_id: str, db: AsyncSession):
    """
    Background task to process video generation
    """
    # Get job
    result = await db.execute(select(VideoJob).where(VideoJob.id == job_id))
    job = result.scalar_one()
    
    try:
        # Update status to processing
        job.status = VideoJobStatus.PROCESSING
        await db.commit()
        
        if job.model == VideoModel.KLING:
            # Create KLING task
            task_result = await kling_service.create_video_task(
                job.source_image_url,
                job.motion_prompt,
                job.duration
            )
            
            # Store external task ID
            job.external_task_id = task_result["task_id"]
            await db.commit()
            
            # Poll for completion
            max_attempts = 30  # 5 minutes with 10-second intervals
            for attempt in range(max_attempts):
                status = await kling_service.check_task_status(job.external_task_id)
                
                # Update progress
                job.progress = status["progress"]
                await db.commit()
                
                if status["status"] == "completed":
                    job.video_url = status["video_url"]
                    job.status = VideoJobStatus.COMPLETED
                    job.completed_at = datetime.utcnow()
                    break
                elif status["status"] == "failed":
                    raise Exception(status.get("error", "Video generation failed"))
                
                # Wait before next check
                await asyncio.sleep(10)
            else:
                raise Exception("Timeout waiting for video generation")
        
        else:
            # TODO: Implement Veo integration
            raise Exception(f"Model {job.model} not implemented yet")
        
    except Exception as e:
        # Update job with error
        job.status = VideoJobStatus.FAILED
        job.error_message = str(e)
    
    await db.commit()


@router.get("/", response_model=List[video_schemas.VideoJob])
async def list_video_jobs(
    skip: int = 0,
    limit: int = 100,
    row_id: Optional[UUID] = None,
    image_job_id: Optional[UUID] = None,
    status: Optional[VideoJobStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List video jobs with optional filtering
    """
    query = select(VideoJob).offset(skip).limit(limit).order_by(VideoJob.created_at.desc())
    
    if row_id:
        query = query.where(VideoJob.row_id == row_id)
    if image_job_id:
        query = query.where(VideoJob.image_job_id == image_job_id)
    if status:
        query = query.where(VideoJob.status == status)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return jobs


@router.post("/", response_model=video_schemas.VideoJob)
async def create_video_job(
    job_in: video_schemas.VideoJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new video generation job
    """
    job = VideoJob(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start background processing
    background_tasks.add_task(process_video_generation, str(job.id), db)
    
    return job


@router.get("/{job_id}", response_model=video_schemas.VideoJob)
async def get_video_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific video job
    """
    result = await db.execute(select(VideoJob).where(VideoJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    return job


@router.get("/external/{external_task_id}", response_model=video_schemas.VideoJob)
async def get_video_job_by_external_id(
    external_task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a video job by external task ID (e.g., KLING task ID)
    """
    result = await db.execute(
        select(VideoJob).where(VideoJob.external_task_id == external_task_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    return job


@router.post("/{job_id}/retry", response_model=video_schemas.VideoJob)
async def retry_video_job(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a failed video job
    """
    result = await db.execute(select(VideoJob).where(VideoJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    if job.status != VideoJobStatus.FAILED:
        raise HTTPException(status_code=400, detail="Can only retry failed jobs")
    
    # Reset job status
    job.status = VideoJobStatus.PENDING
    job.error_message = None
    job.progress = 0
    await db.commit()
    
    # Start background processing
    background_tasks.add_task(process_video_generation, str(job.id), db)
    
    return job