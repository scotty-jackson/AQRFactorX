#!/usr/bin/env python3
"""
Quick dataset preview tool for AQR datasets
Usage: python preview_dataset.py <path_to_xlsx_file>
"""

import sys
import pandas as pd
from pathlib import Path

def preview_dataset(file_path):
    """Preview an AQR dataset file"""

    file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return

    if not file_path.suffix == '.xlsx':
        print(f"Error: File must be an Excel file (.xlsx)")
        return

    print("="*80)
    print(f"Dataset: {file_path.name}")
    print(f"Location: {file_path.parent}")
    print(f"Size: {file_path.stat().st_size / (1024*1024):.2f} MB")
    print("="*80)

    # Read the Excel file to see what sheets are available
    try:
        excel_file = pd.ExcelFile(file_path)
        print(f"\nAvailable sheets: {len(excel_file.sheet_names)}")
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"  {i}. {sheet_name}")

        # Preview the first sheet
        if excel_file.sheet_names:
            first_sheet = excel_file.sheet_names[0]
            print(f"\n{'='*80}")
            print(f"Preview of first sheet: '{first_sheet}'")
            print("="*80)

            df = pd.read_excel(file_path, sheet_name=first_sheet, nrows=10)

            print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns (showing first 10 rows)")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst 10 rows:")
            print(df.to_string())

            # Show data types
            print(f"\n{'='*80}")
            print("Data Types:")
            print("="*80)
            print(df.dtypes)

            # Show basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\n{'='*80}")
                print("Basic Statistics (numeric columns):")
                print("="*80)
                print(df[numeric_cols].describe())

    except Exception as e:
        print(f"Error reading file: {e}")

def list_all_datasets():
    """List all available datasets"""
    data_dir = Path(__file__).parent.parent / "aqr_raw"

    if not data_dir.exists():
        print("Error: data directory not found")
        return

    print("="*80)
    print("Available AQR Datasets")
    print("="*80)

    for category_dir in sorted(data_dir.iterdir()):
        if category_dir.is_dir():
            print(f"\n{category_dir.name}:")
            for file in sorted(category_dir.glob("*.xlsx")):
                size_mb = file.stat().st_size / (1024*1024)
                print(f"  - {file.name} ({size_mb:.1f} MB)")
                print(f"    Path: {file}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, list all datasets
        list_all_datasets()
        print("\n" + "="*80)
        print("Usage: python preview_dataset.py <path_to_xlsx_file>")
        print("="*80)
    elif len(sys.argv) == 2:
        # Preview specific dataset
        preview_dataset(sys.argv[1])
    else:
        print("Usage: python preview_dataset.py [path_to_xlsx_file]")
        print("Run without arguments to list all available datasets")
