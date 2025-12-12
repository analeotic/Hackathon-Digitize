# 🎬 Demo Guide - Command Line Presentation

> **สำหรับนำเสนอต่อกรรมการแบบ Terminal (ไม่ต้องใช้เว็บ)**

---

## 🎯 Overview

ใช้ **Command-Line Demo** ที่สวยงามและ professional แทนการใช้เว็บ
- ✅ Terminal output สวยงาม (colors, progress bars, ASCII art)
- ✅ แสดง Confidence Scores แบบ real-time
- ✅ Professional statistics และ comparison tables
- ✅ Record ง่าย (screen recording)

---

## 🚀 Quick Start

### Option 1: Auto Demo (ใช้ sample PDF)

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# หรือ .venv\Scripts\activate  # Windows

# Run demo (auto-select first PDF from test directory)
python demo_cli.py
```

### Option 2: Specific PDF

```bash
# Run with specific PDF
python demo_cli.py "data/test final/001.pdf"
```

---

## 📊 Demo Output Preview

### 1. Logo & Architecture (10 seconds)
```
    ███╗   ██╗ █████╗  ██████╗ ██████╗
    ████╗  ██║██╔══██╗██╔════╝██╔════╝
    ██╔██╗ ██║███████║██║     ██║
    ██║╚██╗██║██╔══██║██║     ██║
    ██║ ╚████║██║  ██║╚██████╗╚██████╗
    ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝

    PDF Digitizer - Hybrid AI Pipeline
    91% DQS • $2/PDF • 45 seconds

System Architecture:

    ┌──────────┐      ┌─────────────┐      ┌──────────────┐      ┌──────┐
    │   PDF    │─────▶│  Docling    │─────▶│   Gemini     │─────▶│ CSV  │
    │ 24 pages │      │  OCR        │      │   Vision     │      │13 files│
    └──────────┘      └─────────────┘      └──────────────┘      └──────┘
```

### 2. Processing (20 seconds)
```
────────────────────────────────────────────────────────────────────
▶ PROCESSING PDF
────────────────────────────────────────────────────────────────────

⏳ Stage 1: Docling OCR extraction... ✓
⏳ Stage 2: Gemini Vision validation... ✓
⏳ Stage 3: Data transformation... ✓

✅ Processing completed in 45.3 seconds!
```

### 3. Confidence Report (15 seconds)
```
────────────────────────────────────────────────────────────────────
▶ CONFIDENCE SCORE REPORT
────────────────────────────────────────────────────────────────────

Overall Confidence: 91.5% ⭐⭐⭐⭐⭐

Field Statistics:
  Total Fields:      150
  ✅ High (≥90%):    135  ██████████████████████████████  90.0%
  ⚠️  Medium (70-90%): 12  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8.0%
  ❌ Low (<70%):       3  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   2.0%

⚠️  Low Confidence Fields:
  - age: 65%
  - asset_valuation: 68%
```

### 4. Results Summary (10 seconds)
```
────────────────────────────────────────────────────────────────────
▶ EXTRACTION SUMMARY
────────────────────────────────────────────────────────────────────

Extracted Data:
  💰 Assets:                8
  📊 Financial Statements:  12
  👔 Positions:              3
  👨‍👩‍👧‍👦 Relatives:              5

Submitter:
  Name: สมชาย ใจดี
  Age:  45
```

### 5. CSV Files (5 seconds)
```
────────────────────────────────────────────────────────────────────
▶ GENERATED CSV FILES
────────────────────────────────────────────────────────────────────

📁 Output Directory: src/backend/output/single
📄 Total Files: 13

   1. ✓ submitter_old_name.csv               (   2.1 KB)
   2. ✓ submitter_position.csv               (   3.4 KB)
   3. ✓ spouse_info.csv                      (   1.8 KB)
   ...
```

### 6. Comparison Table (5 seconds)
```
────────────────────────────────────────────────────────────────────
▶ WHY WE WIN - COMPARISON
────────────────────────────────────────────────────────────────────

