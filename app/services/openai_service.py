import httpx
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> str:
        """
        Generate image using OpenAI API
        Returns the image URL
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-image-1",
                        "prompt": prompt,
                        "n": 1,
                        "size": size
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    # Return URL or convert base64 to URL
                    image_data = data["data"][0]
                    if "url" in image_data:
                        return image_data["url"]
                    elif "b64_json" in image_data:
                        # TODO: Save base64 to file and return URL
                        return f"data:image/png;base64,{image_data['b64_json']}"
                        
                raise Exception("No image data in response")
                
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenAI API error: {e.response.text}")
                raise Exception(f"Image generation failed: {e.response.text}")
            except Exception as e:
                logger.error(f"Image generation error: {str(e)}")
                raise
    
    async def analyze_image(self, image_url: str) -> dict:
        """
        Analyze image and generate YAML description
        """
        system_prompt = """You are an expert image analyst. Analyze the provided image and generate a structured YAML description following this exact format:

scene:
  description: 
  mood: 
  time_of_day: 
  weather: 

subjects:
  - type: 
    description: 
    position: 
    attributes:
      - 

environment:
  setting: 
  foreground: 
  background: 
  lighting: 

visual_style:
  art_style: 
  color_palette: 
  composition: 

technical:
  camera_angle: 
  focal_length: 
  depth_of_field: 

Important guidelines:
1. Fill in ALL fields with specific, detailed descriptions in English
2. Use concrete, descriptive terms (avoid vague words)
3. For subjects, list all main elements in the image
4. Be accurate about technical aspects like camera angle and composition
5. Ensure the YAML is valid and properly formatted
6. Do not add any extra fields or explanations outside the YAML"""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4-vision-preview",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyze this image and generate the YAML description:"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_url,
                                            "detail": "high"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                yaml_content = data["choices"][0]["message"]["content"]
                
                # Extract preview info
                preview = self._extract_preview_from_yaml(yaml_content)
                
                return {
                    "yaml": yaml_content,
                    "preview": preview
                }
                
            except Exception as e:
                logger.error(f"Image analysis error: {str(e)}")
                raise
    
    async def yaml_to_prompt(self, yaml_content: str) -> str:
        """
        Convert YAML to natural language prompt
        """
        system_prompt = """Convert the following YAML description into a natural, flowing image generation prompt. 
The prompt should be detailed but concise, incorporating all the important elements from the YAML.
Focus on visual elements, style, and composition. Output only the prompt text, nothing else."""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": yaml_content
                            }
                        ],
                        "max_tokens": 300,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except Exception as e:
                logger.error(f"YAML to prompt conversion error: {str(e)}")
                raise
    
    def _extract_preview_from_yaml(self, yaml_content: str) -> dict:
        """
        Extract preview information from YAML
        """
        lines = yaml_content.split('\n')
        description = ''
        mood = ''
        main_subjects = []
        
        for line in lines:
            if 'description:' in line and not description:
                description = line.split('description:')[1].strip()
            if 'mood:' in line and not mood:
                mood = line.split('mood:')[1].strip()
            if 'type:' in line and line.strip().startswith('-'):
                subject = line.split('type:')[1].strip()
                if subject:
                    main_subjects.append(subject)
        
        return {
            "description": description or "Image analysis completed",
            "mainSubjects": main_subjects if main_subjects else ["No specific subjects identified"],
            "mood": mood or "neutral"
        }


openai_service = OpenAIService()