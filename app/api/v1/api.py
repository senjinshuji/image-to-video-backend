from fastapi import APIRouter

from app.api.v1.endpoints import rows, image_jobs, video_jobs

api_router = APIRouter()

api_router.include_router(rows.router, prefix="/rows", tags=["rows"])
api_router.include_router(image_jobs.router, prefix="/image-jobs", tags=["image-jobs"])
api_router.include_router(video_jobs.router, prefix="/video-jobs", tags=["video-jobs"])