# 🛠️ Tools and Resources

> **Complete list of technologies, libraries, and resources used in NACC Asset Declaration Digitization System**

---

## 🐍 Programming Languages

### Python 3.11
- **Version:** 3.11.x
- **Purpose:** Core application language
- **Why:** Modern features, excellent AI/ML library support, type hints
- **License:** PSF (Python Software Foundation License)
- **Link:** https://www.python.org/

### JavaScript (ES6+)
- **Purpose:** Frontend web interface
- **Why:** Native browser support, PDF.js integration, async/await
- **License:** No license (standard web technology)

### HTML5 / CSS3
- **Purpose:** Web UI structure and styling
- **Why:** Standard web technologies, Tailwind CSS integration
- **License:** No license (standard web specifications)

---

## 🤖 AI & Machine Learning

### Google Gemini 2.5 Flash API
- **Version:** gemini-2.5-flash (latest)
- **Purpose:** Vision AI for PDF content extraction and validation
- **Why:** Best Thai language OCR, large context window (2M tokens), cost-effective
- **Pricing:** $0.075 per million input tokens, $0.30 per million output tokens
- **License:** Google Cloud Terms of Service
- **Link:** https://ai.google.dev/gemini-api/docs/models/gemini-v2
- **API Key:** Free tier available (15 RPM), paid tier (1000 RPM)

**Key Features Used:**
- Vision API (multimodal input: images + text)
- JSON mode output
- Prompt caching (cost optimization)
- Safety settings customization
- max_output_tokens: 65536 (for large documents)

---

## 📄 PDF Processing Libraries

### Docling
- **Version:** Latest (via pip)
- **Purpose:** Layout-aware PDF extraction with OCR
- **Why:** Preserves table structure, supports EasyOCR, open-source
- **License:** MIT License
- **Link:** https://github.com/DS4SD/docling
- **Developed by:** IBM Research

**Features Used:**
- Document conversion (PDF → Markdown)
- EasyOCR integration for Thai
- Table structure preservation
- Layout analysis

### EasyOCR
- **Version:** Latest (via pip)
- **Purpose:** Thai language OCR engine
- **Why:** Best open-source Thai OCR, pre-trained models, GPU support
- **License:** Apache 2.0
- **Link:** https://github.com/JaidedAI/EasyOCR
- **Developed by:** Jaided AI

**Languages Supported:**
- Thai (th)
- English (en)

### pdf2image
- **Version:** Latest (via pip)
- **Purpose:** Convert PDF pages to images for Vision API
- **Why:** Fast, reliable, Pillow integration
- **License:** MIT License
- **Link:** https://github.com/Belval/pdf2image
- **Dependency:** poppler-utils (system package)

### Pillow (PIL)
- **Version:** Latest (via pip)
- **Purpose:** Image processing and manipulation
- **Why:** Standard Python imaging library, wide format support
- **License:** HPND License
- **Link:** https://python-pillow.org/

---

## 🌐 Web Framework & API

### FastAPI
- **Version:** Latest (via pip)
- **Purpose:** REST API server
- **Why:** Fast, async, auto-generated docs (Swagger/ReDoc), type hints
- **License:** MIT License
- **Link:** https://fastapi.tiangolo.com/

**Features Used:**
- POST /extract_region (PDF upload)
- GET /health (health check)
- GET /download/{filename} (CSV download)
- CORS middleware
- File upload handling
- JSON responses

### Uvicorn
- **Version:** Latest (via pip)
- **Purpose:** ASGI server for FastAPI
- **Why:** High performance, async support, production-ready
- **License:** BSD License
- **Link:** https://www.uvicorn.org/

**Configuration:**
- Host: 0.0.0.0 (bind to all interfaces)
- Port: 5001 (API server)
- Workers: 1 (single process for development)

### Python HTTP Server
- **Built-in:** http.server module
- **Purpose:** Serve frontend static files
- **Why:** No dependencies, simple, sufficient for demo
- **Port:** 8000 (frontend server)

---

## 🎨 Frontend Libraries

### PDF.js
- **Version:** Latest (CDN)
- **Purpose:** Client-side PDF rendering
- **Why:** Official Mozilla library, canvas rendering, page navigation
- **License:** Apache 2.0
- **Link:** https://mozilla.github.io/pdf.js/
- **CDN:** https://cdnjs.cloudflare.com/ajax/libs/pdf.js/

### Tailwind CSS
- **Version:** 3.x (CDN)
- **Purpose:** Utility-first CSS framework
- **Why:** Rapid UI development, modern design, responsive
- **License:** MIT License
- **Link:** https://tailwindcss.com/
- **CDN:** https://cdn.tailwindcss.com

---

## 📊 Data Processing

### Pandas
- **Version:** Latest (via pip)
- **Purpose:** CSV file generation and manipulation
- **Why:** Industry standard, efficient, wide format support
- **License:** BSD 3-Clause
- **Link:** https://pandas.pydata.org/

**Features Used:**
- DataFrame creation
- CSV export
- Data validation
- Column mapping

