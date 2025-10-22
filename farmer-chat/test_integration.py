import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

try:
    from api.utils import HEALTHCARE_PDF_AVAILABLE, process_query
    print('HEALTHCARE_PDF_AVAILABLE in api.utils:', HEALTHCARE_PDF_AVAILABLE)
    
    # Test the process_query function directly
    result = process_query('I have cough', 'test@email.com', {'first_name': 'Ayaan'})
    print('Response keys:', list(result.keys()))
    print('Response preview:', result.get('translated_response', 'No response')[:150] + '...')
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()