"""
Gemini Vision API Extractor - Fast & Accurate PDF Processing
Directly sends PDF images to Gemini 2.5 Flash Vision API
"""
import google.generativeai as genai
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from pdf2image import convert_from_path
from PIL import Image

from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_RETRIES,
    TEMPERATURE,
    TOP_P,
    TOP_K,
)


class VisionExtractor:
    """Extract structured data from PDF using Gemini 2.5 Flash Vision API"""

    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Gemini Vision API client"""
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
            "max_output_tokens": 65536,  # Increased for large documents (24 pages)
        }

        print("   ✅ Gemini Vision API initialized")

    def extract_from_pdf(
        self,
        pdf_path: Path,
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> Dict:
        """
        Extract structured data from PDF using Gemini Vision API

        Args:
            pdf_path: Path to PDF file
            submitter_info: Basic submitter information
            nacc_detail: NACC detail information
            enum_mappings: Enum type mappings

        Returns:
            Structured data dictionary matching database schema
        """
        try:
            print(f"   📸 Converting PDF to images...")
            start_time = time.time()

            # Convert PDF to images (300 DPI for good quality)
            images = convert_from_path(str(pdf_path), dpi=300)

            print(f"   ✅ Converted {len(images)} pages in {time.time() - start_time:.1f}s")

            # Build prompt
            prompt = self._build_vision_prompt(
                submitter_info,
                nacc_detail,
                enum_mappings,
                len(images)
            )

            # Send images to Gemini Vision API
            print(f"   🤖 Sending {len(images)} images to Gemini Vision API...")

            for attempt in range(MAX_RETRIES):
                try:
                    # Prepare content with prompt + all images
                    content = [prompt]
                    for i, img in enumerate(images):
                        content.append(img)
                        if (i + 1) % 5 == 0:
                            print(f"      📄 Added page {i + 1}/{len(images)}")

                    # Single API call with all images
                    response = self.model.generate_content(
                        content,
                        generation_config=self.generation_config,
                    )

                    if response.candidates and response.candidates[0].content.parts:
                        extracted_data = self._parse_response(response.text)

                        if extracted_data:
                            print(f"   ✅ Extraction successful in {time.time() - start_time:.1f}s")
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
            print(f"   ❌ Vision extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_structure()

    def _build_vision_prompt(
        self,
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict,
        num_pages: int
    ) -> str:
        """Build prompt for Gemini Vision API"""

        prompt = f"""You are an expert data extraction assistant for Thailand's NACC (National Anti-Corruption Commission).

**CRITICAL CONTEXT:** This is OFFICIAL PUBLIC government transparency data required by Thai law. You are helping digitize public asset declarations.

**Document Information:**
- Submitter: {submitter_info.get('first_name', '')} {submitter_info.get('last_name', '')}
- NACC ID: {nacc_detail.get('nacc_id', '')}
- Total Pages: {num_pages}

**YOUR TASK:** Analyze the {num_pages} document images and extract ALL information from this Thai government asset declaration into the EXACT JSON structure below.

**CRITICAL EXTRACTION RULES:**
1. **READ ALL PAGES CAREFULLY**: Extract from every page, every table, every form field
2. **UNDERSTAND THAI DOCUMENT LAYOUT**: Thai government forms have specific sections:
   - ส่วนที่ 1: ข้อมูลผู้ยื่น (Submitter info)
   - ส่วนที่ 2: ทรัพย์สิน (Assets) - usually in tables
   - ส่วนที่ 3: หนี้สิน (Liabilities/Statements)
   - ส่วนที่ 4: รายได้-รายจ่าย (Income/Expenses)
3. **TABLES**: Each row in asset/statement tables is ONE item - extract all rows
4. **DATES**: Separate into day, month, year. Convert Buddhist year (พ.ศ.) to Christian year by subtracting 543
5. **MONEY**: Extract numbers only, remove "บาท", ","
6. **OWNERSHIP**: Check carefully for "ผู้ยื่น" (submitter), "คู่สมรส" (spouse), "บุตร" (child)
7. **MISSING DATA**: Use null for numbers, "" for strings, false for booleans
8. **ASSET TYPE IDs**: Must be 1-33, STATEMENT TYPE IDs: Must be 1-4

