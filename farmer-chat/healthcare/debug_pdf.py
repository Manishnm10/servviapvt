import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')

try:
    import django
    django.setup()
except:
    pass

from healthcare.pdf_content_handler import pdf_handler

def debug_pdf():
    print("=" * 60)
    print("🔍 ServVIA PDF Content Debugger")
    print("=" * 60)
    
    # Extract content
    print("\n1️⃣ Extracting PDF content...")
    pdf_handler.extract_and_process_content()
    
    # Show what conditions were found
    print(f"\n2️⃣ Conditions found in PDF: {len(pdf_handler.remedies_db)}")
    for condition, remedies in pdf_handler.remedies_db.items():
        print(f"   • {condition}: {len(remedies)} remedies")
    
    # Test queries
    print("\n3️⃣ Testing queries:")
    
    test_queries = [
        "nanige jwara ide",  # Kannada: I have fever
        "I have fever",       # English
        "fever",              # Direct
        "jwara",              # Kannada word
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        result = pdf_handler.get_remedies_for_condition(query)
        if result:
            print(f"   ✅ Found {len(result)} remedies")
        else:
            print(f"   ❌ No remedies found")
    
    # Show first 500 chars of PDF to see structure
    print("\n4️⃣ PDF Content Preview (first 1000 chars):")
    print("-" * 60)
    if pdf_handler.content:
        print(pdf_handler.content[:1000])
    print("-" * 60)
    
    print("\n5️⃣ Search for 'fever' in PDF:")
    if pdf_handler.content:
        fever_mentions = [line for line in pdf_handler.content.split('\n') if 'fever' in line.lower()]
        print(f"   Found {len(fever_mentions)} lines mentioning 'fever'")
        for i, line in enumerate(fever_mentions[:5]):
            print(f"   {i+1}. {line.strip()}")

if __name__ == "__main__":
    debug_pdf()