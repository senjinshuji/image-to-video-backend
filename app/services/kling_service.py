import jwt
import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class KlingService:
    def __init__(self):
        self.access_key = settings.KLING_ACCESS_KEY
        self.secret_key = settings.KLING_SECRET_KEY
        self.base_url = "https://api-singapore.klingai.com/v1"
        
    def _generate_jwt(self) -> str:
        """
        Generate JWT token for KLING API authentication
        """
        payload = {
            "iss": self.access_key,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "nbf": datetime.utcnow() - timedelta(seconds=5)
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm="HS256",
            headers={"alg": "HS256", "typ": "JWT"}
        )
    
    def _process_image_url(self, image_url: str) -> str:
        """
        Process image URL for KLING API
        Convert data URL to base64 string if needed
        """
        if image_url.startswith('data:'):
            # Extract base64 part from data URL
            base64_part = image_url.split(',')[1] if ',' in image_url else image_url
            return base64_part
        elif image_url.startswith('http'):
            # HTTP URLs are accepted as-is
            return image_url
        else:
            # Assume it's already base64
            return image_url
    
    async def create_video_task(self, image_url: str, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """
        Create a video generation task
        Returns task info including task_id
        """
        token = self._generate_jwt()
        processed_image = self._process_image_url(image_url)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "kling-v1",
            "image": processed_image,
            "prompt": prompt,
            "duration": str(duration),  # Must be string
            "aspect_ratio": "16:9",
            "cfg_scale": 0.5,
            "mode": "std"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/videos/image2video",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("code") != 0:
                    raise Exception(f"KLING API error: {result.get('message', 'Unknown error')}")
                
                return {
                    "task_id": result["data"]["task_id"],
                    "status": "submitted"
                }
                
            except httpx.HTTPStatusError as e:
                logger.error(f"KLING API HTTP error: {e.response.text}")
                raise Exception(f"Video generation failed: {e.response.text}")
            except Exception as e:
                logger.error(f"KLING video generation error: {str(e)}")
                raise
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation task
        """
        token = self._generate_jwt()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/videos/image2video/{task_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("code") != 0:
                    raise Exception(f"KLING API error: {result.get('message', 'Unknown error')}")
                
                data = result["data"]
                
                # Map KLING status to our status
                status_map = {
                    "submitted": {"status": "pending", "progress": 0},
                    "processing": {"status": "processing", "progress": 50},
                    "succeed": {"status": "completed", "progress": 100},
                    "failed": {"status": "failed", "progress": 0}
                }
                
                mapped_status = status_map.get(
                    data.get("task_status", "processing"),
                    {"status": "processing", "progress": 50}
                )
                
                response_data = {
                    "task_id": task_id,
                    "status": mapped_status["status"],
                    "progress": mapped_status["progress"]
                }
                
                # Add video URL if completed
                if data.get("task_status") == "succeed" and data.get("works"):
                    response_data["video_url"] = data["works"][0]["url"]
                
                # Add error message if failed
                if data.get("task_status") == "failed":
                    response_data["error"] = data.get("task_status_msg", "Video generation failed")
                
                return response_data
                
            except Exception as e:
                logger.error(f"KLING status check error: {str(e)}")
                raise
    
    async def wait_for_completion(self, task_id: str, max_wait_seconds: int = 300) -> str:
        """
        Wait for video generation to complete
        Returns the video URL when ready
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < max_wait_seconds:
            try:
                status = await self.check_task_status(task_id)
                
                if status["status"] == "completed" and status.get("video_url"):
                    return status["video_url"]
                elif status["status"] == "failed":
                    raise Exception(status.get("error", "Video generation failed"))
                
                # Wait before next check
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error while waiting for completion: {str(e)}")
                raise
        
        raise Exception("Timeout waiting for video generation")


kling_service = KlingService()