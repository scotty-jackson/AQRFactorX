# Quick fix for factor naming in ingest_aqr_factors.py
# This script patches lines 377-379 to always generate unique names

import re

with open('backend/etl/ingest_aqr_factors.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic section
old_code = '''            # Set factor name
            if return_col.strip() and return_col.upper() != return_col:
                metadata['name'] = f"{metadata['name']} - {return_col}"'''

new_code = '''            # Set factor name - use filename + column for uniqueness
            file_name_clean = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            metadata['name'] = f"{file_name_clean} - {return_col}"'''

content = content.replace(old_code, new_code)

with open('backend/etl/ingest_aqr_factors.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed factor naming logic in ingest_aqr_factors.py")
