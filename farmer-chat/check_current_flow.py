import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

print("🔍 Checking ServVIA API Flow...")

# Check if our utils.py is being used
try:
    import api.utils
    print(f"✅ api.utils imported from: {api.utils.__file__}")
    
    # Check if our debug message function exists
    if hasattr(api.utils, 'process_query'):
        print("✅ process_query function found")
        
        # Test it
        result = api.utils.process_query("test", "test@email.com", {"first_name": "Test"})
        print(f"✅ process_query works: {list(result.keys())}")
    else:
        print("❌ process_query function NOT found")
        
except Exception as e:
    print(f"❌ Error importing api.utils: {e}")

# Check views
try:
    from api.views import ChatAPIViewSet
    print("✅ ChatAPIViewSet imported")
    
    # Check what methods it has
    methods = [m for m in dir(ChatAPIViewSet) if 'create' in m.lower() or 'post' in m.lower()]
    print(f"📋 Available methods: {methods}")
    
except Exception as e:
    print(f"❌ Error importing views: {e}")

print("🔍 Check complete!")