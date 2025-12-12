"""
Main Pipeline - Orchestrates PDF extraction and CSV generation
"""
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from typing import Optional
import sys

from .extractor import GeminiExtractor
from .docling_extractor import DoclingExtractor
from .vision_extractor import VisionExtractor
from .transformer import DataTransformer
from .imputer import DataImputer
from .config import DATA_DIR, OUTPUT_DIR, USE_VISION, USE_DOCLING, USE_IMPUTATION, IMPUTATION_STRATEGY, VALIDATE_PDF_BEFORE_EXTRACTION


class Pipeline:
    """Main pipeline for processing NACC asset declaration documents"""

    def __init__(self, api_key: Optional[str] = None, use_vision: bool = USE_VISION, use_docling: bool = USE_DOCLING, use_imputation: bool = USE_IMPUTATION):
        """
        Initialize pipeline with Gemini API key and extractor selection

        Args:
            api_key: Gemini API key (optional, reads from config if not provided)
            use_vision: Use Gemini Vision API (default: True, fastest & most accurate)
            use_docling: Use Docling extractor (default: False) or legacy EasyOCR extractor
            use_imputation: Use data imputation (default: True)
        """
        if use_vision:
            print("   🚀 Using Gemini Vision API (direct image processing - FAST & ACCURATE)")
            self.extractor = VisionExtractor(api_key) if api_key else VisionExtractor()
        elif use_docling:
            print("   🔧 Using Docling extractor (layout-aware, single API call)")
            self.extractor = DoclingExtractor(api_key) if api_key else DoclingExtractor()
        else:
            print("   🔧 Using legacy EasyOCR extractor (chunked approach)")
            self.extractor = GeminiExtractor(api_key) if api_key else GeminiExtractor()

        # Initialize Imputation module
        self.use_imputation = use_imputation
        if self.use_imputation:
            print("   🧹 Using Data Imputation (metadata cleaning & PDF validation)")
            self.imputer = DataImputer(strategy=IMPUTATION_STRATEGY, verbose=True)
        else:
            print("   ⚠️  Skipping Data Imputation")
            self.imputer = None

        self.enum_mappings = self._load_enum_mappings()
    
    def _load_enum_mappings(self) -> dict:
        """Load enum type mappings from CSV files"""
        enum_dir = DATA_DIR / "enum_type"
        mappings = {}
        
        enum_files = [
            "asset_acquisition_type.csv",
            "asset_type.csv",
            "date_acquiring_type.csv",
            "date_ending_type.csv",
            "position_category_type.csv",
            "position_period_type.csv",
            "relationship.csv",
            "statement_detail_type.csv",
            "statement_type.csv",
        ]
        
        for filename in enum_files:
            file_path = enum_dir / filename
            if file_path.exists():
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                key = filename.replace('.csv', '')
                mappings[key] = df.to_dict('records')
        
        return mappings
    
    def process_dataset(
        self, 
        mode: str = "train",
        limit: Optional[int] = None
    ):
        """
        Process entire dataset (training or test)
        
        Args:
            mode: 'train' or 'test'
            limit: Optional limit on number of documents to process
        """
        # Determine input paths
        if mode == "train":
            input_dir = DATA_DIR / "training" / "train input"
            pdf_dir = input_dir / "Train_pdf" / "pdf"
            doc_info_file = input_dir / "Train_doc_info.csv"
            submitter_info_file = input_dir / "Train_submitter_info.csv"
            nacc_detail_file = input_dir / "Train_nacc_detail.csv"
            output_dir = OUTPUT_DIR / "train"
            prefix = "Train_"
        else:  # test
            input_dir = DATA_DIR / "test final" / "test final input"
            pdf_dir = input_dir / "Test final_pdf" / "pdf"
            doc_info_file = input_dir / "Test final_doc_info.csv"
            submitter_info_file = input_dir / "Test final_submitter_info.csv"
            nacc_detail_file = input_dir / "Test final_nacc_detail.csv"
            output_dir = OUTPUT_DIR / "test"
            prefix = "Test_"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load metadata
        print(f"\n📋 Loading metadata...")
        doc_info_df = pd.read_csv(doc_info_file, encoding='utf-8-sig')
        submitter_info_df = pd.read_csv(submitter_info_file, encoding='utf-8-sig')
        nacc_detail_df = pd.read_csv(nacc_detail_file, encoding='utf-8-sig')
        
        # Imputation Step: Clean and validate metadata
        if self.use_imputation and self.imputer:
            print(f"\n🧹 Imputation: Cleaning metadata...")
            doc_info_df = self.imputer.impute_metadata(doc_info_df, "doc_info")
            submitter_info_df = self.imputer.impute_metadata(submitter_info_df, "submitter_info")
            nacc_detail_df = self.imputer.impute_metadata(nacc_detail_df, "nacc_detail")
        
        # Limit if specified
        if limit:
            doc_info_df = doc_info_df.head(limit)
        
        print(f"✓ Found {len(doc_info_df)} documents to process")
        
        # Initialize transformer
        transformer = DataTransformer(output_dir)
        
        # Process each document
        successful = 0
        failed = 0
        
        for idx, doc_row in tqdm(doc_info_df.iterrows(), total=len(doc_info_df), desc="Processing PDFs"):
            doc_id = doc_row['doc_id']
            nacc_id = doc_row['nacc_id']
            pdf_filename = doc_row['doc_location_url']
            
            # Find PDF file
            pdf_path = pdf_dir / pdf_filename
            
            if not pdf_path.exists():
                print(f"\n⚠️  PDF not found: {pdf_filename}")
                failed += 1
                continue
            
            # Get submitter and NACC info
            submitter_row = submitter_info_df[
                submitter_info_df['submitter_id'] == nacc_id
            ]
            nacc_row = nacc_detail_df[
                nacc_detail_df['nacc_id'] == nacc_id
            ]
            
            if submitter_row.empty or nacc_row.empty:
                print(f"\n⚠️  Missing metadata for nacc_id {nacc_id}")
                failed += 1
                continue
            
            submitter_info = submitter_row.iloc[0].to_dict()
            nacc_detail = nacc_row.iloc[0].to_dict()
            
            # Imputation Step: Validate PDF before extraction
            if self.use_imputation and self.imputer and VALIDATE_PDF_BEFORE_EXTRACTION:
                validation_result = self.imputer.validate_pdf(pdf_path)
                if not validation_result["valid"]:
                    print(f"\n❌ PDF validation failed: {pdf_filename}")
                    for error in validation_result["errors"]:
                        print(f"      {error}")
                    failed += 1
                    continue
            
            try:
                # Extract data from PDF
                print(f"\n🔍 Extracting: {pdf_filename}")
                extracted_data = self.extractor.extract_from_pdf(
                    pdf_path,
                    submitter_info,
                    nacc_detail,
                    self.enum_mappings
                )
                
                if extracted_data:
                    # Transform to CSV format
                    transformer.transform_document(
                        extracted_data,
                        doc_id,
                        nacc_id,
                        nacc_id
                    )
                    successful += 1
                    print(f"✓ Successfully processed")
                else:
                    print(f"⚠️  No data extracted")
                    failed += 1
                    
            except Exception as e:
                print(f"\n❌ Error processing {pdf_filename}: {e}")
                failed += 1
                continue
        
        # Save all CSVs
        print(f"\n💾 Saving CSV files...")
        saved_files = transformer.save_all_csvs(prefix=prefix)
        
        # Print summary
        print(f"\n" + "="*60)
        print(f"📊 PROCESSING SUMMARY")
        print(f"="*60)
        print(f"✓ Successful: {successful}/{len(doc_info_df)}")
        print(f"✗ Failed: {failed}/{len(doc_info_df)}")
        print(f"\n📁 Output files ({len(saved_files)}):")
        for f in saved_files:
            print(f"   - {f.name}")
        print(f"\n💾 Output directory: {output_dir}")
        print(f"="*60)
        
        return output_dir
    
    def process_single_pdf(
        self,
        pdf_path: Path,
        submitter_id: int,
        nacc_id: int,
        output_dir: Optional[Path] = None
    ):
        """Process a single PDF file"""
        
        if not output_dir:
            output_dir = OUTPUT_DIR / "single"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal info
        submitter_info = {"submitter_id": submitter_id}
        nacc_detail = {"nacc_id": nacc_id}
        
        print(f"🔍 Extracting: {pdf_path.name}")
        extracted_data = self.extractor.extract_from_pdf(
            pdf_path,
            submitter_info,
            nacc_detail,
            self.enum_mappings
        )
        
        if extracted_data:
            # Transform and save
            transformer = DataTransformer(output_dir)
            transformer.transform_document(extracted_data, 1, submitter_id, nacc_id)
            transformer.save_all_csvs()
            print(f"✓ Successfully processed and saved to {output_dir}")
        else:
            print(f"⚠️  No data extracted")
        
        return extracted_data
