"""
FastAPI server for NACC PDF Digitizer
Connects frontend PDF viewer with backend processing pipeline
"""
# Load .env first before any imports that use environment variables
import os
from pathlib import Path

# Load .env from project root with encoding handling
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    try:
        # Try reading with different encodings
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                with open(env_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content:
            # Parse and set environment variables manually
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
            print(f"✅ Loaded .env from {env_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not load .env: {e}")
else:
    print(f"⚠️ Warning: .env not found at {env_path}")

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import shutil
import sys
from typing import Optional

# Add the backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import local modules (works both as package and standalone)
try:
    from .pipeline import Pipeline
    from .config import OUTPUT_DIR
    from .confidence_scorer import add_confidence_scores
except ImportError:
    from pipeline import Pipeline
    from config import OUTPUT_DIR
    from confidence_scorer import add_confidence_scores

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="NACC PDF Digitizer API", version="1.0.0")

# Get frontend path
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

def compress_pdf_for_ocr(pdf_path: Path, target_dpi: int = 150) -> Optional[Path]:
    """
    Compress PDF for faster OCR processing while maintaining quality.

    Args:
        pdf_path: Path to original PDF
        target_dpi: Target DPI for images (150 is good balance of speed/quality)

    Returns:
        Path to compressed PDF, or None if compression failed/unnecessary
    """
    try:
        import fitz  # PyMuPDF

        original_size = pdf_path.stat().st_size

        # Skip if already small (less than 100KB)
        if original_size < 100 * 1024:
            print(f"   📄 PDF already small ({original_size // 1024}KB), skipping compression")
            return None

        print(f"   🗜️ Compressing PDF ({original_size // 1024}KB → optimizing for OCR)...")

        # Open PDF
        doc = fitz.open(pdf_path)

        # Create new compressed PDF
        compressed_path = pdf_path.parent / f"compressed_{pdf_path.name}"

        # Process each page - reduce image quality
        for page in doc:
            # Get all images on page
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]

                # Extract image
                base_image = doc.extract_image(xref)
                if base_image:
                    # Re-encode with lower quality
                    image_bytes = base_image["image"]

                    # Only compress if image is large
                    if len(image_bytes) > 50 * 1024:  # > 50KB
                        try:
                            from PIL import Image
                            import io

                            # Open and compress image
                            img_pil = Image.open(io.BytesIO(image_bytes))

                            # Resize if very large
                            max_dim = 2000  # Max dimension
                            if max(img_pil.size) > max_dim:
                                ratio = max_dim / max(img_pil.size)
                                new_size = (int(img_pil.width * ratio), int(img_pil.height * ratio))
                                img_pil = img_pil.resize(new_size, Image.LANCZOS)

                            # Convert to RGB if needed
                            if img_pil.mode in ('RGBA', 'P'):
                                img_pil = img_pil.convert('RGB')

                            # Compress to JPEG with good quality for OCR
                            output = io.BytesIO()
                            img_pil.save(output, format='JPEG', quality=85, optimize=True)

                            # Replace image in PDF
                            doc.update_stream(xref, output.getvalue())
                        except Exception as e:
                            pass  # Skip if image processing fails

        # Save with compression
        doc.save(
            compressed_path,
            garbage=4,           # Maximum garbage collection
            deflate=True,        # Compress streams
            clean=True,          # Clean unused objects
            deflate_images=True, # Compress images
            deflate_fonts=True   # Compress fonts
        )
        doc.close()

        compressed_size = compressed_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100

        print(f"   ✅ Compressed: {original_size // 1024}KB → {compressed_size // 1024}KB ({reduction:.0f}% smaller)")

        return compressed_path

    except ImportError:
        print("   ⚠️ PyMuPDF not installed, skipping compression")
        return None
    except Exception as e:
        print(f"   ⚠️ Compression failed: {e}, using original file")
        return None

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development/demo
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
    """Serve frontend HTML"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"message": "NACC PDF Digitizer API", "note": "Frontend not found"}

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
            # Temporarily disable compression for debugging
            # compressed_path = compress_pdf_for_ocr(tmp_path)
            # processing_path = compressed_path if compressed_path else tmp_path
            processing_path = tmp_path  # Use original file

            # Process PDF with pipeline
            print(f"📄 Processing {file.filename}...")
            print(f"   Region: ({x}, {y}) size: {w}x{h}")
            print(f"   Page: {page}, Scale: {scale}")

            # Run pipeline on single PDF
            # Use default IDs for single file processing
            result = pipeline.process_single_pdf(
                processing_path,
                submitter_id=1,  # Default ID for single file upload
                nacc_id=1        # Default ID for single file upload
            )

            # Clean up compressed file if created (disabled for now)
            # if compressed_path and compressed_path != tmp_path:
            #     try:
            #         compressed_path.unlink()
            #     except:
            #         pass

            # Get output directory
            output_dir = OUTPUT_DIR / "single"

            # Find generated CSVs
            csv_files = list(output_dir.glob("*.csv"))
            csv_names = [f.name for f in csv_files]

            # Add confidence scores to result
            scored_result = add_confidence_scores(result) if result else {}

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
                "data": scored_result.get("data", result) if result else {},
                "confidence": {
                    "overall": scored_result.get("overall_confidence", 0.0),
                    "field_stats": scored_result.get("field_count", {}),
                    "low_confidence_fields": scored_result.get("low_confidence_fields", []),
                    "warnings": scored_result.get("validation_warnings", [])
                }
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

# Mount static files for frontend assets (CSS, JS)
# This must be after all API routes to avoid conflicts
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting NACC PDF Digitizer API Server...")
    print("📡 Frontend: http://localhost:5001")
    print("📖 API Docs: http://localhost:5001/docs")
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
