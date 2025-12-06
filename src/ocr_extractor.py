"""
OCR-based PDF text extraction for Thai documents
Uses Tesseract OCR to extract text from images
"""
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path
from typing import List, Dict
import re


class OCRExtractor:
    """Extract text from PDF using Tesseract OCR"""
    
    def __init__(self):
        """Initialize OCR extractor"""
        # Configure Tesseract for Thai language
        self.ocr_config = r'--oem 3 --psm 6 -l tha+eng'
        
    def extract_text_from_pdf(self, pdf_path: Path, max_pages: int = None) -> str:
        """
        Extract text from PDF using OCR
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (None = all)
            
        Returns:
            Extracted text from all pages
        """
        print(f"   🖼️  Converting PDF to images...")
        
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300, fmt='png')
        
        if max_pages:
            images = images[:max_pages]
        
        print(f"   📸 Converted {len(images)} pages to images")
        print(f"   🔍 Running OCR on {len(images)} pages...")
        
        full_text = ""
        for page_num, image in enumerate(images):
            try:
                # Extract text using Tesseract
                page_text = pytesseract.image_to_string(image, config=self.ocr_config)
                
                if page_text.strip():
                    full_text += f"\n\n=== หน้า {page_num + 1} ===\n{page_text}"
                    
                # Show progress
                if (page_num + 1) % 5 == 0:
                    print(f"   ... processed {page_num + 1}/{len(images)} pages")
                    
            except Exception as e:
                print(f"   ⚠️ Error OCR page {page_num + 1}: {e}")
                continue
        
        print(f"   ✅ OCR complete: extracted {len(full_text)} characters")
        
        return full_text
    
    def extract_structured_data(self, text: str) -> Dict:
        """
        Extract structured data from OCR text using patterns
        
        Args:
            text: Raw OCR text
            
        Returns:
            Structured data dictionary
        """
        data = {
            "assets": [],
            "statements": [],
            "submitter_positions": [],
            "spouse_info": None,
            "relatives": []
        }
        
        # Extract asset information using patterns
        # Pattern for money: จำนวนเงิน / มูลค่า followed by numbers
        asset_values = re.findall(r'(?:จำนวนเงิน|มูลค่า|ราคา)[:\s]*([0-9,]+(?:\.[0-9]+)?)', text)
        
        # Pattern for dates: วันที่ DD/MM/YYYY or DD-MM-YYYY
        dates = re.findall(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text)
        
        # Pattern for names: Thai names (ขื่อ / นามสกุล)
        names = re.findall(r'(?:ชื่อ|นาม)[:\s]*([ก-๙a-zA-Z\s]+)', text)
        
        print(f"   📊 Found: {len(asset_values)} values, {len(dates)} dates, {len(names)} names")
        
        return data


if __name__ == "__main__":
    # Test OCR extraction
    extractor = OCRExtractor()
    sample_pdf = Path("data/training/train input/Train_pdf/pdf/วทันยา_บุนนาค_สมาชิกสภาผู้แทนราษฎร_(ส.ส.)_กรณีพ้นจากตำแหน่ง_13_ธ.ค._2565.pdf")
    
    if sample_pdf.exists():
        text = extractor.extract_text_from_pdf(sample_pdf, max_pages=3)
        print(f"\n📄 Extracted text (first 500 chars):\n{text[:500]}")
        
        data = extractor.extract_structured_data(text)
        print(f"\n📊 Structured data: {data}")
