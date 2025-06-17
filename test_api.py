#!/usr/bin/env python3
"""
Simple test script for the API
"""
import asyncio
import httpx
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"


async def test_api():
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Image to Video API\n")
        
        # 1. Test health check
        print("1. Testing health check...")
        response = await client.get("http://localhost:8000/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # 2. Create a row
        print("2. Creating a row...")
        row_data = {
            "title": f"Test Row {datetime.now().isoformat()}",
            "description": "Test row created by API test script"
        }
        response = await client.post(f"{API_BASE}/rows", json=row_data)
        if response.status_code == 200:
            row = response.json()
            row_id = row["id"]
            print(f"   ✅ Row created: {row_id}")
            print(f"   Title: {row['title']}\n")
        else:
            print(f"   ❌ Failed: {response.text}\n")
            return
        
        # 3. List rows
        print("3. Listing rows...")
        response = await client.get(f"{API_BASE}/rows")
        rows = response.json()
        print(f"   Found {len(rows)} rows\n")
        
        # 4. Create an image job
        print("4. Creating an image job...")
        image_job_data = {
            "prompt": "A beautiful mountain landscape with a crystal clear lake",
            "row_id": row_id
        }
        response = await client.post(f"{API_BASE}/image-jobs", json=image_job_data)
        if response.status_code == 200:
            image_job = response.json()
            image_job_id = image_job["id"]
            print(f"   ✅ Image job created: {image_job_id}")
            print(f"   Status: {image_job['status']}\n")
        else:
            print(f"   ❌ Failed: {response.text}\n")
            return
        
        # 5. Check image job status
        print("5. Checking image job status...")
        for i in range(5):
            await asyncio.sleep(2)
            response = await client.get(f"{API_BASE}/image-jobs/{image_job_id}")
            job = response.json()
            print(f"   Attempt {i+1}: Status = {job['status']}")
            if job['status'] in ['completed', 'failed']:
                print(f"   Final status: {job['status']}")
                if job.get('image_url'):
                    print(f"   Image URL: {job['image_url']}")
                if job.get('error_message'):
                    print(f"   Error: {job['error_message']}")
                break
        print()
        
        # 6. Test image analysis
        print("6. Testing image analysis...")
        analyze_data = {
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
        }
        response = await client.post(f"{API_BASE}/image-jobs/analyze", json=analyze_data)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Image analyzed successfully")
            print(f"   Preview: {result['preview']['description'][:100]}...")
            print(f"   YAML length: {len(result['yaml'])} characters\n")
        else:
            print(f"   ❌ Failed: {response.text}\n")
        
        # 7. If image job completed, create video job
        if job.get('status') == 'completed' and job.get('image_url'):
            print("7. Creating video job...")
            video_job_data = {
                "source_image_url": job['image_url'],
                "motion_prompt": "Camera slowly pans from left to right",
                "model": "kling",
                "row_id": row_id,
                "image_job_id": image_job_id
            }
            response = await client.post(f"{API_BASE}/video-jobs", json=video_job_data)
            if response.status_code == 200:
                video_job = response.json()
                print(f"   ✅ Video job created: {video_job['id']}")
                print(f"   Status: {video_job['status']}")
                print(f"   Model: {video_job['model']}\n")
            else:
                print(f"   ❌ Failed: {response.text}\n")
        
        print("✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_api())