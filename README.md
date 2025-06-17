# Image to Video Backend API

FastAPI backend for the Image to Video generation application.

## Features

- **Image Generation**: OpenAI GPT image generation with YAML-based prompts
- **Video Generation**: KLING API integration for image-to-video conversion
- **Image Analysis**: O3/GPT-4 Vision for analyzing reference images
- **Job Management**: Async job processing with status tracking
- **Database**: SQLAlchemy with async support
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and update with your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `KLING_ACCESS_KEY`: Your KLING access key
- `KLING_SECRET_KEY`: Your KLING secret key

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Rows
- `GET /api/v1/rows` - List all rows
- `POST /api/v1/rows` - Create a new row
- `GET /api/v1/rows/{row_id}` - Get a specific row
- `PATCH /api/v1/rows/{row_id}` - Update a row
- `DELETE /api/v1/rows/{row_id}` - Delete a row

### Image Jobs
- `GET /api/v1/image-jobs` - List image generation jobs
- `POST /api/v1/image-jobs` - Create a new image generation job
- `GET /api/v1/image-jobs/{job_id}` - Get job status
- `POST /api/v1/image-jobs/{job_id}/rebuild` - Regenerate with new prompt
- `POST /api/v1/image-jobs/analyze` - Analyze an image
- `POST /api/v1/image-jobs/yaml-to-prompt` - Convert YAML to prompt

### Video Jobs
- `GET /api/v1/video-jobs` - List video generation jobs
- `POST /api/v1/video-jobs` - Create a new video generation job
- `GET /api/v1/video-jobs/{job_id}` - Get job status
- `GET /api/v1/video-jobs/external/{task_id}` - Get by external task ID
- `POST /api/v1/video-jobs/{job_id}/retry` - Retry a failed job

## Database

The application uses SQLAlchemy with support for both PostgreSQL (production) and SQLite (development).

### Models
- **Row**: Main data container for Google Sheets integration
- **ImageJob**: Image generation job tracking
- **VideoJob**: Video generation job tracking

## Deployment

### One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/senjinshuji/image-to-video-backend)

### Manual Deployment to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select this repository
4. Use these settings:
   - **Name**: image-to-video-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add environment variables:
   ```
   APP_ENV=production
   DEBUG=false
   CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
   
   # Add as secrets:
   OPENAI_API_KEY=your-openai-api-key
   KLING_ACCESS_KEY=your-kling-access-key
   KLING_SECRET_KEY=your-kling-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

6. Click "Create Web Service"

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing

```bash
pytest tests/
```

## License

MIT