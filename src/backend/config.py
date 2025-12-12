"""
Configuration and constants for NACC Asset Declaration Digitization System
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = Path(__file__).parent / "output"  # Now in backend/output

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"  # Latest Gemini 2.5 Flash

# Extraction Method Configuration
USE_VISION = os.getenv("USE_VISION", "false").lower() == "true"  # Gemini Vision API (fast & accurate)
USE_DOCLING = os.getenv("USE_DOCLING", "true").lower() == "true"  # Docling OCR (slower, for comparison)
DOCLING_OCR_BACKEND = "easyocr"  # EasyOCR for Thai language support

# Imputation Configuration
USE_IMPUTATION = os.getenv("USE_IMPUTATION", "true").lower() == "true"
IMPUTATION_STRATEGY = os.getenv("IMPUTATION_STRATEGY", "forward_fill")  # forward_fill, mean, mode, none
VALIDATE_PDF_BEFORE_EXTRACTION = True

# CSV Output Files (13 files required)
OUTPUT_CSV_FILES = [
    "submitter_old_name.csv",
    "submitter_position.csv",
    "spouse_info.csv",
    "spouse_old_name.csv",
    "spouse_position.csv",
    "relative_info.csv",
    "statement.csv",
    "statement_detail.csv",
    "asset.csv",
    "asset_building_info.csv",
    "asset_land_info.csv",
    "asset_vehicle_info.csv",
    "asset_other_asset_info.csv",
]

# Database Schema - Field types for validation
FIELD_TYPES = {
    "text": ["title", "first_name", "last_name", "asset_name", "province"],
    "numeric": ["age", "valuation", "post_code"],
    "date": ["status_date", "acquiring_date", "ending_date", "latest_submitted_date"],
    "enum": ["status", "relationship", "asset_type_id", "position_period_type"],
}

# Date format patterns for Thai documents
DATE_PATTERNS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d %m %Y",
    "%d/%m/%y",
]

# Thai month mappings
THAI_MONTHS = {
    "ม.ค.": 1, "มกราคม": 1, "January": 1,
    "ก.พ.": 2, "กุมภาพันธ์": 2, "February": 2,
    "มี.ค.": 3, "มีนาคม": 3, "March": 3,
    "เม.ย.": 4, "เมษายน": 4, "April": 4,
    "พ.ค.": 5, "พฤษภาคม": 5, "May": 5,
    "มิ.ย.": 6, "มิถุนายน": 6, "June": 6,
    "ก.ค.": 7, "กรกฎาคม": 7, "July": 7,
    "ส.ค.": 8, "สิงหาคม": 8, "August": 8,
    "ก.ย.": 9, "กันยายน": 9, "September": 9,
    "ต.ค.": 10, "ตุลาคม": 10, "October": 10,
    "พ.ย.": 11, "พฤศจิกายน": 11, "November": 11,
    "ธ.ค.": 12, "ธันวาคม": 12, "December": 12,
}

# DQS Scoring weights
DQS_WEIGHTS = {
    "submitter_spouse": 0.25,
    "statement_details": 0.30,
    "assets": 0.30,
    "relatives": 0.15,
}

# Gemini prompt configuration
MAX_RETRIES = 3
TEMPERATURE = 0.1  # Low temperature for consistent extraction
TOP_P = 0.95
TOP_K = 40
