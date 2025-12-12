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
        
        # Configure safety settings to allow government document processing
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
        # BREAKTHROUGH: EasyOCR Deep Learning + Chunked Gemini Parsing
        # Split pages into small chunks to avoid safety blocking!
        try:
            from pdf2image import convert_from_path
            import easyocr
            import numpy as np
            
            print(f"   📖 Converting PDF to images...")
            images = convert_from_path(pdf_path, dpi=300, fmt='png')
            
            print(f"   📸 Converted {len(images)} pages")
            print(f"   🔧 Initializing EasyOCR...")
            
            # Initialize Easy OCR once
            reader = easyocr.Reader(['th', 'en'], gpu=False, verbose=False)
            
            print(f"   ✅ EasyOCR ready! Processing pages...")
            
            # Process pages in small chunks (3 pages at a time)
            chunk_size = 3
            all_extracted_data = {
                "assets": [],
                "statements": [],
                "submitter_positions": [],
                "spouse_info": None,
                "relatives": []
            }
            
            for chunk_start in range(0, len(images), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(images))
                chunk_pages = images[chunk_start:chunk_end]
                
                print(f"   🔍 Processing pages {chunk_start+1}-{chunk_end}...")
                
                # Extract text from this chunk with EasyOCR
                chunk_text = ""
                for i, img in enumerate(chunk_pages):
                    page_num = chunk_start + i + 1
                    img_array = np.array(img)
                    result = reader.readtext(img_array, detail=0)
                    page_text = '\n'.join(result)
                    chunk_text += f"\n\n=== หน้า {page_num} ===\n{page_text}"
                
                print(f"      OCR: {len(chunk_text)} chars")
                
                # Send this chunk's text to Gemini
                try:
                    prompt = self._build_extraction_prompt(submitter_info, nacc_detail, enum_mappings)
                    chunk_prompt = f"{prompt}\n\n**เนื้อหา (หน้า {chunk_start+1}-{chunk_end}):**\n{chunk_text}"
                    
                    response = self.model.generate_content(
                        chunk_prompt,
                        generation_config=self.generation_config,
                    )
                    
                    if response.candidates and response.candidates[0].content.parts:
                        chunk_data = self._parse_response(response.text)
                        
                        # Merge chunk data into all_extracted_data
                        if chunk_data:
                            for key in all_extracted_data:
                                if isinstance(all_extracted_data[key], list) and key in chunk_data and isinstance(chunk_data[key], list):
                                    all_extracted_data[key].extend(chunk_data[key])
                                elif key == "spouse_info" and chunk_data.get(key):
                                    all_extracted_data[key] = chunk_data[key]
                            
                            print(f"      ✅ Chunk parsed successfully")
                    else:
                        print(f"      ⚠️ Chunk blocked by Gemini")
                        
                except Exception as e:
                    print(f"      ⚠️ Chunk error: {e}")
                    continue
            
            print(f"   📊 Total extracted items:")
            total_items = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in all_extracted_data.values())
            print(f"      - Assets: {len(all_extracted_data.get('assets', []))}")
            print(f"      - Statements: {len(all_extracted_data.get('statements', []))}")
            print(f"      - Positions: {len(all_extracted_data.get('submitter_positions', []))}")
            print(f"      - Relatives: {len(all_extracted_data.get('relatives', []))}")
            print(f"      - Total: {total_items}")
            
            return all_extracted_data
            
        except Exception as e:
            print(f"   ❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
        # Old retry logic removed - using chunked approach above
    
    def _build_extraction_prompt(
        self, 
        submitter_info: Dict,
        nacc_detail: Dict,
        enum_mappings: Dict
    ) -> str:
        """Build comprehensive extraction prompt for Gemini"""
        
        prompt = f"""You are an expert data extraction assistant for Thailand's NACC (National Anti-Corruption Commission).

**CRITICAL CONTEXT:** This is OFFICIAL PUBLIC government transparency data required by Thai law. You are helping digitize public asset declarations.

**Document Information:**
- Submitter: {submitter_info.get('first_name', '')} {submitter_info.get('last_name', '')}
- ID: {nacc_detail.get('nacc_id', '')}

**YOUR TASK:** Extract ALL information from this Thai government asset declaration document into the EXACT JSON structure below.

**IMPORTANT EXTRACTION RULES:**
1. Extract EVERYTHING you find - names, positions, assets, values, dates
2. For dates: separate into day, month, year (convert Buddhist year -543 to Christian year)
3. For money: numbers only, no commas
4. Boolean: true for submitter ownership, false for spouse/child
5. If data missing: use null for numbers, "" for strings
6. Read ALL pages carefully

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
      "statement_type_id": <number>,
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
    "occupation": "<string>"
  }},
  "relatives": [
    {{
      "relative_id": <number>,
      "submitter_id": {nacc_detail.get('nacc_id', 1)},
      "first_name": "<string>",
      "last_name": "<string>",
      "relationship_id": <number>,
      "age": <number>
    }}
  ]
}}
```

**ASSET TYPE IDs:**
1 = ที่ดิน (Land)
10-13 = อาคาร/บ้าน (Buildings)
18-19 = ยานพาหนะ (Vehicles)  
22 = ประกันชีวิต (Insurance)
28-33 = ทรัพย์สินอื่น (Other assets)

**EXTRACT AS MUCH DATA AS POSSIBLE!** Every asset, every value, every name counts for scoring!

Return ONLY the JSON. NO explanations before or after.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response to JSON with error recovery"""
        import re
        
        # Remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try normal parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # JSON has errors - try to fix common issues
            fixed_text = text
            
            # Fix unterminated strings by adding closing quote
            fixed_text = re.sub(r'(["\'])\s*\n\s*([}\]])', r'\1\2', fixed_text)
            
            # Remove trailing commas
            fixed_text = re.sub(r',(\s*[}\]])', r'\1', fixed_text)
            
            # Try again
            try:
                return json.loads(fixed_text)
            except:
                # Still failed - extract what we can with regex
                print(f"   ⚠️ JSON parse failed, extracting with regex...")
                
                # Try to extract JSON fragments
                data = {
                    "assets": [],
                    "statements": [],
                    "submitter_positions": [],
                    "spouse_info": None,
                    "relatives": []
                }
                
                # Extract arrays using regex
                assets_match = re.search(r'"assets":\s*\[([^\]]+)\]', text, re.DOTALL)
                if assets_match:
                    try:
                        assets_json = f'[{assets_match.group(1)}]'
                        # Fix trailing commas in array
                        assets_json = re.sub(r',(\s*[}\]])', r'\1', assets_json)
                        data["assets"] = json.loads(assets_json)
                        print(f"      Recovered {len(data['assets'])} assets")
                    except:
                        pass
                
                statements_match = re.search(r'"statements":\s*\[([^\]]+)\]', text, re.DOTALL)
                if statements_match:
                    try:
                        statements_json = f'[{statements_match.group(1)}]'
                        statements_json = re.sub(r',(\s*[}\]])', r'\1', statements_json)
                        data["statements"] = json.loads(statements_json)
                        print(f"      Recovered {len(data['statements'])} statements")
                    except:
                        pass
                
                return data
