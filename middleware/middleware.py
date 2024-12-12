from django.http import JsonResponse

class ValidatePostRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            # Example validation logic for POST request data
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)
        
        response = self.get_response(request)
        return response