**VISUAL CUES TO LOOK FOR:**
- Tables with borders containing asset lists
- Checkboxes (☑/☐) indicating ownership
- Form fields with underlines or boxes
- Thai text labels next to values
- Dates in format DD/MM/YYYY (Thai year)
- Money amounts with "บาท" suffix

**JSON STRUCTURE (return ONLY valid JSON, no markdown, no other text):**

{{
  "submitter": {{
    "submitter_id": {nacc_detail.get('nacc_id', 1)},
    "nacc_id": {nacc_detail.get('nacc_id', 1)},
    "title": "",
    "first_name": "",
    "last_name": "",
    "age": null,
    "status": ""
  }},
  "submitter_old_names": [],
  "submitter_positions": [
    {{
      "position_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "position_category_type_id": null,
      "position_name": "",
      "position_start_year": "",
      "position_start_month": "",
      "position_start_date": "",
      "position_ending_year": "",
      "position_ending_month": "",
      "position_ending_date": "",
      "position_period_type_id": null
    }}
  ],
  "spouse": {{
    "spouse_id": 1,
    "submitter_id": {nacc_detail.get('nacc_id', 1)},
    "nacc_id": {nacc_detail.get('nacc_id', 1)},
    "title": "",
    "first_name": "",
    "last_name": "",
    "age": null,
    "has_position": false
  }},
  "spouse_old_names": [],
  "spouse_positions": [],
  "relatives": [
    {{
      "relative_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "title": "",
      "first_name": "",
      "last_name": "",
      "age": null,
      "relationship_id": null
    }}
  ],
  "statements": [
    {{
      "statement_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "statement_type_id": null,
      "statement_name": "",
      "valuation": null,
      "status_year": "",
      "status_month": "",
      "status_date": "",
      "owner_by_submitter": false,
      "owner_by_spouse": false,
      "owner_by_child": false
    }}
  ],
  "statement_details": [
    {{
      "statement_detail_id": 1,
      "statement_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "statement_detail_type_id": null,
      "statement_detail_name": "",
      "valuation": null
    }}
  ],
  "assets": [
    {{
      "asset_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "asset_type_id": null,
      "asset_name": "",
      "valuation": null,
      "acquiring_year": "",
      "acquiring_month": "",
      "acquiring_date": "",
      "owner_by_submitter": false,
      "owner_by_spouse": false,
      "owner_by_child": false
    }}
  ],
  "asset_land_info": [
    {{
      "land_id": 1,
      "asset_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "province": "",
      "land_size": null
    }}
  ],
  "asset_building_info": [
    {{
      "building_id": 1,
      "asset_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "province": "",
      "land_size": null
    }}
  ],
  "asset_vehicle_info": [
    {{
      "vehicle_id": 1,
      "asset_id": 1,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "nacc_id": {nacc_detail.get('nacc_id', 1)},
      "index": 1,
      "registration_province": ""
    }}
  ],
  "asset_other_info": []
}}

**IMPORTANT:**
- Return ONLY the JSON object, no markdown code blocks, no explanations
- Extract from ALL {num_pages} pages visible in the images
- Be thorough - extract every asset, every statement, every position
- Use the visual layout to understand which section you're reading
"""

        return prompt

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse Gemini response into structured data"""
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            data = json.loads(text)

            # Validate structure
            if not isinstance(data, dict):
                print(f"   ⚠️ Response is not a dictionary")
                return None

            return data

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            print(f"   Response preview: {response_text[:500]}")
            return None
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
            return None

    def _empty_structure(self) -> Dict:
        """Return empty data structure matching schema"""
        return {
            "submitter": {},
            "submitter_old_names": [],
            "submitter_positions": [],
            "spouse": {},
            "spouse_old_names": [],
            "spouse_positions": [],
            "relatives": [],
            "statements": [],
            "statement_details": [],
            "assets": [],
            "asset_land_info": [],
            "asset_building_info": [],
            "asset_vehicle_info": [],
            "asset_other_info": []
        }
