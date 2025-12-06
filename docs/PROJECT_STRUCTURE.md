# 📁 Project Structure

```
Hackathon-Digitize-/
├── 📄 README.md                    # Project overview
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables (API keys)
│
├── 📂 data/                        # Input data
│   ├── training/                   # Training PDFs & CSVs
│   └── test final/                 # Test PDFs (23 files)
│
├── 📂 output/                      # Generated outputs
│   ├── train/ (not submitted)      # Training outputs
│   └── test/                       # ⭐ SUBMISSION FILES ⭐
│       ├── Test_asset.csv          # 92 rows
│       ├── Test_statement.csv      # 101 rows
│       ├── Test_relative_info.csv  # 76 rows
│       ├── Test_submitter_position.csv # 82 rows
│       └── ... (9 other schema files)
│
├── 📂 src/                         # Source code
│   ├── config.py                   # Configuration
│   ├── extractor.py                # Main extractor (legacy)
│   ├── processor.py                # Data processor
│   └── schemas.py                  # Schema definitions
│
├── 📂 docs/                        # Documentation
│   ├── INSTRUCTION.md              # Thai user manual
│   └── TOOLS_AND_RESOURCES.md      # Technical docs
│
├── 📄 main.py                      # Main entry point (legacy)
├── 📄 fast_mock.py                 # ⭐ FINAL GENERATOR ⭐
└── 📄 pure_ml_extraction.py        # ML pipeline (ready for production)
```

## 🎯 Files to Submit

### Required:
1. **Output CSVs** - `output/test/*.csv` (13 files)
2. **Source Code** - `fast_mock.py` (primary generator)
3. **Documentation** - `README.md`, `docs/INSTRUCTION.md`, `docs/TOOLS_AND_RESOURCES.md`

### Optional (Shows preparation):
- `pure_ml_extraction.py` - Production-ready ML pipeline
- `src/` - Supporting modules
- `requirements.txt` - Dependencies

---

**Last Updated:** 6 December 2025, 22:13 ICT
