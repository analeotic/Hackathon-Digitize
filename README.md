# NACC Asset Declaration Digitization System

ระบบแปลงเอกสารบัญชีทรัพย์สินและหนี้สินของ ป.ป.ช. จาก PDF เป็นข้อมูลดิจิทัล (CSV) โดยใช้ AI

## 🎯 สร้างสำหรับ
Kaggle Competition: **Hack the Asset Declaration**  
วันที่: 15 พ.ย. - 6 ธ.ค. 2568

## ✨ ความสามารถ
- ✅ อ่าน PDF ภาษาไทยด้วย AI (Google Gemini 2.0 Flash)
- ✅ แปลงเป็น 13 ไฟล์ CSV ตามมาตรฐาน Database
- ✅ รองรับข้อมูล Training และ Test
- ✅ จัดการวันที่ ตัวเลข และข้อความภาษาไทย

## 🚀 เริ่มต้นใช้งานเร็ว

### 1. ติดตั้ง
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key
```bash
cp .env.example .env
# แก้ไข .env ใส่ Gemini API Key
```

รับ API Key ฟรีที่: https://aistudio.google.com/apikey

### 3. รันโปรแกรม

**ทดสอบกับ Training data (5 เอกสารแรก):**
```bash
python main.py --mode train --limit 5
```

**ประมวลผล Test data ทั้งหมด (สำหรับส่งแข่งขัน):**
```bash
python main.py --mode test
```

## 📁 ผลลัพธ์

ไฟล์ CSV 13 ไฟล์ใน `output/test/`:
1. `Test_submitter_old_name.csv`
2. `Test_submitter_position.csv`
3. `Test_spouse_info.csv`
4. `Test_spouse_old_name.csv`
5. `Test_spouse_position.csv`
6. `Test_relative_info.csv`
7. `Test_statement.csv`
8. `Test_statement_detail.csv`
9. `Test_asset.csv`
10. `Test_asset_building_info.csv`
11. `Test_asset_land_info.csv`
12. `Test_asset_vehicle_info.csv`
13. `Test_asset_other_asset_info.csv`

## 📚 เอกสารเพิ่มเติม

- **[INSTRUCTION.md](INSTRUCTION.md)** - คู่มือการใช้งานฉบับเต็ม (ภาษาไทย)
- **[TOOLS_AND_RESOURCES.md](TOOLS_AND_RESOURCES.md)** - เครื่องมือและทรัพยากรที่ใช้

## 🧠 เทคโนโลยีที่ใช้

- **AI Model:** Google Gemini 2.0 Flash
- **Language:** Python 3.8+
- **Libraries:** pandas, google-generativeai, tqdm
- **Free API:** ใช้ Gemini Free Tier (15 RPM)

## 📊 โครงสร้างโปรเจค

```
Hackathon-Digitize-/
├── README.md                 # คู่มือหลัก
├── main.py                   # Entry point (รันโปรแกรมที่นี่)
├── requirements.txt          # Python dependencies
├── .env.example              # ตัวอย่างการตั้งค่า API key
├── .env                      # API key (ไม่ขึ้น git)
│
├── docs/                     # 📚 เอกสาร
│   ├── INSTRUCTION.md       # คู่มือการใช้งาน (ไทย)
│   └── TOOLS_AND_RESOURCES.md  # เอกสารเครื่องมือ
│
├── src/                      # 💻 Source code หลัก
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── extractor.py         # Gemini PDF extraction
│   ├── transformer.py       # JSON to CSV
│   └── pipeline.py          # Main orchestration
│
├── examples/                 # 📝 ตัวอย่างการใช้งาน
│   └── README.md
│
├── tests/                    # 🧪 Unit tests (อนาคต)
│   └── README.md
│
├── output/                   # 📁 ผลลัพธ์ CSV
│   ├── train/               # Training output
│   └── test/                # Test output (สำหรับส่งแข่งขัน)
│
└── data/                     # 📦 Dataset จาก Kaggle
    ├── training/
    ├── test final/
    └── enum_type/
```

## ⚡ ตัวอย่างการใช้งาน

```bash
# ประมวลผล PDF เดี่ยว
python main.py --pdf "path/to/document.pdf"

# ประมวลผล Training data ทั้งหมด
python main.py --mode train

# ประมวลผล Test data (สำหรับส่งแข่งขัน)
python main.py --mode test

# ระบุ API key โดยตรง
python main.py --mode test --api-key YOUR_API_KEY
```

## 🏆 สำหรับการส่งแข่งขัน

### ส่งใน Kaggle:
- อัปโหลด `output/test/summary.csv` (ถ้ามี)
- หรือไฟล์ CSV ตามที่กำหนด

### ส่งใน Email (opendata@hand.co.th):
1. ✅ CSV ผลลัพธ์ทั้ง 13 ไฟล์
2. ✅ Code/Model (โฟลเดอร์นี้)
3. ✅ เอกสารวิธีการใช้งาน (INSTRUCTION.md)
4. ✅ เอกสารเครื่องมือและทรัพยากร (TOOLS_AND_RESOURCES.md)
5. ⭐ ข้อเสนอแนะ (Optional)

## 🐛 แก้ไขปัญหา

**ปัญหา:** API Key not found  
**แก้ไข:** ตรวจสอบไฟล์ `.env` หรือตั้งค่า environment variable

**ปัญหา:** PDF not found  
**แก้ไข:** ตรวจสอบโครงสร้างโฟลเดอร์ `hack-the-assetdeclaration-data/`

**ปัญหา:** Rate limit error  
**แก้ไข:** ใช้ `--limit` เพื่อประมวลผลทีละน้อย

ดูรายละเอียดเพิ่มเติมใน [INSTRUCTION.md](INSTRUCTION.md)

## 📝 License

MIT License (หรือตามที่ Hackathon กำหนด)  
นวัตกรรมนี้จะเป็น Open Source หลังจบกิจกรรม

## 👥 ผู้พัฒนา

สร้างสำหรับ NACC Asset Declaration Hackathon 2025

---

**เวอร์ชัน:** 1.0  
**วันที่:** 6 ธันวาคม 2568  
**AI Model:** Google Gemini 2.0 Flash