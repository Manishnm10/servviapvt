"""
Test FarmStack API Integration
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from retrieval.content_retrieval import retrieve_content_from_api

def test_farmstack_query():
    print("\n🧪 Testing FarmStack API Integration\n")
    
    # Use your actual FarmStack email
    user_email = "mohammedayaan2193@gmail.com"
    
    test_queries = [
        "What are remedies for headache?",
        "How to treat fever naturally?",
        "What helps with cold and cough?"
    ]
    
    for query in test_queries:
        print("=" * 70)
        print(f"Query: {query}")
        print("=" * 70)
        
        try:
            content = retrieve_content_from_api(
                query=query,
                user_email=user_email
            )
            
            if content:
                print(f"✅ Retrieved {len(content)} content chunks")
                if isinstance(content, list) and len(content) > 0:
                    preview = content[0][:200] if len(str(content[0])) > 200 else content[0]
                    print(f"Preview: {preview}...")
                else:
                    print(f"Content: {content}")
            else:
                print("❌ No content retrieved")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    test_farmstack_query()