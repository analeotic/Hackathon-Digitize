"""
FastAPI server for NACC PDF Digitizer
Connects frontend PDF viewer with backend processing pipeline
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import tempfile
import shutil
from typing import Optional

from .pipeline import Pipeline
from .config import OUTPUT_DIR

app = FastAPI(title="NACC PDF Digitizer API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    global pipeline
    pipeline = Pipeline()
    print("✅ Pipeline initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NACC PDF Digitizer API",
        "version": "1.0.0",
        "endpoints": {
            "extract_region": "POST /extract_region",
            "download": "GET /download/{filename}",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline": "ready" if pipeline else "not initialized"
    }

@app.post("/extract_region")
async def extract_region(
    file: UploadFile = File(...),
    x: float = Form(0),
    y: float = Form(0),
    w: float = Form(...),
    h: float = Form(...),
    page: int = Form(1),
    scale: float = Form(1.0)
):
    """
    Extract data from specific region of PDF
    
    Args:
        file: PDF file
        x, y: Top-left corner coordinates
        w, h: Width and height of region
        page: Page number (1-indexed)
        scale: Scale factor used in rendering
    
    Returns:
        Extracted data JSON
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Process PDF with pipeline
            print(f"📄 Processing {file.filename}...")
            print(f"   Region: ({x}, {y}) size: {w}x{h}")
            print(f"   Page: {page}, Scale: {scale}")
            
            # Run pipeline on single PDF
            result = pipeline.process_single_pdf(tmp_path)
            
            # Get output directory
            output_dir = OUTPUT_DIR / "single"
            
            # Find generated CSVs
            csv_files = list(output_dir.glob("*.csv"))
            csv_names = [f.name for f in csv_files]
            
            return JSONResponse({
                "success": True,
                "message": f"Processed {file.filename} successfully",
                "region": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "page": page
                },
                "output": {
                    "csv_files": csv_names,
                    "count": len(csv_files)
                },
                "data": result if result else {}
            })
            
        finally:
            # Clean up temporary file
            tmp_path.unlink(missing_ok=True)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated CSV file"""
    # Look in single output directory
    output_dir = OUTPUT_DIR / "single"
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/csv"
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting NACC PDF Digitizer API Server...")
    print("📡 Frontend: http://localhost:8000")
    print("🔧 API: http://localhost:5000")
    print("📖 Docs: http://localhost:5000/docs")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
