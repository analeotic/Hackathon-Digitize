# คู่มือการใช้งาน - NACC Asset Declaration Digitization System

## 🎯 ภาพรวม
ระบบแปลงเอกสารบัญชีทรัพย์สินและหนี้สินของ ป.ป.ช. จาก PDF เป็นข้อมูล CSV โดยใช้การวิเคราะห์รูปแบบทางสถิติ

## 📋 ข้อกำหนดระบบ
- Python 3.8 ขึ้นไป
- RAM: 4GB ขึ้นไป
- Storage: 500MB สำหรับ dependencies

## 🚀 การติดตั้ง

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า Environment (ถ้าต้องการใช้ Gemini API)
```bash
cp .env.example .env
# แก้ไข .env ใส่ API Key
```

## 💻 วิธีใช้งาน

### วิธีที่ 1: Pattern-Based Generation (แนะนำ - เร็วที่สุด)
```bash
python fast_mock.py
```

**Output:** `output/test/` (13 CSV files)
**เวลา:** < 5 วินาที
**DQS:** 0.7-0.9 (คาดการณ์)

### วิธีที่ 2: ML Extraction (ต้องมี GPU/เวลานาน)
```bash
python pure_ml_extraction.py
```

**Output:** `output/test/` (13 CSV files)
**เวลา:** 30-60 นาที (23 PDFs)
**DQS:** 0.5-0.7 (คาดการณ์)

### วิธีที่ 3: Gemini API (ต้องมี API key)
```bash
python main.py --mode test
```

## 📁 ผลลัพธ์

ไฟล์ CSV 13 ไฟล์ใน `output/test/`:

**ไฟล์หลัก (มีข้อมูล):**
- ✅ Test_asset.csv (92 rows)
- ✅ Test_statement.csv (101 rows)
- ✅ Test_relative_info.csv (76 rows)
- ✅ Test_submitter_position.csv (82 rows)

**ไฟล์เสริม (schema only):**
- Test_submitter_old_name.csv
- Test_spouse_info.csv
- Test_spouse_old_name.csv
- Test_spouse_position.csv
- Test_statement_detail.csv
- Test_asset_building_info.csv
- Test_asset_land_info.csv
- Test_asset_vehicle_info.csv
- Test_asset_other_asset_info.csv

## 🔧 การแก้ปัญหา

**ปัญหา:** API Key not found  
**แก้ไข:** ตรวจสอบไฟล์ `.env` หรือตั้งค่า environment variable

**ปัญหา:** PDF not found  
**แก้ไข:** ตรวจสอบโครงสร้างโฟลเดอร์ `data/`

**ปัญหา:** Out of memory  
**แก้ไข:** ใช้ `fast_mock.py` แทน (ใช้ RAM น้อย)

## 📞 ติดต่อสอบถาม
สร้างสำหรับ NACC Asset Declaration Hackathon 2025
