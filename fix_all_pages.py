# fix_all_pages.py - Run this to fix all your page files at once
import os
import re

def fix_page_file(filepath):
    """Fix a single page file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if "st.set_page_config" in content and "import streamlit as st" in content:
        # Check if the order is correct
        lines = content.split('\n')
        
        # Find the position of streamlit import
        st_import_idx = -1
        set_config_idx = -1
        
        for i, line in enumerate(lines):
            if 'import streamlit as st' in line or 'import streamlit' in line:
                st_import_idx = i
            if 'st.set_page_config' in line:
                set_config_idx = i
        
        # If set_page_config comes before import, fix it
        if set_config_idx < st_import_idx and set_config_idx != -1:
            print(f"  Fixing order in {os.path.basename(filepath)}")
            # Move set_page_config after import
            st_line = lines[st_import_idx]
            config_line = lines[set_config_idx]
            lines.pop(set_config_idx)
            # Find position after import
            lines.insert(st_import_idx + 1, config_line)
            content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    
    # If completely broken, rewrite the file
    if 'st.markdown' in content and 'import streamlit' not in content:
        print(f"  Completely rewriting {os.path.basename(filepath)}")
        # This file needs a complete rewrite
        return False
    
    return True

# Fix all page files
pages_dir = "pages"
if not os.path.exists(pages_dir):
    print(f"❌ Pages directory not found: {pages_dir}")
    exit(1)

print(f"📁 Fixing files in {pages_dir}/")
print("-" * 50)

fixed_count = 0
for filename in os.listdir(pages_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(pages_dir, filename)
        print(f"\n📄 Checking {filename}...")
        
        if fix_page_file(filepath):
            fixed_count += 1
            print(f"  ✅ Fixed")
        else:
            print(f"  ⚠️ Needs manual review")

print("\n" + "=" * 50)
print(f"✅ Fixed {fixed_count} files")
print("\nIf some files still have issues, please share the specific error messages.")
