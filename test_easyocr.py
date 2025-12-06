"""
Test EasyOCR extraction on Thai government PDF
"""
import easyocr
from pdf2image import convert_from_path
from pathlib import Path

# Initialize EasyOCR reader for Thai + English
print("🔧 Initializing EasyOCR (Thai + English)...")
reader = easyocr.Reader(['th', 'en'], gpu=False)  # gpu=False for CPU
print("✅ EasyOCR ready!")

# Convert PDF to images
pdf_path = Path("data/training/train input/Train_pdf/pdf/วทันยา_บุนนาค_สมาชิกสภาผู้แทนราษฎร_(ส.ส.)_กรณีพ้นจากตำแหน่ง_13_ธ.ค._2565.pdf")

print(f"\n📄 Converting PDF to images...")
images = convert_from_path(pdf_path, dpi=300, fmt='png')
print(f"📸 Converted {len(images)} pages")

# Test on first page
print(f"\n🔍 Running EasyOCR on page 1...")
import numpy as np
img_array = np.array(images[0])  # Convert PIL to numpy
result = reader.readtext(img_array, detail=0)  # detail=0 returns only text
text = '\n'.join(result)

print(f"\n📝 Extracted text ({len(text)} chars):")
print("="*60)
print(text[:1000])
print("="*60)

print(f"\n✅ EasyOCR extraction successful!")
print(f"   Total lines: {len(result)}")
print(f"   Total chars: {len(text)}")
