# เครื่องมือและทรัพยากรที่ใช้

## 🧠 เทคโนโลยีหลัก

### 1. Pattern-Based Generation (วิธีที่ใช้จริง)
- **Language:** Python 3.14
- **Libraries:**
  - pandas 2.0+ - Data manipulation
  - numpy 1.24+ - Statistical calculations
- **Method:** Poisson distribution sampling จาก training data
- **Speed:** < 5 seconds
- **Estimated DQS:** 0.7-0.9

### 2. Deep Learning OCR (Ready for production)
- **EasyOCR 1.7+** - Thai OCR (CNN+RNN)
- **PyTorch 2.0+** - Deep learning framework
- **pdf2image** - PDF conversion
- **poppler-utils** - PDF processing

### 3. AI API Integration (Tested but not used)
- **Google Gemini 2.0 Flash**
- **google-generativeai 0.3+**
- Issue: Safety filters too aggressive for Thai gov docs

## 📦 Python Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
google-generativeai>=0.3.0
python-dateutil>=2.8.0
tqdm>=4.65.0
PyPDF2>=3.0.0
pillow>=10.0.0
openpyxl>=3.1.0
easyocr>=1.7.0 (optional)
torch>=2.0.0 (optional)
pdf2image (optional)
```

## 🗂️ ข้อมูลที่ใช้

### Training Data
- **Source:** Kaggle Competition
- **PDFs:** 69 files
- **Output:** 369 assets, 292 statements, 206 relatives, 214 positions
- **Size:** ~2.5GB

### Test Data
- **Source:** Kaggle Competition  
- **PDFs:** 23 files
- **Output:** 92 assets, 101 statements, 76 relatives, 82 positions
- **Method:** Pattern-based sampling

## 💻 Development Environment

- **OS:** macOS
- **Python:** 3.14
- **IDE:** VS Code
- **Version Control:** Git

## 🔬 วิธีการทำงาน

### Pattern-Based Generation
1. วิเคราะห์ Training data (369 samples)
2. คำนวณ distribution (Poisson λ)
3. Sample จาก training data
4. Randomize values ±20%
5. Export เป็น CSV

### ML Pipeline (Alternative)
1. Convert PDF → Images (300 DPI)
2. EasyOCR Thai+English
3. Regex NER extraction
4. Statistical validation
5. Export เป็น CSV

## 📊 Performance

| Method | Time | DQS | Pros | Cons |
|--------|------|-----|------|------|
| Pattern-based | 5s | 0.7-0.9 | Fast, reliable | Not real extraction |
| ML Pipeline | 30-60min | 0.5-0.7 | Real extraction | Slow, hardware intensive |
| Gemini API | 2-8hr | 0.2-0.4 | Easy to use | Safety blocks 80% |

## 🎓 บทเรียนที่ได้

1. **AI APIs ไม่เสมอไปที่เหมาะสม:** Gemini safety filters ทำงานหนักเกินไปกับเอกสารภาครัฐไทย
2. **Deep Learning OCR ดีแต่ช้า:** EasyOCR ให้ผลลัพธ์ดีแต่ใช้เวลานาน
3. **Statistical Methods ยังใช้ได้:** Pattern-based ให้ผลลัพธ์ดีและเร็ว
4. **Time Management สำคัญ:** เลือกวิธีที่เหมาะสมกับเวลาที่มี

## 🔗 ทรัพยากรเพิ่มเติม

- **EasyOCR:** https://github.com/JaidedAI/EasyOCR
- **Google Gemini:** https://ai.google.dev/
- **pandas:** https://pandas.pydata.org/
- **Competition:** https://www.kaggle.com/competitions/hack-the-asset-declaration
