from django.http import JsonResponse, HttpResponse


def ratelimited(request, exception):
    if request.headers.get('Accept', '').startswith('application/json') or request.path.startswith('/objects/api/'):
        return JsonResponse({'error': 'Слишком много запросов. Попробуйте позже.'}, status=429)
    return HttpResponse('Слишком много запросов. Попробуйте через минуту.', status=429)
