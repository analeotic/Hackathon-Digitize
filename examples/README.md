# Examples

ตัวอย่างการใช้งานระบบ

## ตัวอย่างที่ 1: ประมวลผล PDF เดี่ยว

```python
from src.pipeline import Pipeline

# สร้าง pipeline
pipeline = Pipeline(api_key="your_api_key")

# ประมวลผล PDF เดี่ยว
pipeline.process_single_pdf(
    pdf_path="path/to/document.pdf",
    submitter_id=1,
    nacc_id=1
)
```

## ตัวอย่างที่ 2: ประมวลผลหลาย PDFs

```python
from src.pipeline import Pipeline

# สร้าง pipeline
pipeline = Pipeline(api_key="your_api_key")

# ประมวลผล Training data
pipeline.process_dataset(mode="train", limit=5)

# ประมวลผล Test data
pipeline.process_dataset(mode="test")
```

## ตัวอย่างที่ 3: ใช้ผ่าน CLI

```bash
# ประมวลผล Training data (5 เอกสารแรก)
python main.py --mode train --limit 5

# ประมวลผล Test data ทั้งหมด
python main.py --mode test

# ประมวลผล PDF เดี่ยว
python main.py --pdf "path/to/document.pdf"
```
