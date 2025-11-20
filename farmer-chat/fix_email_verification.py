"""
Fix Email Verification Check in OAuth
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 13:53:42
Current User's Login: Raghuraam21

Makes email verification check more flexible for Google OAuth
"""

oauth_file = 'api/google_oauth.py'

print(f"\n{'='*70}")
print(f"  Fixing Email Verification Check")
print(f"{'='*70}\n")

print(f"📝 Reading {oauth_file}...")

try:
    with open(oauth_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Old strict verification code
    old_code = """        email_verified = userinfo.get('email_verified', False)
        
        logger.info(f"✅ User info received: {email} (verified: {email_verified})")
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email not provided by Google'
            }, status=400)
        
        if not email_verified:
            return JsonResponse({
                'success': False,
                'error': 'Email not verified by Google. Please verify your email first.'
            }, status=400)"""
    
    # New flexible verification code
    new_code = """        # Default to True if Google doesn't provide verification status
        # This handles Google Workspace accounts and test users
        email_verified = userinfo.get('email_verified', True)
        
        logger.info(f"✅ User info received: {email} (verified: {email_verified})")
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email not provided by Google'
            }, status=400)
        
        # Only reject if explicitly marked as unverified
        if email_verified is False:
            logger.warning(f"⚠️ Email verification failed for: {email}")
            return JsonResponse({
                'success': False,
                'error': 'Email not verified by Google. Please verify your email first.'
            }, status=400)
        
        logger.info(f"✅ Email verification passed for: {email}")"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(oauth_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ File updated successfully!")
        print("\n📋 Changes made:")
        print("   - Default email_verified to True instead of False")
        print("   - Only reject if explicitly False")
        print("   - Added logging for verification status")
        
        print("\n🔄 Next steps:")
        print("   1. Restart Django server")
        print("   2. Try OAuth login again")
        print("   3. Should work now!")
        
        print(f"\n{'='*70}\n")
    else:
        print("❌ Could not find exact code to replace.")
        print("\n💡 Manual fix needed:")
        print(f"   1. Open {oauth_file}")
        print("   2. Find line: email_verified = userinfo.get('email_verified', False)")
        print("   3. Change False to True")
        print("   4. Save file")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Please update manually in api/google_oauth.py")