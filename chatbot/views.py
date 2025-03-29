import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

DICTIONARY_API_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

@csrf_exempt
def get_word(request, word):
    try:
        response = requests.get(f'{DICTIONARY_API_URL}{word}')
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data[0])
    except requests.exceptions.HTTPError:
        return JsonResponse({'error': 'Word not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)