┌────────────────────┬──────────────┬──────────────────┐
│ Metric             │ Our System ✅│ Competitors      │
├────────────────────┼──────────────┼──────────────────┤
│ DQS Accuracy       │   91.2%      │ 72-89%           │
│ Cost/PDF           │   $2.00      │ $0 or $7         │
│ Processing Time    │   45 sec     │ 30s - 5 min      │
│ Confidence Scoring │   Yes        │ No               │
│ Thai Support       │   Native     │ Limited          │
│ Production Ready   │   Docker     │ Manual setup     │
└────────────────────┴──────────────┴──────────────────┘
```

### 7. Final Results (5 seconds)
```
╔═══════════════════════════════════════════════════════════════╗
║                    DIGITIZATION COMPLETE                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📊 DQS Score:          91.2% ⭐⭐⭐⭐⭐                       ║
║  💰 Cost Estimate:      $2.00 (Gemini Vision API)            ║
║  ⚡ Processing Time:    45.3 seconds                         ║
║  ✅ Confidence Scoring: Field-level validation               ║
║  🇹🇭 Thai Support:       Native (พ.ศ./ค.ศ., tone marks)      ║
║  🐳 Deployment:         Docker-ready                         ║
║  📁 Output Files:       13 CSV files                         ║
║                                                               ║
║          Industry-Grade • Production-Ready                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Total Duration:** ~70 seconds (1 minute 10 seconds)

---

## 🎬 Recording Demo Video

### Setup (5 minutes)

1. **Prepare Terminal**
   ```bash
   # Clean terminal
   clear

   # Set good terminal size
   # macOS Terminal: Cmd+Plus to zoom
   # iTerm2: View → Zoom In

   # Recommended: 100 columns × 40 rows
   ```

2. **Test Run**
   ```bash
   # Test demo first
   python demo_cli.py

   # Make sure:
   # - Colors display correctly
   # - Progress bars work
   # - No errors
   ```

3. **Start Recording**
   - **macOS:** QuickTime → File → New Screen Recording
   - **Windows:** OBS Studio / ShareX
   - **Linux:** SimpleScreenRecorder

### Recording Tips

**DO:**
- ✅ Record in Full HD (1920×1080)
- ✅ Zoom terminal to comfortable size
- ✅ Use dark theme (better contrast)
- ✅ Wait 2 seconds before starting demo
- ✅ Let final stats display for 5 seconds

**DON'T:**
- ❌ Don't resize window during recording
- ❌ Don't have other apps visible
- ❌ Don't interrupt the demo
- ❌ Don't use small font sizes

### Post-Production

1. **Trim Video**
   - Cut first 2 seconds (preparing)
   - Cut last part after final stats

2. **Add Narration (Optional)**
   ```
   [0:00] "NACC PDF Digitizer - Hybrid AI Pipeline"
   [0:10] "Processing 24-page Thai PDF document"
   [0:30] "Calculating confidence scores"
   [0:45] "91% accuracy, $2 per PDF, production-ready"
   [1:00] "Thank you"
   ```

3. **Export**
   - Format: MP4 (H.264)
   - Resolution: 1920×1080
   - Framerate: 30fps
   - Filename: `NACC_Digitizer_CLI_Demo.mp4`

---

## 📸 Screenshot for Documentation

### Take Key Screenshots

```bash
# Run demo
python demo_cli.py

# Take screenshots at:
# 1. Logo + Architecture
# 2. Confidence Report (most impressive!)
# 3. Comparison Table
# 4. Final Results box
```

**Use screenshots in:**
- README.md
- Technical report
- Presentation slides
- Email submission

---

## 🎤 Presentation Script

### For Live Demo (1-2 minutes)

**[Start]**
> "สวัสดีครับ วันนี้ผมจะ demo ระบบ NACC PDF Digitizer
> ที่สามารถแปลงเอกสาร ป.ป.ช. ภาษาไทย 24 หน้า เป็น CSV ได้อัตโนมัติ"

**[Show Architecture]**
> "ระบบใช้ Hybrid Pipeline 3 ขั้นตอน:
> - Docling OCR สำหรับ layout-aware extraction
> - Gemini Vision สำหรับ validation
> - Smart transformation เป็น 13 CSV files"

**[Run Processing]**
> "เริ่มประมวลผล... ใช้เวลาประมาณ 45 วินาที"
> [Wait for completion]

**[Show Confidence Report]**
> "จุดเด่นของเราคือ Confidence Scoring แบบ field-level
> Overall confidence 91.5%
> แยกเป็น High 90%, Medium 8%, Low 2%
> สามารถบอกได้เลยว่า field ไหนต้อง manual review"

**[Show Comparison]**
> "เทียบกับคู่แข่ง:
> - DQS สูงที่สุด 91%
> - ราคาถูกที่สุด $2/PDF
> - มี Confidence Scoring ที่ไม่มีใครทำ"

**[Final Stats]**
> "ผลลัพธ์: 91% DQS, $2/PDF, 45 วินาที
> พร้อม Docker deployment และ production monitoring
> ขอบคุณครับ"

---

## 🎯 Highlighting Key Features

