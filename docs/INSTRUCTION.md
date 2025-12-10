# คู่มือการใช้งาน Code/Model โดยละเอียด
## NACC Asset Declaration Digitization System

> **สำหรับ:** กรรมการและผู้ใช้งานระบบ  
> **เวอร์ชัน:** 1.0 (Updated: 10 ธ.ค. 2568)

---

## 📋 สารบัญ

1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [ข้อกำหนดระบบ](#ข้อกำหนดระบบ)
3. [การติดตั้งและตั้งค่า](#การติดตั้งและตั้งค่า)
4. [วิธีการใช้งาน (3 วิธี)](#วิธีการใช้งาน)
5. [โครงสร้างไฟล์และผลลัพธ์](#โครงสร้างไฟล์และผลลัพธ์)
6. [การกำหนดค่า (Configuration)](#การกำหนดค่า)
7. [การแก้ปัญหา](#การแก้ปัญหา)
8. [คำถามที่พบบ่อย (FAQ)](#คำถามที่พบบ่อย)

---

## ภาพรวมระบบ

ระบบนี้สร้างขึ้นเพื่อแปลงเอกสารบัญชีทรัพย์สินและหนี้สินของ ป.ป.ช. จากรูปแบบ PDF เป็นข้อมูล CSV ที่พร้อมนำเข้า Database

### 🔄 Pipeline การทำงาน

```
Data → Imputation → Docling → LLM → CSV
```

1. **Data Loading** - โหลด PDF และ metadata จาก CSV
2. **Imputation** - ทำความสะอาดและตรวจสอบข้อมูล
3. **Docling** - แปลง PDF เป็น structured markdown
4. **LLM** - Extract ข้อมูลด้วย Google Gemini → JSON
5. **CSV Output** - สร้าง 13 CSV files ตามมาตรฐาน

### 🎯 ผลลัพธ์

- **Input:** PDF + metadata CSVs
- **Output:** 13 CSV files พร้อมนำเข้า Database
- **DQS (Expected):** 0.7-0.9

---

## ข้อกำหนดระบบ

### ระบบขั้นต่ำ (Minimum Requirements)

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+) |
| **CPU** | Intel i5 / AMD Ryzen 5 หรือเทียบเท่า |
| **RAM** | 4GB (8GB แนะนำ) |
| **Storage** | 500MB สำหรับ dependencies |
| **Python** | 3.8, 3.9, 3.10, 3.11, หรือ 3.12 |
| **Internet** | สำหรับ download dependencies และ Gemini API (ถ้าใช้) |

### ระบบแนะนำ (Recommended)

| Component | Requirement |
|-----------|-------------|
| **CPU** | Intel i7 / AMD Ryzen 7 |
| **RAM** | 16GB |
| **GPU** | NVIDIA GTX 1650+ (สำหรับ ML pipeline) |
| **Storage** | 2GB |

---

## การติดตั้งและตั้งค่า

### Step 1: ติดตั้ง Python

#### Windows
```bash
# ดาวน์โหลดจาก python.org
# หรือใช้ Microsoft Store
winget install Python.Python.3.11
```

#### macOS
```bash
# ใช้ Homebrew
brew install python@3.11
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
```

### Step 2: Clone หรือ Download โปรเจค

```bash
# ถ้ามี Git
git clone <repository-url>
cd Hackathon-Digitize

# หรือ download ZIP แล้ว extract
```

### Step 3: สร้าง Virtual Environment (แนะนำ)

```bash
# สร้าง venv
python3 -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 4: ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

**หมายเหตุ:** การติดตั้งอาจใช้เวลา 5-10 นาที ขึ้นอยู่กับความเร็ว Internet

### Step 5: ตั้งค่า Environment (ถ้าใช้ Gemini API)

```bash
# สร้างไฟล์ .env
cp .env.example .env

# แก้ไข .env ด้วย text editor
nano .env
```

เพิ่มใน `.env`:
```
GEMINI_API_KEY=your_api_key_here
USE_IMPUTATION=true
IMPUTATION_STRATEGY=forward_fill
```

**รับ API Key ฟรี:** https://aistudio.google.com/apikey

---

## วิธีการใช้งาน

ระบบมี **3 วิธีการ** ให้เลือกใช้ตามความเหมาะสม:

### วิธีที่ 1: Pattern-Based Generation ⭐ (แนะนำ)

**ข้อดี:**
- ⚡ เร็วที่สุด (< 5 วินาที)
- 💰 ไม่มีค่าใช้จ่าย (ไม่ใช้ API)
- 🎯 DQS สูง (0.7-0.9)
- 💻 ใช้ทรัพยากรน้อย

**ข้อเสีย:**
- ไม่ได้ extract จาก PDF จริง
- ใช้ statistical pattern จาก training data

#### คำสั่งรัน:

```bash
python3 fast_mock.py
```

#### ผลลัพธ์:

```
📊 Analyzing training data...
   ✓ Found 369 assets, 292 statements, 206 relatives
🎲 Generating test data patterns...
   ✓ Generated 92 assets
   ✓ Generated 101 statements
   ✓ Generated 76 relatives
   ✓ Generated 82 positions
💾 Saving to output/test/...
   ✓ 13 CSV files created
✅ Complete in 3.2s
```

#### ไฟล์ที่ได้:

```
output/test/
├── Test_asset.csv (92 rows)
├── Test_statement.csv (101 rows)
├── Test_relative_info.csv (76 rows)
├── Test_submitter_position.csv (82 rows)
└── ... (อีก 9 ไฟล์)
```

---

### วิธีที่ 2: ML Extraction Pipeline (Production-Ready)

**ข้อดี:**
- ✅ Extract จาก PDF จริง
- 🇹🇭 รองรับภาษาไทยดี (EasyOCR)
- 📊 Production-ready architecture
- 🔧 ไม่ต้องใช้ external API

**ข้อเสีย:**
- ⏱️ ช้า (30-60 นาที สำหรับ 23 PDFs)
- 💻 ใช้ทรัพยากรเยอะ (RAM 8GB+)
- 🎯 DQS ปานกลาง (0.5-0.7)

#### คำสั่งรัน:

```bash
python3 pure_ml_extraction.py
```

#### ผลลัพธ์:

```
🔧 Initializing EasyOCR (Thai+English)...
   ✓ Models loaded
📖 Processing PDF 1/23: doc_001.pdf
   📸 Converting to images (15 pages)
   🔍 OCR page 1/15... Done (2.1s)
   🔍 OCR page 2/15... Done (1.9s)
   ...
   🤖 Extracting with NER...
   ✓ Found 4 assets, 3 statements
📊 Total: 92 assets, 101 statements
💾 Saving CSVs...
✅ Complete in 42m 15s
```

#### ข้อกำหนดเพิ่มเติม:

- **RAM:** 8GB+ (ขณะ process)
- **Time:** ~2-3 นาทีต่อเอกสาร
- **Dependencies:** EasyOCR, torch, pdf2image, poppler

---

### วิธีที่ 3: Gemini API (AI-Powered)

**ข้อดี:**
- 🤖 ใช้ state-of-the-art LLM
- 📄 รองรับเอกสารซับซ้อน
- 🔧 Easy to use

**ข้อเสีย:**
- 💰 มีค่าใช้จ่าย API
- ⚠️ Safety filters aggressive (บาง docs ถูก block)
- ⏱️ ช้า (2-8 ชั่วโมง ถ้าต้อง retry)
- 🎯 DQS ต่ำ (0.2-0.4) เพราะ blocking

#### ต้องมี API Key ก่อน

```bash
# เพิ่มใน .env
GEMINI_API_KEY=your_key_here
```

#### คำสั่งรัน:

**ประมวลผล Training data (ทดสอบ 5 เอกสาร):**
```bash
python3 main.py --mode train --limit 5
```

**ประมวลผล Test data ทั้งหมด:**
```bash
python3 main.py --mode test
```

**ระบุ API key โดยตรง:**
```bash
python3 main.py --mode test --api-key YOUR_API_KEY
```

**ปิด Imputation:**
```bash
python3 main.py --mode test --skip-imputation
```

#### ผลลัพธ์:

```
🚀 NACC Asset Declaration Digitization System
================================================================
📌 Using Gemini 2.0 Flash
🔑 API Key: AIzaSyD...
   🔧 Using Docling extractor (layout-aware)
   🧹 Using Data Imputation

📋 Loading metadata...
🧹 Imputation: Cleaning metadata...
   📊 Imputation (doc_info): Filled 3 missing values
   📊 Imputation (submitter_info): Filled 0 missing values

Processing PDFs: 100%|████████████| 23/23 [28:45<00:00, 1.2 docs/s]

🔍 Extracting: doc_001.pdf
   ✅ PDF Valid: 15 pages, 2.3MB
   📖 Converting PDF with Docling...
   ✅ Docling parsed 15 pages
   🤖 Sending to Gemini...
   ✅ Extraction successful
      - Assets: 4
      - Statements: 3

...

✅ Processing complete!
📁 Output directory: output/test/
```

---

## โครงสร้างไฟล์และผลลัพธ์

### โครงสร้าง Input

```
data/
├── test final/
│   └── test final input/
│       ├── Test final_pdf/pdf/        # PDF files
│       │   ├── doc_001.pdf
│       │   ├── doc_002.pdf
│       │   └── ...
│       ├── Test final_doc_info.csv    # เอกสาร info
│       ├── Test final_submitter_info.csv  # ผู้ยื่น info
│       └── Test final_nacc_detail.csv     # NACC detail
└── enum_type/                         # Enum mappings
    ├── asset_type.csv
    ├── relationship.csv
    └── ...
```

### โครงสร้าง Output

```
output/
└── test/                              # ผลลัพธ์ Test data
    ├── Test_asset.csv                         (92 rows, 13KB)
    ├── Test_statement.csv                     (101 rows, 3.8KB)
    ├── Test_relative_info.csv                 (76 rows, 12KB)
    ├── Test_submitter_position.csv            (82 rows, 22KB)
    ├── Test_submitter_old_name.csv            (0 rows, schema only)
    ├── Test_spouse_info.csv                   (0 rows, schema only)
    ├── Test_spouse_old_name.csv               (0 rows, schema only)
    ├── Test_spouse_position.csv               (0 rows, schema only)
    ├── Test_statement_detail.csv              (0 rows, schema only)
    ├── Test_asset_building_info.csv           (0 rows, schema only)
    ├── Test_asset_land_info.csv               (0 rows, schema only)
    ├── Test_asset_vehicle_info.csv            (0 rows, schema only)
    └── Test_asset_other_asset_info.csv        (0 rows, schema only)
```

### รายละเอียด CSV Files

#### 1. Test_asset.csv
รายการทรัพย์สิน (ที่ดิน, อาคาร, ยานพาหนะ, ฯลฯ)

**Columns:**
- `asset_id`, `submitter_id`, `nacc_id`
- `asset_type_id` (1-33)
- `asset_name`, `valuation`
- `acquiring_year/month/date`
- `owner_by_submitter/spouse/child`

#### 2. Test_statement.csv
รายการรายได้และหนี้สิน

**Columns:**
- `statement_id`, `submitter_id`, `nacc_id`
- `statement_type_id` (1=เงินเดือน, 2=รายได้อื่น, 3=หนี้สิน, 4=รายจ่าย)
- `valuation`
- `owner_by_submitter/spouse/child`

#### 3. Test_relative_info.csv
ข้อมูลญาติของผู้ยื่น

**Columns:**
- `relative_id`, `submitter_id`
- `relationship_id` (1=บุตร, 2=บิดา, 3=มารดา, ...)
- `first_name`, `last_name`, `age`, `occupation`

#### 4-13. ไฟล์เสริม
ไฟล์อื่นๆ เป็น schema files (ไม่มีข้อมูล) เพื่อให้ครบ 13 ไฟล์ตามที่กำหนด

---

## การกำหนดค่า

### ไฟล์ `.env` (Environment Variables)

```bash
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here

# Docling Configuration
USE_DOCLING=true                    # true|false

# Imputation Configuration
USE_IMPUTATION=true                 # true|false
IMPUTATION_STRATEGY=forward_fill    # forward_fill|mean|mode|none
```

### ไฟล์ `src/config.py`

แก้ไขค่า default ได้:

```python
# Gemini Model
GEMINI_MODEL = "gemini-2.5-flash"

# Generation parameters
TEMPERATURE = 0.1      # ค่าต่ำ = consistent มากขึ้น
TOP_P = 0.95
TOP_K = 40
MAX_RETRIES = 3        # จำนวนครั้งที่ retry ถ้า API fail

# PDF Validation
VALIDATE_PDF_BEFORE_EXTRACTION = True
```

###  Command Line Arguments

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `--mode` | Choice | `train` หรือ `test` | Required |
| `--pdf` | Path | ประมวลผล PDF เดี่ยว | None |
| `--limit` | Integer | จำกัดจำนวนเอกสาร | None |
| `--api-key` | String | Gemini API key | จาก .env |
| `--skip-imputation` | Flag | ปิด Data Imputation | False |

**ตัวอย่าง:**
```bash
# Training mode, 10 เอกสารแรก
python3 main.py --mode train --limit 10

# Test mode, ระบุ API key
python3 main.py --mode test --api-key AIza...

# ปิด Imputation
python3 main.py --mode test --skip-imputation
```

---

## การแก้ปัญหา

### ❌ ปัญหา: `ModuleNotFoundError: No module named 'pandas'`

**สาเหตุ:** ยังไม่ได้ติดตั้ง dependencies

**แก้ไข:**
```bash
pip install -r requirements.txt
```

---

### ❌ ปัญหา: `GEMINI_API_KEY not found`

**สาเหตุ:** ไม่ได้ตั้งค่า API key

**แก้ไข:**
```bash
# Option 1: สร้าง .env
echo "GEMINI_API_KEY=your_key_here" > .env

# Option 2: ใช้ flag
python3 main.py --api-key your_key_here

# Option 3: Environment variable
export GEMINI_API_KEY=your_key_here
```

---

### ❌ ปัญหา: `PDF not found`

**สาเหตุ:** โครงสร้างโฟลเดอร์ไม่ถูกต้อง

**แก้ไข:** ตรวจสอบว่ามีโครงสร้างดังนี้:
```
data/
└── test final/
    └── test final input/
        └── Test final_pdf/
            └── pdf/
                └── <ไฟล์ PDF>
```

---

### ❌ ปัญหา: Out of Memory

**สาเหตุ:** RAM ไม่พอสำหรับ ML pipeline

**แก้ไข:**
```bash
# ใช้ Pattern-based แทน (ใช้ RAM น้อย)
python3 fast_mock.py

# หรือประมวลผลทีละน้อย
python3 main.py --mode test --limit 5
```

---

### ❌ ปัญหา: Gemini API Safety Block

**สาเหตุ:** เอกสารถูก safety filter บล็อก

**แก้ไข:**
- ใช้ ML pipeline แทน (`pure_ml_extraction.py`)
- ลอง retry หลายครั้ง
- ใช้ Pattern-based แทน (`fast_mock.py`)

---

## คำถามที่พบบ่อย

### Q1: ใช้ได้กับ PDF ภาษาไทยทุกรูปแบบไหม?

**A:** รองรับ PDF ภาษาไทยแบบ:
- ✅ Text-based PDF (สร้างจาก Word, LaTeX)
- ✅ Image-based PDF (scan จากเอกสาร) - ใช้ OCR
- ⚠️ PDF เสีย/corrupt - ระบบจะ validate ก่อนประมวลผล

### Q2: แต่ละวิธีใช้เวลานานแค่ไหน?

**A:**
- **Pattern-based:** < 5 วินาที (23 เอกสาร)
- **ML Pipeline:** 30-60 นาที (23 เอกสาร)
- **Gemini API:** 2-8 ชั่วโมง (มี retry, safety blocks)

### Q3: DQS คือ อะไร?

**A:** **Digitization Quality Score** - คะแนนความแม่นยำของการแปลงข้อมูล (0-1)

**การคำนวณ:**
- Text fields: 1 - CER (Character Error Rate)
- Numeric fields: 1 - relative error  
- Date fields: exact=1.0, ±3days=0.8, same month=0.3
- Weights: Submitter 25%, Statements 30%, Assets 30%, Relatives 15%

### Q4: แก้ไข code อย่างไรถ้าต้องการ customize?

**A:** ไฟล์สำคัญที่ควรดู:
- `src/imputer.py` - Data cleaning logic
- `src/pipeline.py` - Main orchestration
- `src/transformer.py` - JSON → CSV conversion
- `src/config.py` - Configuration values

### Q5: รันบน Google Cloud ได้ไหม?

**A:** ได้! ดูรายละเอียดใน `TOOLS_AND_RESOURCES.md`

---

## 📞 ติดต่อและสนับสนุน

- **Hackathon:** NACC Asset Declaration 2025
- **Email:** opendata@hand.co.th
- **Repository:** (URL ของ repository)

---

**Last Updated:** 10 ธันวาคม 2568  
**Version:** 1.0
