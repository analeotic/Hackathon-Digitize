#!/usr/bin/env python3
"""
NACC Asset Declaration Digitization System
Main entry point for processing PDFs and generating CSV files

Usage:
    python main.py --mode train --limit 5        # Process 5 training documents
    python main.py --mode test                   # Process all test documents
    python main.py --pdf path/to/file.pdf       # Process single PDF
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipeline import Pipeline
from backend.config import OUTPUT_DIR


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NACC Asset Declaration Digitization System"
    )
    
    parser.add_argument(
        "--mode",
        choices=["train", "test"],
        help="Process training or test dataset"
    )
    
    parser.add_argument(
        "--pdf",
        type=str,
        help="Path to single PDF file to process"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of documents to process (for testing)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="Gemini API key (or set GEMINI_API_KEY env variable)"
    )
    
    parser.add_argument(
        "--skip-imputation",
        action="store_true",
        help="Skip data imputation step (not recommended)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found!")
        print("\nPlease either:")
        print("  1. Set environment variable: export GEMINI_API_KEY='your-key'")
        print("  2. Create .env file with: GEMINI_API_KEY=your-key")
        print("  3. Use --api-key flag: python main.py --api-key your-key")
        print("\n🔑 Get free API key at: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Initialize pipeline
    print("\n" + "="*60)
    print("🚀 NACC Asset Declaration Digitization System")
    print("="*60)
    print(f"📌 Using Gemini 2.0 Flash")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        pipeline = Pipeline(api_key=api_key, use_imputation=not args.skip_imputation)
        
        if args.pdf:
            # Process single PDF
            pdf_path = Path(args.pdf)
            if not pdf_path.exists():
                print(f"❌ PDF file not found: {pdf_path}")
                sys.exit(1)
            
            pipeline.process_single_pdf(
                pdf_path,
                submitter_id=1,
                nacc_id=1
            )
            
        elif args.mode:
            # Process dataset
            output_dir = pipeline.process_dataset(
                mode=args.mode,
                limit=args.limit
            )
            
            print(f"\n✅ Processing complete!")
            print(f"📁 Output directory: {output_dir}")
            
        else:
            parser.print_help()
            print("\n❌ Error: Please specify --mode or --pdf")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