### Python JSON
- **Built-in:** json module
- **Purpose:** Parse API responses, configuration files
- **Why:** Native Python support, fast, reliable

### Python Re (Regular Expressions)
- **Built-in:** re module
- **Purpose:** Pattern matching, date parsing, validation
- **Why:** Powerful text processing, standard library

---

## 🐳 Deployment & Infrastructure

### Docker
- **Version:** 20.x or later
- **Purpose:** Application containerization
- **Why:** Consistent environment, easy deployment, isolation
- **License:** Apache 2.0
- **Link:** https://www.docker.com/
- **Base Image:** python:3.11-slim

**Dockerfile Features:**
- Multi-stage optimization (future)
- System dependencies (libgl1, poppler-utils, curl)
- Health check support
- Environment variables

### Docker Compose
- **Version:** 2.x
- **Purpose:** Multi-service orchestration
- **Why:** Single-command startup, volume management, networking
- **License:** Apache 2.0
- **Link:** https://docs.docker.com/compose/

**Services:**
- app (frontend + backend combined)

**Features Used:**
- Port mapping (8000:8000, 5001:5001)
- Volume mounts (code, data, output)
- Environment variables
- Health checks
- Resource limits (4GB RAM, 2 CPUs)
- Auto-restart policy

---

## 📦 Python Dependencies

### Core Libraries (requirements.txt)

```txt
# AI & API
google-generativeai>=0.3.0    # Gemini API client
python-dotenv>=1.0.0          # Environment variable loading

# PDF Processing
docling>=1.0.0                # IBM PDF extraction
pdf2image>=1.16.0             # PDF to image conversion
Pillow>=10.0.0                # Image processing
easyocr>=1.7.0                # Thai OCR

# Web Framework
fastapi>=0.104.0              # REST API
uvicorn>=0.24.0               # ASGI server
python-multipart>=0.0.6       # File upload support

# Data Processing
pandas>=2.0.0                 # CSV generation
```

### System Dependencies (apt-get)

**For Vision API & OCR:**
- `libgl1` - OpenGL library (OpenCV dependency)
- `libglib2.0-0` - GLib library
- `libsm6` - X11 Session Management
- `libxext6` - X11 extensions
- `libxrender1` - X11 rendering
- `libgomp1` - GNU OpenMP library

**For PDF Processing:**
- `poppler-utils` - PDF rendering utilities (pdf2image dependency)

**For Health Checks:**
- `curl` - HTTP client for health endpoints

---

## 🔧 Development Tools

### Python Virtual Environment
- **Built-in:** venv module
- **Purpose:** Dependency isolation
- **Why:** Avoid conflicts, reproducible builds
- **Directory:** `.venv/` (project-local)

### Git
- **Purpose:** Version control
- **Why:** Standard VCS, GitHub integration
- **License:** GPL v2
- **Link:** https://git-scm.com/

### VS Code (Recommended)
- **Purpose:** Code editor
- **Extensions Used:**
  - Python
  - Docker
  - Markdown Preview
- **Link:** https://code.visualstudio.com/

---

## 📚 Documentation Tools

### Markdown
- **Purpose:** All documentation files
- **Why:** Readable, GitHub-friendly, universal
- **Format:** GitHub Flavored Markdown (GFM)

### Swagger/OpenAPI
- **Auto-generated:** FastAPI built-in
- **Purpose:** API documentation
- **Access:** http://localhost:5001/docs

### ReDoc
- **Auto-generated:** FastAPI built-in
- **Purpose:** Alternative API docs
- **Access:** http://localhost:5001/redoc

---

## 🎥 Media & Assets

### Screen Recording
- **OBS Studio** (recommended)
  - Free, open-source, cross-platform
  - Link: https://obsproject.com/
  - License: GPL v2

- **QuickTime** (macOS)
  - Built-in, simple
  - Screen recording feature

### Video Editing
- **iMovie** (macOS) - Free, simple
- **DaVinci Resolve** - Professional, free version available
- **Adobe Premiere Pro** (if available) - Professional

### Graphics Design
- **Figma** - UI mockups, diagrams (free tier)
  - Link: https://www.figma.com/

- **Canva** - Quick graphics, slides (free tier)
  - Link: https://www.canva.com/

- **draw.io** - Architecture diagrams (free)
  - Link: https://app.diagrams.net/

---

## 📖 Reference Materials

### Thai Language Processing
- **Thai Buddhist Calendar**
  - พ.ศ. (Buddhist Era) = ค.ศ. (Common Era) + 543
  - Example: พ.ศ. 2568 = ค.ศ. 2025

- **Thai Month Names**
  - Full list in `src/backend/config.py` (THAI_MONTHS)

- **Thai Digits**
  - ๐๑๒๓๔๕๖๗๘๙ → 0123456789

### NACC Database Schema
- **Source:** Hackathon documentation
- **Tables:** 13 CSV files (submitter, spouse, assets, statements, etc.)
- **Enum Types:** asset_type, statement_type, position_type, relationship

