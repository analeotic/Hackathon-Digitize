# เครื่องมือและทรัพยากรที่ใช้

เอกสารนี้ระบุรายละเอียดเครื่องมือ ไลบรารี และทรัพยากรทั้งหมดที่ใช้ในระบบ Digitize ข้อมูลบัญชีทรัพย์สิน ป.ป.ช.

---

## 1. AI/ML Model

### Google Gemini 2.0 Flash (Experimental)
- **เวอร์ชัน:** gemini-2.0-flash-exp
- **ผู้พัฒนา:** Google DeepMind
- **ประเภท:** Large Language Model (LLM) with Multimodal capabilities
- **ความสามารถ:**
  - รองรับ PDF input โดยตรง (Multimodal)
  - อ่านและเข้าใจภาษาไทยได้ดีเยี่ยม
  - สร้าง Structured JSON output
  - Context window: 1 million tokens
  - ความเร็วสูง (Flash model)

- **ใช้สำหรับ:** อ่านและแปลง PDF เป็น Structured Data
- **ราคา:** ฟรี (Free tier: 15 RPM, 1M tokens/day)
- **เอกสาร:** https://ai.google.dev/gemini-api/docs
- **API:** https://aistudio.google.com/

---

## 2. Python Libraries

### Core Dependencies

#### 2.1 google-generativeai (>= 0.3.0)
- **เวอร์ชัน:** 0.3.0+
- **ผู้พัฒนา:** Google
- **GitHub:** https://github.com/google/generative-ai-python
- **ใช้สำหรับ:**
  - เชื่อมต่อกับ Gemini API
  - Upload และประมวลผล PDF
  - Generate structured responses

#### 2.2 pandas (>= 2.0.0)
- **เวอร์ชัน:** 2.0.0+
- **ผู้พัฒนา:** Pandas Development Team
- **Website:** https://pandas.pydata.org/
- **ใช้สำหรับ:**
  - อ่านและเขียนไฟล์ CSV
  - จัดการ DataFrame
  - Data transformation และ cleaning

#### 2.3 python-dateutil (>= 2.8.0)
- **เวอร์ชัน:** 2.8.0+
- **GitHub:** https://github.com/dateutil/dateutil
- **ใช้สำหรับ:**
  - จัดการและแปลงรูปแบบวันที่
  - รองรับรูปแบบวันที่ภาษาไทย

#### 2.4 tqdm (>= 4.65.0)
- **เวอร์ชัน:** 4.65.0+
- **GitHub:** https://github.com/tqdm/tqdm
- **ใช้สำหรับ:**
  - แสดง Progress bar ขณะประมวลผล
  - Monitoring การทำงาน

#### 2.5 PyPDF2 (>= 3.0.0)
- **เวอร์ชัน:** 3.0.0+
- **GitHub:** https://github.com/py-pdf/PyPDF2
- **ใช้สำหรับ:**
  - Fallback PDF reading
  - PDF metadata extraction

#### 2.6 Pillow (>= 10.0.0)
- **เวอร์ชัน:** 10.0.0+
- **Website:** https://python-pillow.org/
- **ใช้สำหรับ:**
  - Image processing (ถ้าต้องแปลง PDF เป็นภาพ)
  - รองรับ Multimodal input

#### 2.7 python-dotenv
- **GitHub:** https://github.com/theskumar/python-dotenv
- **ใช้สำหรับ:**
  - จัดการ Environment variables
  - โหลด API key จากไฟล์ .env

---

## 3. Development Tools

### 3.1 Python 3.8+
- **ภาษา:** Python
- **เวอร์ชันขั้นต่ำ:** 3.8
- **แนะนำ:** 3.10 หรือ 3.11
- **Download:** https://www.python.org/downloads/

### 3.2 pip
- **Package Manager:** pip
- **ใช้สำหรับ:** ติดตั้ง Python libraries

### 3.3 Virtual Environment (.venv)
- **เครื่องมือ:** venv (built-in Python)
- **ใช้สำหรับ:** แยก dependencies ของโปรเจค

---

## 4. Data Sources

### 4.1 NACC Asset Declaration Dataset
- **ที่มา:** Kaggle Competition - Hack the Asset Declaration
- **ประเภทข้อมูล:**
  - PDF Files: เอกสารบัญชีทรัพย์สินและหนี้สิน
  - CSV Files: Metadata และ Ground truth
- **ขนาด:**
  - Training: 69 documents
  - Test: 23 documents
