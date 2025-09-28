#!/usr/bin/env python3
"""
Fix basic_data.xlsx file:
1. Add proper fname field (combination of job and disease)
2. Fix fid field (ncc_ + ids value)
3. Ensure all required fields are present
"""

import pandas as pd
import os
from datetime import datetime

def fix_basic_data():
    # File paths
    input_file = 'data/basic_data.xlsx'
    backup_file = f'data/basic_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    print(f"🔍 Reading Excel file: {input_file}")

    # Read the Excel file
    try:
        df = pd.read_excel(input_file)
        print(f"✅ Successfully read {len(df)} rows")
        print(f"📋 Current columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

    # Create backup
    try:
        df.to_excel(backup_file, index=False)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️ Warning: Could not create backup: {e}")

    # Show sample of current data
    print("\n📊 Sample of current data:")
    print(df.head(3).to_string())

    # Fix fid field: ncc_ + ids value
    if 'ids' in df.columns:
        print(f"\n🔧 Fixing fid field...")
        df['fid'] = 'ncc_' + df['ids'].astype(str)
        print(f"✅ Updated fid field (first 5): {df['fid'].head().tolist()}")
    else:
        print("❌ Error: 'ids' column not found!")
        return False

    # Fix fname field: combination of job and disease
    if 'job' in df.columns and 'disease' in df.columns:
        print(f"\n🔧 Creating fname field...")

        def create_fname(row):
            job_name = str(row.get('job', '미상 직종')).strip()
            disease_name = str(row.get('disease', '질병')).strip()

            # Handle NaN or empty values
            if pd.isna(job_name) or job_name == 'nan' or job_name == '':
                job_name = '미상 직종'
            if pd.isna(disease_name) or disease_name == 'nan' or disease_name == '':
                disease_name = '질병'

            return f"{job_name} 관련 {disease_name}"

        df['fname'] = df.apply(create_fname, axis=1)
        print(f"✅ Created fname field (first 5): {df['fname'].head().tolist()}")
    else:
        print("❌ Error: 'job' or 'disease' columns not found!")
        print(f"Available columns: {list(df.columns)}")
        return False

    # Ensure all required fields are present
    required_fields = [
        'fid', 'ids', 'fname', 'job', 'disease', 'job_code', 'disease_code',
        'decision', 'smry', 'exposure', 'pdf_link', 'pop_link', 'process_link',
        'exp_start', 'exp_period'
    ]

    print(f"\n🔍 Checking required fields...")
    missing_fields = []
    for field in required_fields:
        if field not in df.columns:
            missing_fields.append(field)
            # Add missing field with default empty value
            df[field] = ''

    if missing_fields:
        print(f"⚠️ Added missing fields: {missing_fields}")
    else:
        print("✅ All required fields present")

    # Reorder columns to put important ones first
    column_order = [
        'fid', 'ids', 'fname', 'job', 'disease', 'job_code', 'disease_code',
        'decision', 'smry', 'exposure', 'pdf_link', 'pop_link', 'process_link',
        'exp_start', 'exp_period'
    ]

    # Add any additional columns that weren't in our standard list
    additional_columns = [col for col in df.columns if col not in column_order]
    final_column_order = column_order + additional_columns

    # Only include columns that actually exist
    final_column_order = [col for col in final_column_order if col in df.columns]
    df = df[final_column_order]

    print(f"\n📋 Final column order: {final_column_order}")

    # Show sample of fixed data
    print("\n📊 Sample of fixed data:")
    print(df[['fid', 'ids', 'fname', 'job', 'disease']].head(3).to_string())

    # Save the fixed file
    try:
        df.to_excel(input_file, index=False)
        print(f"\n✅ Successfully saved fixed file: {input_file}")
        print(f"📊 Total rows: {len(df)}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting basic_data.xlsx fix...")
    success = fix_basic_data()
    if success:
        print("\n🎉 basic_data.xlsx has been successfully fixed!")
        print("📌 Next steps:")
        print("   1. Run: python manage.py import_data")
        print("   2. Check that fid and fname fields are working correctly")
    else:
        print("\n❌ Failed to fix basic_data.xlsx")