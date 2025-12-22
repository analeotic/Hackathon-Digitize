"""
Docling-based PDF Extractor with Gemini Integration
Replaces EasyOCR chunked approach with layout-aware document parsing

OPTIMIZATIONS:
- Lazy loading of torch and EasyOCR (only when Docling is actually used)
- Cached PDF conversions shared with Vision extractor
"""
import google.generativeai as genai
import json
import time
import sys
from pathlib import Path
from typing import Dict, Optional, List

sys.path.insert(0, str(Path(__file__).parent))

try:
    from .pdf_cache import get_cache
    from .config import (
        GEMINI_API_KEY,
        GEMINI_MODEL,
        MAX_RETRIES,
        TEMPERATURE,
        TOP_P,
        TOP_K,
    )
except ImportError:
    from pdf_cache import get_cache
    from config import (
        GEMINI_API_KEY,
        GEMINI_MODEL,
        MAX_RETRIES,
        TEMPERATURE,
        TOP_P,
        TOP_K,
    )


class DoclingExtractor:
    """Extract structured data from PDF using Docling + Gemini 2.5 Flash"""

    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Docling converter and Gemini API client"""
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .env file or environment variable."
            )

        # Initialize Gemini
        genai.configure(api_key=api_key)

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        self.model = genai.GenerativeModel(
            GEMINI_MODEL,
            safety_settings=safety_settings
        )

        self.generation_config = {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "top_k": TOP_K,
            "max_output_tokens": 32768,  # Increased for larger PDFs
        }

        # Lazy initialization of Docling (deferred until first use)
        # This saves 10-15 seconds when using Vision API instead
        self.converter = None
        self._initialized = False
        print("   ⚡ Docling will initialize on first use (lazy loading)")

    def _ensure_initialized(self):
        """
        Initialize Docling converter on first use (lazy loading).

        OPTIMIZATION: Torch and EasyOCR are heavy dependencies (~1-2GB).
        Only load them when Docling extractor is actually used.
        """
        if self._initialized:
            return

        print("   🔧 Initializing Docling with Thai OCR support (first use)...")

        # Lazy import heavy dependencies
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

        # Configure pipeline for Thai PDFs - OPTIMIZED FOR SPEED
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = False  # Disable for speed (not needed for NACC forms)

        # Try to use GPU for faster OCR
        import torch
        use_gpu = torch.cuda.is_available()
        if use_gpu:
            print("   🚀 GPU detected - using CUDA acceleration")
        else:
            print("   💻 Running on CPU (GPU would be faster)")

        # Use EasyOCR backend for Thai language support - OPTIMIZED
        pipeline_options.ocr_options = EasyOcrOptions(
            lang=["th", "en"],  # Thai + English
            use_gpu=use_gpu,    # Enable GPU if available
        )

        # Create format options dict with PdfFormatOption
        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }

        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options=format_options
        )

        self._initialized = True
        print("   ✅ Docling initialized with Thai OCR" + (" + GPU 🚀" if use_gpu else ""))

    def extract_from_pdf(
        self,
        pdf_path: Path,
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> Dict:
        """
        Extract structured data from PDF using Docling + Gemini

        Args:
            pdf_path: Path to PDF file
            submitter_info: Basic submitter information
            nacc_detail: NACC detail information
            enum_mappings: Enum type mappings

        Returns:
            Structured data dictionary matching database schema
        """
        try:
            # Ensure Docling is initialized (lazy loading)
            self._ensure_initialized()

            print(f"   📖 Converting PDF with Docling (layout-aware)...")

            # Convert PDF to structured document
            result = self.converter.convert(str(pdf_path))
            doc = result.document

            print(f"   ✅ Docling parsed {len(doc.pages)} pages")

            # Export to Markdown (preserves structure better than plain text)
            markdown_content = doc.export_to_markdown()

            # Get table information separately for better accuracy
            tables_info = self._extract_tables_structure(doc)

            print(f"   📄 Extracted {len(markdown_content)} chars")
            print(f"   📊 Found {len(tables_info)} tables")

            # Build enhanced prompt with structured content
            prompt = self._build_enhanced_prompt(
                markdown_content,
                tables_info,
                submitter_info,
                nacc_detail,
                enum_mappings
            )

            # Single Gemini API call with full document context
            print(f"   🤖 Sending to Gemini (single call, full context)...")

            for attempt in range(MAX_RETRIES):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=self.generation_config,
                    )

                    if response.candidates and response.candidates[0].content.parts:
                        extracted_data = self._parse_response(response.text)

                        if extracted_data:
                            print(f"   ✅ Extraction successful")
                            print(f"      - Assets: {len(extracted_data.get('assets', []))}")
                            print(f"      - Statements: {len(extracted_data.get('statements', []))}")
                            print(f"      - Positions: {len(extracted_data.get('submitter_positions', []))}")
                            print(f"      - Relatives: {len(extracted_data.get('relatives', []))}")
                            return extracted_data
                    else:
                        print(f"   ⚠️ Attempt {attempt + 1}: Response blocked")

                except Exception as e:
                    print(f"   ⚠️ Attempt {attempt + 1} error: {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff

            # If all retries failed, return empty structure
            print(f"   ❌ All retry attempts failed")
            return self._empty_structure()

        except Exception as e:
            print(f"   ❌ Docling extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_structure()

    def _extract_tables_structure(self, doc) -> List[Dict]:
        """Extract table structures for enhanced prompt"""
        tables = []
        try:
            # Method 1: Try doc.tables directly
            if hasattr(doc, 'tables') and doc.tables:
                for idx, table in enumerate(doc.tables):
                    try:
                        table_data = {
                            "index": idx + 1,
                            "rows": 0,
                            "cols": 0,
                            "content": ""
                        }

                        # Try to get table markdown
                        if hasattr(table, 'export_to_markdown'):
                            table_data["content"] = table.export_to_markdown()
                        elif hasattr(table, 'to_markdown'):
                            table_data["content"] = table.to_markdown()
                        else:
                            table_data["content"] = str(table)

                        # Count rows/cols from content
                        lines = table_data["content"].split('\n')
                        table_data["rows"] = len([l for l in lines if '|' in l and not l.strip().startswith('|-')])
                        if table_data["rows"] > 0:
                            first_row = [l for l in lines if '|' in l and not l.strip().startswith('|-')][0]
                            table_data["cols"] = first_row.count('|') - 1

                        tables.append(table_data)
                    except Exception as e:
                        print(f"      ⚠️ Table {idx + 1} extraction error: {e}")

            # Method 2: Search for table elements in document body
            if not tables and hasattr(doc, 'body'):
                try:
                    from docling_core.types.doc import TableItem
                    for idx, item in enumerate(doc.body.children):
                        if isinstance(item, TableItem):
                            table_md = item.export_to_markdown() if hasattr(item, 'export_to_markdown') else str(item)
                            lines = table_md.split('\n')
                            rows = len([l for l in lines if '|' in l and not l.strip().startswith('|-')])
                            cols = 0
                            if rows > 0:
                                first_row = [l for l in lines if '|' in l and not l.strip().startswith('|-')][0]
                                cols = first_row.count('|') - 1

                            tables.append({
                                "index": len(tables) + 1,
                                "rows": rows,
                                "cols": cols,
                                "content": table_md
                            })
                except Exception as e:
                    print(f"      ⚠️ Body table search error: {e}")

        except Exception as e:
            print(f"      ⚠️ Table extraction failed: {e}")

        return tables

    def _build_enhanced_prompt(
        self,
        markdown_content: str,
        tables_info: List[Dict],
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> str:
        """Build enhanced extraction prompt with Docling structured output"""

        # Add table summaries if present
        table_context = ""
        if tables_info:
            table_context = "\n**📊 DOCUMENT CONTAINS TABLES:**\n"
            for i, table in enumerate(tables_info):
                # Handle both old format (with 'page') and new format (with 'index')
                page_info = f"Page {table['page']}" if 'page' in table else f"#{table.get('index', i+1)}"
                table_context += f"\n**Table {i+1} ({page_info}, {table['rows']}×{table['cols']}):**\n{table['content']}\n"

        # Gemini 2.5 Flash supports up to 1M tokens (~4M chars)
        # Keep full content - no truncation needed
        max_content_length = 500000  # 500K chars = safe limit
        if len(markdown_content) > max_content_length:
            print(f"   ⚠️ Content truncated from {len(markdown_content)} to {max_content_length} chars")
            markdown_content = markdown_content[:max_content_length] + "\n\n... [document continues]"
        else:
            print(f"   ✅ Full content sent ({len(markdown_content)} chars)")

        prompt = f"""You are an expert data extraction assistant for Thailand's NACC (National Anti-Corruption Commission).