- **ลิงก์:** https://www.kaggle.com/competitions/hack-the-assetdeclaration/

### 4.2 Database Schema
- **แหล่งข้อมูล:** Google Sheets
- **ลิงก์:** https://docs.google.com/spreadsheets/d/1QN87D5_3gXRjVCOoyan3bxHLh_wvQfud0BPiYGIofpM/
- **ใช้สำหรับ:** กำหนดโครงสร้าง CSV output

---

## 5. Algorithms & Techniques

### 5.1 Prompt Engineering
- **Technique:** Few-shot prompting + Schema-guided generation
- **การใช้งาน:**
  - สร้าง detailed prompt สำหรับ Gemini
  - ระบุโครงสร้าง JSON ที่ต้องการ
  - ให้ตัวอย่างและคำอธิบาย

### 5.2 Data Transformation Pipeline
- **แนวทาง:** ETL (Extract, Transform, Load)
- **ขั้นตอน:**
  1. Extract: Gemini อ่าน PDF → JSON
  2. Transform: แปลง JSON → DataFrame
  3. Load: บันทึกเป็น CSV files

### 5.3 Error Handling
- **Retry Logic:** Exponential backoff
- **ค่า Default:** MAX_RETRIES = 3
- **การจัดการ:**
  - Graceful degradation
  - Error logging
  - Skip failed documents และดำเนินการต่อ

---

## 6. Evaluation Metrics

### Digitization Quality Score (DQS)
- **สูตร:** Section-weighted mean of per-field scores
- **Score Range:** 0-1 (1 = perfect)
- **Field Scoring:**
  - **Text fields:** 1 - CER (Character Error Rate)
  - **Numeric fields:** 1 - Relative Error
  - **Date fields:** 
    - Exact match: 1.0
    - ±3 days: 0.8
    - Same month: 0.3
  - **Enum fields:** Exact match after normalization

- **Section Weights:**
  - Submitter & Spouse: 25%
  - Statement & Details: 30%
  - Assets: 30%
  - Relatives: 15%

---

## 7. System Architecture

### 7.1 โครงสร้างโค้ด

```
Hackathon-Digitize-/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env                    # API key configuration
│
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration และ constants
│   ├── extractor.py       # Gemini PDF extraction
│   ├── transformer.py     # JSON to CSV transformation
│   └── pipeline.py        # Main orchestration
│
├── hack-the-assetdeclaration-data/   # Dataset
│   ├── training/
│   ├── test final/
│   └── enum_type/
│
└── output/                # Output CSVs
    ├── train/
    └── test/
```

### 7.2 Data Flow

```
PDF File
   ↓
[Gemini API] ← Prompt Engineering
   ↓
Structured JSON
   ↓
[DataTransformer] ← Schema Mapping
   ↓
13 CSV Files
```

---

## 8. Operating System & Environment

### 8.1 Supported Platforms
- ✅ macOS (tested)
- ✅ Linux
- ✅ Windows (with adjustments for file paths)

### 8.2 System Requirements
- **RAM:** 4GB ขึ้นไป
- **Storage:** 500MB ขึ้นไป
- **Internet:** จำเป็น (สำหรับ Gemini API)

---

## 9. Version Control

### Git
- **System:** Git
- **Platform:** GitHub (optional)
- **ไฟล์ที่ ignore:**
  - `.venv/`
  - `output/`
  - `.env`
  - `__pycache__/`
  - `*.pyc`

---

## 10. References & Documentation

### Official Documentation
1. [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
2. [Pandas Documentation](https://pandas.pydata.org/docs/)
3. [Python Official Docs](https://docs.python.org/3/)

### Thai Language Processing
- ภาษาไทยใช้ encoding: UTF-8-SIG
- รองรับเดือนไทย (ม.ค., ก.พ., มี.ค., etc.)
- จัดการปี พ.ศ. โดยแปลงเป็น ค.ศ.

---

## 11. Open Source License

### ระบบนี้
- **License:** MIT License (หรือตามที่ Hackathon กำหนด)
- **การใช้งาน:** Open source หลังจบกิจกรรม

### Dependencies Licenses
- google-generativeai: Apache 2.0
- pandas: BSD 3-Clause
- python-dateutil: Apache 2.0 / BSD
- tqdm: MIT
- PyPDF2: BSD 3-Clause
- Pillow: HPND License

---

**อัปเดตล่าสุด:** 6 ธันวาคม 2568  
**สร้างสำหรับ:** NACC Asset Declaration Digitization Hackathon
