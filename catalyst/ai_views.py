# catalyst/ai_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chat_service import ask_gigachat

@csrf_exempt
def ai_chat(request):
    """
    Принимает POST-запрос с JSON: { "message": "текст вопроса" }
    Возвращает JSON: { "reply": "ответ нейросети" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST-запросы'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'reply': '🤖 Не могу разобрать твой запрос. Попробуй ещё раз.'})

    if not user_message:
        return JsonResponse({'reply': '🤖 Напиши что-нибудь, я слушаю.'})

    # Вызываем нейросеть
    reply = ask_gigachat(user_message)
    return JsonResponse({'reply': reply})