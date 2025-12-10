"""
Docling-based PDF Extractor with Gemini Integration
Replaces EasyOCR chunked approach with layout-aware document parsing
"""
import google.generativeai as genai
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

from .config import (
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
            "max_output_tokens": 8192,
        }

        # Initialize Docling with Thai OCR support
        print("   🔧 Initializing Docling with Thai OCR support...")

        # Configure pipeline for Thai PDFs
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True

        # Use EasyOCR backend for Thai language support
        pipeline_options.ocr_options = EasyOcrOptions(
            lang=["th", "en"],  # Thai + English
            use_gpu=False
        )

        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            pipeline_options=pipeline_options
        )

        print("   ✅ Docling initialized with Thai OCR")

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
        for page_num, page in enumerate(doc.pages):
            if hasattr(page, 'tables'):
                for table in page.tables:
                    try:
                        tables.append({
                            "page": page_num + 1,
                            "rows": len(table.data) if hasattr(table, 'data') else 0,
                            "cols": len(table.data[0]) if hasattr(table, 'data') and table.data else 0,
                            "content": table.export_to_markdown() if hasattr(table, 'export_to_markdown') else str(table)
                        })
                    except Exception as e:
                        print(f"      ⚠️ Table extraction error on page {page_num + 1}: {e}")
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
                table_context += f"\n**Table {i+1} (Page {table['page']}, {table['rows']}×{table['cols']}):**\n{table['content']}\n"

        # Truncate markdown if too long (keep within Gemini limits)
        max_content_length = 25000  # Leave room for prompt structure
        if len(markdown_content) > max_content_length:
            print(f"   ⚠️ Content truncated from {len(markdown_content)} to {max_content_length} chars")
            markdown_content = markdown_content[:max_content_length] + "\n\n... [document continues]"

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
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to fix common issues
            fixed_text = text
            fixed_text = re.sub(r',(\s*[}\]])', r'\1', fixed_text)  # Remove trailing commas

            try:
                return json.loads(fixed_text)
            except:
                print(f"   ⚠️ JSON parse failed, returning empty structure")
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
