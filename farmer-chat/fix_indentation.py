"""
Fix Indentation in google_oauth.py
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 13:58:48
Current User's Login: Raghuraam21
"""

import re

oauth_file = 'api/google_oauth.py'

print(f"\n{'='*70}")
print(f"  Fixing Indentation in {oauth_file}")
print(f"{'='*70}\n")

try:
    with open(oauth_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all tabs with 4 spaces
    fixed_content = content.replace('\t', '    ')
    
    with open(oauth_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Indentation fixed!")
    print("   - Converted all tabs to spaces")
    print("   - Using 4 spaces per indentation level")
    print(f"\n{'='*70}\n")
    
except Exception as e:
    print(f"❌ Error: {e}")