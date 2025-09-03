from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

import json

from .models import Subscriber

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            first_name = data.get('first_name')
            if not email or not first_name:
                return JsonResponse({'error': 'email and first_name both required'}, status=400)

            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={"first_name":first_name, "is_active": True},
            )
            
            if not created and subscriber.is_active:
                if subscriber.first_name != first_name:
                    subscriber.first_name = first_name
                    subscriber.save()
                    return JsonResponse({'message': f'Email already subscribed, first_name changed to {first_name}'}, status=200)
                return JsonResponse({'message': 'Email already subscribed'}, status=200)

            if not created and not subscriber.is_active:    
                # Incase of Re-subscription
                subscriber.first_name = first_name
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.resubscribed_at = timezone.now()
                subscriber.save()

            return JsonResponse({'message': 'Subscription successful', 'email': subscriber.email}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Server Error {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'only POST request allowed'}, status=405)
    

@csrf_exempt
def unsubscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'email required'}, status=400)

            try:
                subscriber = Subscriber.objects.get(email=email)
                if subscriber.is_active:
                    subscriber.is_active = False
                    subscriber.unsubscribed_at = timezone.now()
                    subscriber.save()
                    return JsonResponse({'message': 'Unsubscription successful', 'email': subscriber.email}, status=200)
                else:
                    return JsonResponse({'message': 'Email already unsubscribed'}, status=200)
            except Subscriber.DoesNotExist:
                return JsonResponse({'error': 'Email not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': f'Server Error {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'only POST request allowed'}, status=405)