"""
PDF Extractor using Google Gemini 2.0 Flash
Extracts structured data from Thai asset declaration PDFs
"""
import google.generativeai as genai
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_RETRIES,
    TEMPERATURE,
    TOP_P,
    TOP_K,
)


class GeminiExtractor:
    """Extract structured data from PDF using Gemini 2.0 Flash"""
    
    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Gemini API client"""
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .env file or environment variable."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Configure generation parameters
        self.generation_config = {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "top_k": TOP_K,
            "max_output_tokens": 8192,
        }
    
    def extract_from_pdf(
        self, 
        pdf_path: Path, 
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> Dict:
        """
        Extract structured data from a single PDF
        
        Args:
            pdf_path: Path to PDF file
            submitter_info: Basic submitter information from CSV
            nacc_detail: NACC detail information from CSV
            enum_mappings: Enum type mappings for validation
            
        Returns:
            Structured data dictionary matching database schema
        """
        prompt = self._build_extraction_prompt(submitter_info, nacc_detail, enum_mappings)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Upload PDF to Gemini
                pdf_file = genai.upload_file(str(pdf_path))
                
                # Wait for file processing
                while pdf_file.state.name == "PROCESSING":
                    time.sleep(1)
                    pdf_file = genai.get_file(pdf_file.name)
                
                if pdf_file.state.name == "FAILED":
                    raise ValueError(f"PDF processing failed: {pdf_file.state.name}")
                
                # Generate extraction
                response = self.model.generate_content(
                    [pdf_file, prompt],
                    generation_config=self.generation_config,
                )
                
                # Parse JSON response
                extracted_data = self._parse_response(response.text)
                
                # Cleanup uploaded file
                genai.delete_file(pdf_file.name)
                
                return extracted_data
                
            except Exception as e:
                print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return {}
    
    def _build_extraction_prompt(
        self, 
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> str:
        """Build detailed extraction prompt for Gemini"""
        
        prompt = f"""คุณเป็น AI ผู้เชี่ยวชาญในการแปลงเอกสารบัญชีทรัพย์สินและหนี้สินของ ป.ป.ช. (NACC) ให้อยู่ในรูปแบบดิจิทัล

**ข้อมูลพื้นฐานจาก CSV:**
- ชื่อผู้ยื่น: {submitter_info.get('title', '')} {submitter_info.get('first_name', '')} {submitter_info.get('last_name', '')}
- NACC ID: {nacc_detail.get('nacc_id', '')}
- ประเภทเอกสาร: {nacc_detail.get('statement_type', '')}

**งานของคุณ:**
อ่านเอกสาร PDF และแปลงข้อมูลทั้งหมดให้อยู่ในรูปแบบ JSON ที่มีโครงสร้างดังนี้:

