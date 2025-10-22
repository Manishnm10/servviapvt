from django.http import HttpResponse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Only for testing; remove in production for security!
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if not username or not password:
                return JsonResponse({'success': False, 'error': 'Username and password required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    elif request.method == 'GET':
        return HttpResponse('Registration form goes here')
def home(request):
    return HttpResponse("Hello, this is the home page!")