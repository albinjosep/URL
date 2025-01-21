from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from .models import URL, AccessLog
from .utils import generate_short_url, is_valid_url
import json

@csrf_exempt
def shorten_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_url = data.get('original_url')
            expiry_hours = data.get('expiry', 24)

            if not is_valid_url(original_url):
                return JsonResponse({'error': 'Invalid URL'}, status=400)

            short_url_hash = generate_short_url(original_url)
            expires_at = now() + timedelta(hours=expiry_hours)

            url, created = URL.objects.get_or_create(
                short_url=short_url_hash,
                defaults={'original_url': original_url, 'expires_at': expires_at}
            )

            return JsonResponse({
                'short_url': f"https://short.ly/{url.short_url}",
                'expires_at': url.expires_at
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

def redirect_url(request, short_url):
    url = get_object_or_404(URL, short_url=short_url)

    if now() > url.expires_at:
        return JsonResponse({'error': 'URL has expired'}, status=410)

    url.access_count += 1
    url.save()

    AccessLog.objects.create(
        short_url=url,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return HttpResponseRedirect(url.original_url)

def url_analytics(request, short_url):
    url = get_object_or_404(URL, short_url=short_url)
    logs = AccessLog.objects.filter(short_url=url).values('accessed_at', 'ip_address')

    return JsonResponse({
        'original_url': url.original_url,
        'short_url': f"https://short.ly/{url.short_url}",
        'access_count': url.access_count,
        'logs': list(logs)
    })