### DQS (Digitization Quality Score)
- **Weights:**
  - Submitter/Spouse: 25%
  - Statement Details: 30%
  - Assets: 30%
  - Relatives: 15%

---

## 💰 Cost & Pricing

### Gemini API Pricing
- **Free Tier:**
  - 15 RPM (Requests Per Minute)
  - 1M TPM (Tokens Per Minute)
  - 1500 RPD (Requests Per Day)

- **Paid Tier:**
  - Input: $0.075 per 1M tokens
  - Output: $0.30 per 1M tokens
  - Cached input: $0.01875 per 1M tokens (75% discount)

**Our Usage (per PDF):**
- Input: ~150K tokens (24 pages × 300 DPI)
- Output: ~10K tokens (JSON data)
- Cost: ~$0.15 Vision + $2 validation = $2.15 total

### Alternative Services (for comparison)
- **Google Cloud Document AI:** $1.50 per 1K pages
- **AWS Textract:** $1.50 per 1K pages
- **Azure Form Recognizer:** $1.50 per 1K pages

**Our system is competitive:** $2/PDF = $86 per 1K pages (custom Thai solution)

---

## 🔒 Security & Privacy

### API Key Management
- **Storage:** .env file (excluded from Git)
- **Environment Variables:** os.getenv()
- **Example File:** .env.example (no real keys)

### Data Privacy
- **No Data Storage:** PDFs processed in-memory, deleted after
- **No Logging:** Sensitive data not logged
- **Local Processing:** All processing local (except Gemini API)

---

## 📊 Monitoring & Logging

### Health Checks
- **Endpoint:** GET /health
- **Response:** {"status": "healthy", "pipeline": "ready"}
- **Docker:** Automated health checks every 30s

### Logging
- **Python Logging:** Built-in logging module
- **Levels:** INFO, WARNING, ERROR
- **Output:** Console (stdout)

### Performance Metrics
- **Processing Time:** Tracked per PDF
- **Confidence Scores:** Per field, per section
- **Error Rate:** Failed extractions logged

---

## 🌍 External Resources

### APIs & Services
1. **Gemini API**
   - Endpoint: https://generativelanguage.googleapis.com
   - Docs: https://ai.google.dev/

2. **Google AI Studio**
   - API Key management: https://aistudio.google.com/apikey
   - Prompt testing

### Community Resources
1. **Stack Overflow**
   - Python: https://stackoverflow.com/questions/tagged/python
   - FastAPI: https://stackoverflow.com/questions/tagged/fastapi
   - Docker: https://stackoverflow.com/questions/tagged/docker

2. **GitHub Repositories**
   - Docling: https://github.com/DS4SD/docling
   - EasyOCR: https://github.com/JaidedAI/EasyOCR
   - FastAPI: https://github.com/tiangolo/fastapi

3. **Documentation Sites**
   - Python: https://docs.python.org/3/
   - FastAPI: https://fastapi.tiangolo.com/
   - Docker: https://docs.docker.com/

---

## 🎓 Learning Resources

### Tutorials Used
1. **FastAPI Tutorial:** https://fastapi.tiangolo.com/tutorial/
2. **Docker Tutorial:** https://docs.docker.com/get-started/
3. **Gemini API Quickstart:** https://ai.google.dev/gemini-api/docs/quickstart

### Documentation References
1. **Docling Documentation:** https://ds4sd.github.io/docling/
2. **EasyOCR Usage:** https://www.jaided.ai/easyocr/documentation/
3. **Pandas API:** https://pandas.pydata.org/docs/

---

## 🏆 Credits & Acknowledgments

### Open Source Projects
- **IBM Research** - Docling library
- **Jaided AI** - EasyOCR Thai support
- **Google** - Gemini 2.5 Flash API
- **FastAPI** - Sebastián Ramírez and contributors
- **Mozilla** - PDF.js library

### Communities
- **Python Community** - Extensive library ecosystem
- **Docker Community** - Containerization best practices
- **Thai NLP Community** - Language-specific insights

---

## 📝 License Summary

All dependencies are compatible with commercial and competition use:

- **MIT License:** FastAPI, Docling, pdf2image, Pillow, Tailwind CSS
- **Apache 2.0:** EasyOCR, Docker, PDF.js
- **BSD License:** Pandas, Uvicorn
- **PSF License:** Python
- **Proprietary:** Google Gemini API (free tier, terms of service)

**Our Project:** MIT License (after hackathon)

---

## 🔄 Version Information

**Last Updated:** December 2025

**Tool Versions:**
- Python: 3.11.x
- Gemini API: 2.5 Flash
- FastAPI: 0.104+
- Docker: 20.x+
- Docling: Latest
- EasyOCR: 1.7+

---

## 📞 Support & Contact

**For Technical Issues:**
- Gemini API: https://ai.google.dev/support
- Docker: https://forums.docker.com/
- Python: https://www.python.org/community/

**For Hackathon Questions:**
- Email: opendata@hand.co.th
- Kaggle: Competition discussion board

---

**Document Version:** 1.0
**Created:** December 2025
**Purpose:** NACC Hackathon 2025 Submission