```json
{{
  "submitter": {{
    "old_names": [
      {{
        "submitter_id": int,
        "old_first_name": "string",
        "old_last_name": "string",
        "change_date": "DD",
        "change_month": "MM",
        "change_year": "YYYY"
      }}
    ],
    "positions": [
      {{
        "submitter_id": int,
        "position_period_type_id": int,
        "position_category_type_id": int,
        "position_start_date": "DD",
        "position_start_month": "MM",
        "position_start_year": "YYYY",
        "position_end_date": "DD",
        "position_end_month": "MM",
        "position_end_year": "YYYY",
        "position_title": "string",
        "position_agency": "string"
      }}
    ]
  }},
  "spouse": {{
    "info": {{
      "spouse_id": int,
      "submitter_id": int,
      "title": "string",
      "first_name": "string",
      "last_name": "string",
      "title_en": "string",
      "first_name_en": "string",
      "last_name_en": "string",
      "id_card_number": "string",
      "age": int,
      "occupation": "string",
      "office_name": "string",
      "marriage_date": "DD",
      "marriage_month": "MM",
      "marriage_year": "YYYY"
    }},
    "old_names": [...],
    "positions": [...]
  }},
  "relatives": [
    {{
      "relative_id": int,
      "submitter_id": int,
      "relationship_id": int,
      "title": "string",
      "first_name": "string",
      "last_name": "string",
      "age": int,
      "occupation": "string",
      "office_name": "string"
    }}
  ],
  "statements": [
    {{
      "statement_id": int,
      "submitter_id": int,
      "nacc_id": int,
      "statement_type_id": int,
      "owner_by_submitter": boolean,
      "owner_by_spouse": boolean,
      "owner_by_child": boolean,
      "statement_number": int,
      "valuation": float
    }}
  ],
  "statement_details": [
    {{
      "statement_detail_id": int,
      "statement_id": int,
      "statement_detail_type_id": int,
      "statement_detail_name": "string",
      "valuation": float
    }}
  ],
  "assets": [
    {{
      "asset_id": int,
      "submitter_id": int,
      "nacc_id": int,
      "index": int,
      "asset_type_id": int,
      "asset_type_other": "string",
      "asset_name": "string",
      "date_acquiring_type_id": int,
      "acquiring_date": "DD",
      "acquiring_month": "MM",
      "acquiring_year": "YYYY",
      "date_ending_type_id": int,
      "ending_date": "DD",
      "ending_month": "MM",
      "ending_year": "YYYY",
      "asset_acquisition_type_id": int,
      "valuation": float,
      "owner_by_submitter": boolean,
      "owner_by_spouse": boolean,
      "owner_by_child": boolean,
      "latest_submitted_date": "YYYY-MM-DD"
    }}
  ],
  "asset_land_info": [
    {{
      "asset_land_id": int,
      "asset_id": int,
      "title_deed_number": "string",
      "land_parcel_number": "string",
      "survey_page_number": "string",
      "sub_district": "string",
      "district": "string",
      "province": "string",
      "right_area_rai": int,
      "right_area_ngan": int,
      "right_area_wa": float
    }}
  ],
  "asset_building_info": [
    {{
      "asset_building_id": int,
      "asset_id": int,
      "building_type": "string",
      "house_number": "string",
      "sub_district": "string",
      "district": "string",
      "province": "string"
    }}
  ],
  "asset_vehicle_info": [
    {{
      "asset_vehicle_id": int,
      "asset_id": int,
      "vehicle_brand": "string",
      "vehicle_model": "string",
      "vehicle_year": "YYYY",
      "vehicle_color": "string",
      "license_plate_number": "string",
      "license_plate_province": "string",
      "engine_number": "string",
      "chassis_number": "string"
    }}
  ],
  "asset_other_info": [
    {{
      "asset_other_id": int,
      "asset_id": int,
      "other_asset_description": "string"
    }}
  ]
}}
```

**สิ่งสำคัญ:**
1. แยกข้อมูลให้ละเอียดที่สุด อ่านทุกหน้าของเอกสาร
2. วันที่ให้แยกเป็น วัน เดือน ปี (ปี ค.ศ. ไม่ใช่ พ.ศ.)
3. ตัวเลขเงินให้เป็นตัวเลขล้วน ไม่มีเครื่องหมายจุลภาค
4. Boolean: TRUE สำหรับผู้ยื่น, FALSE สำหรับคู่สมรสหรือบุตร
5. ถ้าข้อมูลไม่มีให้ใส่ null หรือ "" หรือ 0 ตามประเภท
6. asset_type_id: 1=ที่ดิน, 10-13=อาคาร/บ้าน, 18-19=ยานพาหนะ, 22=ประกันชีวิต, 28-33=ทรัพย์สินอื่น
7. index คือลำดับของทรัพย์สินแต่ละประเภท (เริ่มจาก 1)

**กรุณาส่งค่ากลับเป็น JSON เท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติม**
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response to JSON"""
        # Remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response text: {text[:500]}...")
            return {}
