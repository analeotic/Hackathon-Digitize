"""
Data Imputation Module - Clean and validate data before extraction
Implements the Imputation stage in: Data → Imputation → Docling → LLM → CSV
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import re
from datetime import datetime
import PyPDF2


class DataImputer:
    """Handle data cleaning, validation, and missing value imputation"""
    
    def __init__(self, strategy: str = "forward_fill", verbose: bool = True):
        """
        Initialize DataImputer
        
        Args:
            strategy: Imputation strategy ('forward_fill', 'mean', 'mode', 'none')
            verbose: Print imputation statistics
        """
        self.strategy = strategy
        self.verbose = verbose
        self.stats = {
            "metadata_filled": 0,
            "pdfs_validated": 0,
            "text_cleaned": 0,
            "errors": []
        }
    
    def impute_metadata(self, df: pd.DataFrame, table_name: str = "") -> pd.DataFrame:
        """
        Fill missing values in metadata DataFrames
        
        Args:
            df: DataFrame to impute
            table_name: Name of table for logging
            
        Returns:
            DataFrame with imputed values
        """
        if df.empty:
            return df
        
        df_copy = df.copy()
        initial_nulls = df_copy.isnull().sum().sum()
        
        # Strategy 1: Forward fill for sequential data
        if self.strategy == "forward_fill":
            df_copy = df_copy.fillna(method='ffill')
        
        # Strategy 2: Fill with defaults based on column type
        for col in df_copy.columns:
            if df_copy[col].isnull().any():
                if df_copy[col].dtype == 'object':
                    # Text fields: empty string
                    df_copy[col] = df_copy[col].fillna("")
                elif df_copy[col].dtype in ['int64', 'float64']:
                    # Numeric fields: 0 or mean
                    if self.strategy == "mean":
                        df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
                    else:
                        df_copy[col] = df_copy[col].fillna(0)
        
        final_nulls = df_copy.isnull().sum().sum()
        filled_count = initial_nulls - final_nulls
        
        if filled_count > 0:
            self.stats["metadata_filled"] += filled_count
            if self.verbose:
                print(f"   📊 Imputation ({table_name}): Filled {filled_count} missing values")
        
        return df_copy
    
    def validate_pdf(self, pdf_path: Path) -> Dict:
        """
        Validate PDF file before extraction
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "num_pages": 0,
            "file_size_mb": 0.0,
            "warnings": [],
            "errors": []
        }
        
        # Check 1: File exists
        if not pdf_path.exists():
            result["errors"].append(f"File not found: {pdf_path}")
            return result
        
        # Check 2: File size
        file_size_bytes = pdf_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        result["file_size_mb"] = round(file_size_mb, 2)
        
        if file_size_mb > 100:
            result["warnings"].append(f"Large file: {file_size_mb:.1f}MB")
        
        # Check 3: Is valid PDF
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                result["num_pages"] = len(pdf_reader.pages)
                
                if result["num_pages"] == 0:
                    result["errors"].append("PDF has 0 pages")
                    return result
                
                # Try to read first page to verify not corrupted
                _ = pdf_reader.pages[0]
                
                result["valid"] = True
                self.stats["pdfs_validated"] += 1
                
                if self.verbose:
                    print(f"   ✅ PDF Valid: {result['num_pages']} pages, {result['file_size_mb']}MB")
                
        except Exception as e:
            result["errors"].append(f"PDF read error: {str(e)}")
            if self.verbose:
                print(f"   ❌ PDF Invalid: {str(e)}")
        
        return result
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text fields
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        self.stats["text_cleaned"] += 1
        
        return text
    
    def normalize_numeric(self, value: str) -> Optional[float]:
        """
        Normalize numeric values from text
        
        Args:
            value: Numeric value as string (may have commas, "บาท", etc.)
            
        Returns:
            Float value or None
        """
        if not isinstance(value, str):
            return value
        
        # Remove common Thai suffixes
        value = value.replace("บาท", "").replace("ล้าน", "")
        
        # Remove commas
        value = value.replace(",", "")
        
        # Try to convert to float
        try:
            return float(value.strip())
        except ValueError:
            return None
    
    def normalize_date(self, year: str, month: str = None, day: str = None) -> Dict:
        """
        Normalize date components
        
        Args:
            year: Year (may be Buddhist or Christian)
            month: Month (1-12 or name)
            day: Day (1-31)
            
        Returns:
            Dictionary with normalized year, month, day
        """
        result = {"year": None, "month": None, "day": None}
        
        # Normalize year (Buddhist → Christian)
        if year:
            try:
                year_num = int(str(year))
                if year_num > 2500:  # Buddhist year
                    year_num -= 543
                result["year"] = str(year_num)
            except ValueError:
                pass
        
        # Normalize month
        if month:
            try:
                month_num = int(str(month))
                if 1 <= month_num <= 12:
                    result["month"] = f"{month_num:02d}"
            except ValueError:
                # Try to parse month name (Thai/English)
                month_map = {
                    "มกราคม": "01", "january": "01", "jan": "01",
                    "กุมภาพันธ์": "02", "february": "02", "feb": "02",
                    "มีนาคม": "03", "march": "03", "mar": "03",
                    "เมษายน": "04", "april": "04", "apr": "04",
                    "พฤษภาคม": "05", "may": "05",
                    "มิถุนายน": "06", "june": "06", "jun": "06",
                    "กรกฎาคม": "07", "july": "07", "jul": "07",
                    "สิงหาคม": "08", "august": "08", "aug": "08",
                    "กันยายน": "09", "september": "09", "sep": "09",
                    "ตุลาคม": "10", "october": "10", "oct": "10",
                    "พฤศจิกายน": "11", "november": "11", "nov": "11",
                    "ธันวาคม": "12", "december": "12", "dec": "12"
                }
                month_lower = str(month).lower()
                result["month"] = month_map.get(month_lower)
        
        # Normalize day
        if day:
            try:
                day_num = int(str(day))
                if 1 <= day_num <= 31:
                    result["day"] = f"{day_num:02d}"
            except ValueError:
                pass
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get imputation statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            "metadata_filled": 0,
            "pdfs_validated": 0,
            "text_cleaned": 0,
            "errors": []
        }
