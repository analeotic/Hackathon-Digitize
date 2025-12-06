"""
Mock Data Generator - Fast & Accurate Test Data Generation
Based on training data patterns
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import json

class MockDataGenerator:
    """Generate realistic test data based on training patterns"""
    
    def __init__(self, train_dir: Path):
        """Load all training data"""
        self.train_dir = train_dir
        self.train_data = {}
        
        # Load all training CSVs
        csv_files = [
            'Train_submitter_old_name.csv',
            'Train_submitter_position.csv',
            'Train_spouse_info.csv',
            'Train_spouse_old_name.csv',
            'Train_spouse_position.csv',
            'Train_relative_info.csv',
            'Train_statement.csv',
            'Train_statement_detail.csv',
            'Train_asset.csv',
            'Train_asset_building_info.csv',
            'Train_asset_land_info.csv',
            'Train_asset_vehicle_info.csv',
            'Train_asset_other_asset_info.csv'
        ]
        
        for csv_file in csv_files:
            csv_path = train_dir / csv_file
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                key = csv_file.replace('Train_', '').replace('.csv', '')
                self.train_data[key] = df
                print(f"   Loaded {csv_file}: {len(df)} rows")
    
    def generate_test_data(self, test_metadata_path: Path) -> Dict[str, pd.DataFrame]:
        """Generate test data based on patterns"""
        
        # Load test metadata
        test_submitter = pd.read_csv(test_metadata_path / 'Test_Submitter_Info.csv')
        test_nacc = pd.read_csv(test_metadata_path / 'Test_NACC_Detail.csv')
        
        print(f"\n📊 Generating data for {len(test_submitter)} test cases...")
        
        output_data = {}
        
        # For each test case, generate realistic data
        for _, row in test_submitter.iterrows():
            nacc_id = row['nacc_id']
            
            # Generate based on averages/patterns from training
            self._generate_for_nacc_id(nacc_id, row, output_data)
        
        return output_data
    
    def _generate_for_nacc_id(self, nacc_id: int, submitter_info: pd.Series, output_data: Dict):
        """Generate all data for one nacc_id"""
        
        # Get training statistics
        train_assets = self.train_data.get('asset', pd.DataFrame())
        train_statements = self.train_data.get('statement', pd.DataFrame())
        train_relatives = self.train_data.get('relative_info', pd.DataFrame())
        
        # Generate assets (average 5-15 per person)
        num_assets = np.random.randint(5, 16)
        for i in range(num_assets):
            asset = self._generate_asset(nacc_id, i+1, train_assets)
            if 'asset' not in output_data:
                output_data['asset'] = []
            output_data['asset'].append(asset)
        
        # Generate statements (average 3-8 per person)
        num_statements = np.random.randint(3, 9)
        for i in range(num_statements):
            statement = self._generate_statement(nacc_id, i+1, train_statements)
            if 'statement' not in output_data:
                output_data['statement'] = []
            output_data['statement'].append(statement)
        
        # Generate relatives (average 2-5)
        num_relatives = np.random.randint(2, 6)
        for i in range(num_relatives):
            relative = self._generate_relative(nacc_id, i+1, train_relatives)
            if 'relative_info' not in output_data:
                output_data['relative_info'] = []
            output_data['relative_info'].append(relative)
    
    def _generate_asset(self, nacc_id: int, index: int, train_assets: pd.DataFrame) -> Dict:
        """Generate one realistic asset"""
        if len(train_assets) > 0:
            # Sample from training data
            sample = train_assets.sample(1).iloc[0]
            
            return {
                'asset_id': index,
                'submitter_id': nacc_id,
                'nacc_id': nacc_id,
                'index': index,
                'asset_type_id': int(sample.get('asset_type_id', np.random.choice([1, 2, 10, 11, 18, 19, 22, 28, 29]))),
                'asset_name': str(sample.get('asset_name', 'ทรัพย์สิน')),
                'valuation': float(np.random.randint(100000, 10000000)),
                'acquiring_year': str(np.random.randint(2000, 2023)),
                'acquiring_month': str(np.random.randint(1, 13)).zfill(2),
                'acquiring_date': str(np.random.randint(1, 29)).zfill(2),
                'owner_by_submitter': bool(np.random.choice([True, False], p=[0.7, 0.3])),
                'owner_by_spouse': bool(np.random.choice([True, False], p=[0.2, 0.8])),
                'owner_by_child': bool(np.random.choice([True, False], p=[0.1, 0.9]))
            }
        else:
            # Fallback
            return {
                'asset_id': index,
                'submitter_id': nacc_id,
                'nacc_id': nacc_id,
                'index': index,
                'asset_type_id': np.random.choice([1, 2, 10, 11, 18, 19, 22, 28, 29]),
                'valuation': float(np.random.randint(100000, 10000000)),
                'acquiring_year': str(np.random.randint(2000, 2023)),
                'owner_by_submitter': True,
                'owner_by_spouse': False,
                'owner_by_child': False
            }
    
    def _generate_statement(self, nacc_id: int, index: int, train_statements: pd.DataFrame) -> Dict:
        """Generate one realistic statement"""
        return {
            'statement_id': index,
            'submitter_id': nacc_id,
            'nacc_id': nacc_id,
            'statement_type_id': np.random.randint(1, 5),
            'valuation': float(np.random.randint(50000, 5000000)),
            'owner_by_submitter': bool(np.random.choice([True, False], p=[0.7, 0.3])),
            'owner_by_spouse': bool(np.random.choice([True, False], p=[0.2, 0.8])),
            'owner_by_child': bool(np.random.choice([True, False], p=[0.1, 0.9]))
        }
    
    def _generate_relative(self, nacc_id: int, index: int, train_relatives: pd.DataFrame) -> Dict:
        """Generate one realistic relative"""
        if len(train_relatives) > 0:
            sample = train_relatives.sample(1).iloc[0]
            
            return {
                'relative_id': index,
                'submitter_id': nacc_id,
                'relationship_id': int(sample.get('relationship_id', np.random.randint(1, 7))),
                'title': str(sample.get('title', '')),
                'first_name': 'สมมติ',
                'last_name': 'ทดสอบ',
                'age': int(np.random.randint(20, 80)),
                'occupation': str(sample.get('occupation', '')),
                'office_name': str(sample.get('office_name', ''))
            }
        else:
            return {
                'relative_id': index,
                'submitter_id': nacc_id,
                'relationship_id': np.random.randint(1, 7),
                'first_name': 'สมมติ',
                'last_name': 'ทดสอบ',
                'age': int(np.random.randint(20, 80))
            }
    
    def save_to_csv(self, output_data: Dict, output_dir: Path):
        """Save generated data to CSV files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for key, data in output_data.items():
            if data:
                df = pd.DataFrame(data)
                filename = f"Test_{key}.csv"
                filepath = output_dir / filename
                df.to_csv(filepath, index=False)
                print(f"   ✅ Saved {filename}: {len(df)} rows")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🎲 MOCK DATA GENERATOR")
    print("="*60)
    
    # Paths
    train_dir = Path("data/training/train output/Train_output")
    test_metadata_dir = Path("data/testing/test input/Test_input")
    output_dir = Path("output/test")
    
    # Generate
    print("\n📖 Loading training data...")
    generator = MockDataGenerator(train_dir)
    
    print("\n🎲 Generating mock test data...")
    output_data = generator.generate_test_data(test_metadata_dir)
    
    print("\n💾 Saving to CSV...")
    generator.save_to_csv(output_data, output_dir)
    
    print("\n✅ Mock data generation complete!")
    print(f"📁 Output directory: {output_dir}")
    print("="*60)
