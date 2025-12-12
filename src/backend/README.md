# API Server

FastAPI server for NACC PDF Digitizer - connects frontend with backend processing pipeline.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start API Server
```bash
# Option 1: Using startup script
./src/backend/start_api.sh

# Option 2: Direct command
cd src/backend
python api_server.py

# Option 3: Using uvicorn
uvicorn backend.api_server:app --reload --port 5000
```

### 3. Start Frontend (in another terminal)
```bash
python src/frontend/server.py
```

### 4. Access
- Frontend: http://localhost:8000
- API: http://localhost:5000
- API Docs: http://localhost:5000/docs

## API Endpoints

### POST /extract_region
Extract data from PDF region.

**Request:**
- `file`: PDF file (multipart/form-data)
- `x`, `y`: Top-left coordinates
- `w`, `h`: Width and height
- `page`: Page number (1-indexed)
- `scale`: Rendering scale

**Response:**
```json
{
  "success": true,
  "message": "Processed file successfully",
  "region": {...},
  "output": {
    "csv_files": [...],
    "count": 13
  }
}
```

### GET /download/{filename}
Download generated CSV file.

### GET /health
Health check endpoint.

## Development

Start both servers:
```bash
# Terminal 1: API Server
python src/backend/api_server.py

# Terminal 2: Frontend Server
python src/frontend/server.py
```

## Architecture

```
Frontend (localhost:8000)
    ↓ HTTP POST
API Server (localhost:5000)
    ↓ Python call
Backend Pipeline
    ↓ CSV output
Download endpoint
```