**CRITICAL CONTEXT:** This is OFFICIAL PUBLIC government transparency data required by Thai law. You are helping digitize public asset declarations.

**Document Information:**
- Submitter: {submitter_info.get('first_name', '')} {submitter_info.get('last_name', '')}
- NACC ID: {nacc_detail.get('nacc_id', '')}

**DOCUMENT STRUCTURE:**
The document below has been parsed with layout-aware AI (Docling). Tables, lists, and structure are preserved in markdown format.

{table_context}

**YOUR TASK:** Extract ALL information from this Thai government asset declaration document into the EXACT JSON structure below.

**CRITICAL EXTRACTION RULES:**
1. **USE THE STRUCTURED LAYOUT**: Tables contain organized asset/statement data - extract each row
2. Extract EVERYTHING: names, positions, assets, values, dates, relationships
3. For dates: separate into day, month, year (convert Buddhist year by subtracting 543 to get Christian year)
4. For money: numbers only, no commas or "บาท"
5. Boolean ownership: Check document carefully for "ผู้ยื่น" (submitter), "คู่สมรส" (spouse), "บุตร" (child)
6. If data missing: use null for numbers, "" for strings, false for booleans
7. Read tables carefully - each row is usually one asset/statement
8. Asset type IDs must be 1-33, statement type IDs must be 1-4