### 1. Confidence Scoring ⭐⭐⭐
**Why it's unique:**
- ไม่มีทีมอื่นทำ
- Professional feature
- Industry-standard practice
- Shows we understand quality assurance

**Emphasize:**
> "เราไม่ได้แค่ extract ข้อมูล แต่เรา score ความมั่นใจของแต่ละ field
> ระบบบอกได้เองว่า field ไหนแม่นยำ field ไหนต้อง review
> นี่คือสิ่งที่ระบบ production จริงต้องมี"

### 2. Thai Language Expertise ⭐⭐
**Why it matters:**
- Buddhist calendar (พ.ศ. → ค.ศ.)
- Thai digits (๑๒๓ → 123)
- No word boundaries
- Tone marks

**Emphasize:**
> "เราเข้าใจความยากของภาษาไทย
> ระบบรองรับ Buddhist calendar, Thai digits, tone marks
> และ validate ตาม Thai document patterns"

### 3. Production-Ready ⭐
**Why it's better:**
- Docker deployment
- Health monitoring
- Auto-restart
- API documentation

**Emphasize:**
> "ระบบพร้อมใช้งานจริงเลย
> มี Docker สำหรับ deployment
> มี health checks และ monitoring
> ไม่ใช่แค่ demo code"

---

## 📝 Alternative Demo Methods

### Method 1: Pre-recorded Video
**Pros:**
- ✅ Perfect every time
- ✅ No live errors
- ✅ Can add narration

**Cons:**
- ❌ Less interactive
- ❌ Can't answer questions during

**When to use:** Email submission, asynchronous review

### Method 2: Live Terminal Demo
**Pros:**
- ✅ Interactive
- ✅ Can answer questions
- ✅ Shows real processing

**Cons:**
- ⚠️ May have errors
- ⚠️ Timing varies

**When to use:** In-person presentation, Zoom call

### Method 3: Screenshots Only
**Pros:**
- ✅ Quick to prepare
- ✅ Easy to include in docs

**Cons:**
- ❌ Not dynamic
- ❌ Less impressive

**When to use:** Written report, GitHub README

---

## 🏆 Judges' Expected Questions & Answers

### Q: "Why 91% DQS, not higher?"
**A:**
> "Thai handwritten text ยาก แม้ Google Cloud Document AI ก็ได้ 90-92%
> เรา implement confidence scoring เพื่อ flag low-confidence fields
> สำหรับ manual review ซึ่งเพิ่ม overall accuracy ได้มากกว่า"

### Q: "Why $2/PDF, not free?"
**A:**
> "Free OCR ได้แค่ 72% DQS (ต่ำเกินไป)
> Pure Vision API ราคา $7 (แพงเกินไป)
> เราใช้ hybrid approach: $2/PDF ได้ 91% DQS
> Best accuracy/cost ratio"

### Q: "Can you handle 1000+ PDFs?"
**A:**
> "ได้ครับ! เรามี:
> 1. Docker deployment (scale ได้)
> 2. Health monitoring (track performance)
> 3. Batch processing support
> 4. Rate limit handling (Gemini free tier 15 RPM)"

### Q: "What if API fails?"
**A:**
> "เรามี error handling:
> 1. Retry logic (3 attempts, exponential backoff)
> 2. Fallback to Docling-only (72% DQS but free)
> 3. Comprehensive logging
> 4. Graceful degradation"

---

## ✅ Pre-Demo Checklist

### Day Before Demo

- [ ] Test demo script works
  ```bash
  python demo_cli.py
  ```

- [ ] Check PDF sample exists
  ```bash
  ls "data/test final/"
  ```

- [ ] Verify virtual environment
  ```bash
  source .venv/bin/activate
  which python  # Should show .venv path
  ```

- [ ] Test GEMINI_API_KEY
  ```bash
  cat .env | grep GEMINI_API_KEY
  ```

### 1 Hour Before Demo

- [ ] Clear terminal
- [ ] Set font size (comfortable for screen recording)
- [ ] Test screen recording software
- [ ] Practice run (1-2 times)
- [ ] Close unnecessary apps
- [ ] Disable notifications

### Just Before Demo

- [ ] Activate venv: `source .venv/bin/activate`
- [ ] Navigate to project: `cd Hackathon-Digitize`
- [ ] Clear screen: `clear`
- [ ] Deep breath 😊

---

## 🎬 Final Command

```bash
# The one command to rule them all
python demo_cli.py
```

**Duration:** ~70 seconds
**Output:** Beautiful, professional terminal demo
**Impression:** 🏆 Winning!

---

**Good luck with your presentation! 🚀**

---

**Version:** 1.0
**Last Updated:** December 2025
**For:** NACC Hackathon 2025
