#!/usr/bin/env python3
"""
Debug test to identify the upload issue
"""

import pandas as pd
import os
import sys

# Test file path
file_path = "../database/seed_data/nfhs5_real/PLS_FY19_AE_pud19i.csv"

print("=" * 50)
print("DEBUG TEST - File Reading")
print("=" * 50)

# Check if file exists
if not os.path.exists(file_path):
    print(f"✗ File not found: {file_path}")
    sys.exit(1)

print(f"✓ File exists: {file_path}")
print(f"  Size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")

# Try to read the file with different encodings
encodings = ['us-ascii', 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']

for encoding in encodings:
    print(f"\nTrying encoding: {encoding}")
    try:
        df = pd.read_csv(file_path, encoding=encoding, nrows=5)
        print(f"  ✓ Success! Read {len(df)} rows")
        print(f"  Columns: {df.columns.tolist()[:5]}...")
        
        # Try reading full file
        print(f"  Reading full file...")
        df_full = pd.read_csv(file_path, encoding=encoding, low_memory=False)
        print(f"  ✓ Full file read: {len(df_full)} rows, {len(df_full.columns)} columns")
        
        # Check for problematic characters in column names
        print(f"\n  Column names check:")
        for col in df_full.columns[:10]:
            print(f"    - {repr(col)}")
        
        # Try to save a sample
        print(f"\n  Testing save to CSV...")
        test_save_path = "test_save.csv"
        df_full.head(100).to_csv(test_save_path, index=False)
        print(f"  ✓ Saved sample to {test_save_path}")
        
        # Clean up
        os.remove(test_save_path)
        
        print(f"\n✓ Encoding {encoding} works perfectly!")
        break
        
    except UnicodeDecodeError as e:
        print(f"  ✗ Unicode error: {str(e)[:100]}")
    except Exception as e:
        print(f"  ✗ Other error: {str(e)[:100]}")

print("\n" + "=" * 50)
print("Testing direct import of services...")
print("=" * 50)

try:
    from services.file_manager import FileManager
    print("✓ FileManager imported")
    
    # Test creating instance folders
    import uuid
    test_id = str(uuid.uuid4())
    print(f"\nTesting FileManager.create_instance_folders with ID: {test_id[:8]}...")
    
    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    paths = FileManager.create_instance_folders(test_id)
    print(f"✓ Created instance folders:")
    for stage, path in paths.items():
        print(f"  Stage {stage}: {path}")
    
    # Clean up test folders
    import shutil
    shutil.rmtree(f"data/{test_id}")
    print(f"✓ Cleaned up test folders")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)
print("Testing database connection...")
print("=" * 50)

try:
    from services.database import DatabaseService
    from asyncio import run
    
    async def test_db():
        db = DatabaseService()
        await db.initialize()
        print("✓ Database connected")
        
        # Test creating a document
        import json
        test_data = {
            "document_name": "Test Document",
            "original_filename": "test.csv",
            "file_path": "/tmp/test.csv",
            "file_size": 1000,
            "file_type": ".csv",
            "row_count": 100,
            "column_count": 10,
            "metadata": {"test": "data"}
        }
        
        doc_id = await db.create_document(test_data)
        print(f"✓ Created test document: {doc_id}")
        
        # Clean up
        db.client.execute(f"ALTER TABLE documents DELETE WHERE document_id = '{doc_id}'")
        print(f"✓ Cleaned up test document")
        
        await db.close()
    
    run(test_db())
    
except Exception as e:
    print(f"✗ Database error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("DEBUG TEST COMPLETE")
print("=" * 50)