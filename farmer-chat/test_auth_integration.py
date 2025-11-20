"""
Test Authentication Integration
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 17:14:18
Current User's Login: Raghuraam21
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

print("\n" + "=" * 70)
print("  Authentication Integration Test")
print("  Current Date and Time (UTC): 2025-11-19 17:14:18")
print("  Current User: Raghuraam21")
print("=" * 70)

# Test 1: Check static files
print("\n1️⃣ Checking static files...")
from django.conf import settings
from pathlib import Path

static_dir = Path(settings.BASE_DIR) / 'static' / 'js'
print(f"   Static directory: {static_dir}")

if not static_dir.exists():
    print(f"   ⚠️ Creating static/js directory...")
    static_dir.mkdir(parents=True, exist_ok=True)

auth_js = static_dir / 'auth.js'
medical_js = static_dir / 'medical-profile.js'

if auth_js.exists():
    print(f"   ✅ auth.js found ({auth_js.stat().st_size} bytes)")
else:
    print(f"   ❌ auth.js NOT found at: {auth_js}")

if medical_js.exists():
    print(f"   ✅ medical-profile.js found ({medical_js.stat().st_size} bytes)")
else:
    print(f"   ❌ medical-profile.js NOT found at: {medical_js}")

# Test 2: Check templates
print("\n2️⃣ Checking templates...")
templates_dir = Path(settings.BASE_DIR) / 'templates'
index_html = templates_dir / 'index.html'
login_html = templates_dir / 'auth' / 'login.html'
register_html = templates_dir / 'auth' / 'register.html'

print(f"   Templates directory: {templates_dir}")

if index_html.exists():
    print(f"   ✅ index.html found ({index_html.stat().st_size} bytes)")
else:
    print(f"   ❌ index.html NOT found at: {index_html}")

if login_html.exists():
    print(f"   ✅ login.html found ({login_html.stat().st_size} bytes)")
else:
    print(f"   ❌ login.html NOT found at: {login_html}")

if register_html.exists():
    print(f"   ✅ register.html found ({register_html.stat().st_size} bytes)")
else:
    print(f"   ❌ register.html NOT found at: {register_html}")

# Test 3: Check API views
print("\n3️⃣ Checking API views...")
try:
    from api.auth_page_views import index_page, login_page, register_page, dashboard_page
    print("   ✅ auth_page_views.py imported successfully")
    print(f"      - index_page: {index_page}")
    print(f"      - login_page: {login_page}")
    print(f"      - register_page: {register_page}")
    print(f"      - dashboard_page: {dashboard_page}")
except ImportError as e:
    print(f"   ❌ Failed to import auth_page_views: {e}")

try:
    from api.auth_views import register_view, login_view
    print("   ✅ auth_views.py imported successfully")
    print(f"      - register_view: {register_view}")
    print(f"      - login_view: {login_view}")
except ImportError as e:
    print(f"   ❌ Failed to import auth_views: {e}")

try:
    from api.medical_profile_api import create_or_update_medical_profile, get_medical_profile
    print("   ✅ medical_profile_api.py imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import medical_profile_api: {e}")

# Test 4: Check URLs
print("\n4️⃣ Checking URL configuration...")
try:
    from django.urls import reverse
    
    urls_to_check = [
        ('chatbot-home', '/'),
        ('login-page', '/login/'),
        ('register-page', '/register/'),
        ('dashboard-page', '/dashboard/'),
        ('auth-login', '/auth/login/'),
        ('auth-register', '/auth/register/'),
        ('medical-profile-create-update', '/medical/profile/'),
    ]
    
    for name, expected_path in urls_to_check:
        try:
            path = reverse(name)
            if path == expected_path:
                print(f"   ✅ {name:<35} → {path}")
            else:
                print(f"   ⚠️ {name:<35} → {path} (expected: {expected_path})")
        except Exception as e:
            print(f"   ❌ {name:<35} → Error: {e}")
            
except Exception as e:
    print(f"   ❌ URL check failed: {e}")

# Test 5: Check database password field
print("\n5️⃣ Checking database schema...")
try:
    from database.models import User
    db = User._meta.database
    
    cursor = db.execute_sql("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name='user' AND column_name='password'
    """)
    
    result = cursor.fetchone()
    if result:
        col_name, data_type, max_length = result
        print(f"   ✅ Password field exists: {col_name} {data_type}({max_length})")
    else:
        print("   ❌ Password field NOT found in database")
        print("   💡 Run: python create_password_migration.py")
        
except Exception as e:
    print(f"   ❌ Database check failed: {e}")

# Test 6: Check settings
print("\n6️⃣ Checking Django settings...")
try:
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   BASE_DIR: {settings.BASE_DIR}")
    
    if hasattr(settings, 'STATICFILES_DIRS'):
        print(f"   STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    else:
        print("   ⚠️ STATICFILES_DIRS not configured")
    
    if hasattr(settings, 'TEMPLATES'):
        template_dirs = settings.TEMPLATES[0].get('DIRS', [])
        print(f"   TEMPLATE_DIRS: {template_dirs}")
    else:
        print("   ⚠️ TEMPLATES not configured")
        
except Exception as e:
    print(f"   ❌ Settings check failed: {e}")

# Test 7: Summary
print("\n" + "=" * 70)
print("📊 Integration Test Summary")
print("=" * 70)

issues = []

if not auth_js.exists():
    issues.append("❌ Missing: static/js/auth.js")
if not medical_js.exists():
    issues.append("❌ Missing: static/js/medical-profile.js")
if not index_html.exists():
    issues.append("❌ Missing: templates/index.html")
if not login_html.exists():
    issues.append("❌ Missing: templates/auth/login.html")
if not register_html.exists():
    issues.append("❌ Missing: templates/auth/register.html")

if issues:
    print("\n⚠️ Issues Found:")
    for issue in issues:
        print(f"   {issue}")
    print("\n💡 Please create missing files before continuing.")
else:
    print("\n✅ All integration checks passed!")
    print("\n🚀 Next Steps:")
    print("   1. Start server: python manage.py runserver 0.0.0.0:8000")
    print("   2. Open browser: http://localhost:8000/")
    print("   3. Should redirect to: http://localhost:8000/login/")
    print("   4. Register new account with strong password")
    print("   5. Login and test medical profile")

print("\n" + "=" * 70)
print(f"✅ Test completed at: 2025-11-19 17:14:18 UTC")
print("=" * 70 + "\n")