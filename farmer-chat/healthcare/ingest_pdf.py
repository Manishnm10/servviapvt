import os
import sys
import json

def main():
    print("🏥 ServVIA Healthcare PDF Ingestion")
    print("=" * 40)
    
    # Check if PDF exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    pdf_path = os.path.join(parent_dir, 'healthcare_data', 'Home_Remedies_Guide.pdf')
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found at: {pdf_path}")
        return False
    
    print(f"✅ Found PDF: {os.path.basename(pdf_path)}")
    
    # Add parent directory to Python path
    sys.path.insert(0, parent_dir)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
    
    try:
        import django
        django.setup()
        
        # Since farmer-chat uses a different approach, let's create a simple test
        # to make sure our PDF content gets into the system
        
        print("🔧 Setting up Django environment...")
        
        # Let's try to use farmer-chat's existing RAG pipeline
        # First, let's check what modules are available
        try:
            from retrieval.content_retrieval import content_retrieval
            print("✅ Found content_retrieval module")
        except ImportError as e:
            print(f"⚠️ content_retrieval not available: {e}")
        
        try:
            from rag_service.execute_rag import execute_rag_pipeline
            print("✅ Found execute_rag_pipeline module")
        except ImportError as e:
            print(f"⚠️ execute_rag_pipeline not available: {e}")
        
        # For now, let's create a simple placeholder that confirms setup
        print("\n📄 PDF File Details:")
        print(f"   Path: {pdf_path}")
        print(f"   Size: {os.path.getsize(pdf_path)} bytes")
        print(f"   Exists: {os.path.exists(pdf_path)}")
        
        # Create a simple marker file to indicate PDF is ready
        marker_file = os.path.join(parent_dir, 'healthcare_data', 'pdf_ready.json')
        pdf_info = {
            "pdf_path": pdf_path,
            "pdf_name": "Home_Remedies_Guide.pdf",
            "ingestion_date": "2025-10-11",
            "status": "ready_for_ingestion",
            "type": "healthcare",
            "category": "home_remedies"
        }
        
        with open(marker_file, 'w') as f:
            json.dump(pdf_info, f, indent=2)
        
        print(f"✅ Created PDF marker file: {marker_file}")
        print("\n🎯 PDF is ready for ServVIA ingestion!")
        print("📋 Next steps:")
        print("   1. The PDF is in the correct location")
        print("   2. We'll modify the content retrieval to use your PDF")
        print("   3. ServVIA will be able to answer questions from your PDF content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("\n💡 Let's try a different approach...")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Setup complete!")
        print("🚀 Let's configure ServVIA to use your PDF content...")
    else:
        print("\n⚠️ Setup had issues, but we can still proceed with configuration.")
    
    input("Press Enter to continue...")