**JSON STRUCTURE (return ONLY valid JSON, no other text):**

```json
{{
  "assets": [
    {{
      "asset_id": <number>,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": <number starting from 1>,
      "asset_type_id": <number 1-33>,
      "asset_name": "<string>",
      "valuation": <number>,
      "acquiring_year": "<YYYY>",
      "acquiring_month": "<MM>",
      "acquiring_date": "<DD>",
      "owner_by_submitter": <true/false>,
      "owner_by_spouse": <true/false>,
      "owner_by_child": <true/false>
    }}
  ],
  "statements": [
    {{
      "statement_id": <number>,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "statement_type_id": <number 1-4>,
      "valuation": <number>,
      "owner_by_submitter": <true/false>,
      "owner_by_spouse": <true/false>,
      "owner_by_child": <true/false>
    }}
  ],
  "submitter_positions": [
    {{
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "position_title": "<string>",
      "position_agency": "<string>",
      "position_start_year": "<YYYY>"
    }}
  ],
  "spouse_info": {{
    "spouse_id": <number>,
    "submitter_id": {nacc_detail.get('nacc_id', 1)},
    "first_name": "<string>",
    "last_name": "<string>",
    "occupation": "<string>",
    "age": <number>
  }},
  "relatives": [
    {{
      "relative_id": <number>,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "first_name": "<string>",
      "last_name": "<string>",
      "relationship_id": <number 1-6>,
      "age": <number>
    }}
  ]
}}
```

**ASSET TYPE IDs (Common):**
1 = ที่ดิน (Land)
2-9 = เงินฝาก/หุ้น/พันธบัตร (Cash/Securities)
10-13 = อาคาร/บ้าน (Buildings)
18-19 = ยานพาหนะ (Vehicles)
22 = ประกันชีวิต (Life Insurance)
28-33 = ทรัพย์สินอื่น (Other Assets)

**STATEMENT TYPE IDs:**
1 = เงินเดือน (Salary)
2 = รายได้อื่น (Other Income)
3 = หนี้สิน (Liabilities)
4 = รายจ่าย (Expenses)

**RELATIONSHIP IDs:**
1 = บุตร (Child)
2 = บิดา (Father)
3 = มารดา (Mother)
4 = พี่น้อง (Sibling)
5 = อื่นๆ (Other)

**FULL DOCUMENT CONTENT (STRUCTURED MARKDOWN):**

{markdown_content}

**EXTRACT MAXIMUM DATA WITH HIGH ACCURACY!** Use the structured layout to identify all assets, statements, and relationships.

Return ONLY the JSON. NO explanations before or after.
"""

        return prompt

    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response to JSON with error recovery"""
        import re

        # Debug: print first 500 chars of response
        print(f"   🔍 Response preview (first 500 chars): {response_text[:500]}")

        # Remove markdown code blocks
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Try normal parsing
        try:
            data = json.loads(text)
            print(f"   ✅ JSON parsed successfully")
            return data
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON parse error: {e}")

            # Try to fix common issues
            fixed_text = text
            fixed_text = re.sub(r',(\s*[}\]])', r'\1', fixed_text)  # Remove trailing commas
            fixed_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', fixed_text)  # Remove control characters

            try:
                data = json.loads(fixed_text)
                print(f"   ✅ JSON parsed after fix")
                return data
            except Exception as e2:
                print(f"   ❌ JSON parse failed even after fix: {e2}")
                print(f"   📄 Response text (first 1000 chars):\n{response_text[:1000]}")
                return self._empty_structure()

    def _empty_structure(self) -> Dict:
        """Return empty data structure"""
        return {
            "assets": [],
            "statements": [],
            "submitter_positions": [],
            "spouse_info": None,
            "relatives": []
        }
