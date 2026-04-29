# ai/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gigachat import GigaChat

# Токен
GIGACHAT_CREDENTIALS = "MDE5ZGQ5NzMtZTg2Ny03ZjNkLTkyNmQtMDU2NWMwZDk3OWE5OjllYjQ1Njk0LTY3MDgtNDQ0OC1iNjcyLTlkNmY5MWQxNjM1MA=="

def ask_gigachat(system_prompt: str, user_message: str) -> str:
    """Универсальная функция для запросов к GigaChat."""
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }
    
    with GigaChat(credentials=GIGACHAT_CREDENTIALS) as client:
        response = client.chat(payload)
        return response.choices[0].message.content


# Промпт для ИИ-баристы
SYSTEM_PROMPT_BARISTA = """Ты — ИИ-бариста компьютерного клуба "Catalyst Cyber Lounge".
Твоя задача — рекомендовать напитки и закуски под ситуацию клиента.
У нас есть: энергетики (Burn, Monster, Red Bull), кофе (латте, капучино, американо),
чай (черный, зеленый, фруктовый), газировка (Cola, Sprite, Fanta),
снэки (чипсы, начос, сэндвичи, печенье, протеиновые батончики).
Отвечай коротко, дружелюбно, в стиле киберпанк-клуба.
Если вопрос не про еду/напитки — вежливо откажись."""

@csrf_exempt
def ai_barista(request):
    """Рекомендация напитков для любого пользователя"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_query = data.get('query', '')
        
        if not user_query:
            return JsonResponse({'reply': 'Напиши, что тебе нужно, странник.'})
        
        reply = ask_gigachat(SYSTEM_PROMPT_BARISTA, user_query)
        return JsonResponse({'reply': reply})
    
    return JsonResponse({'error': 'POST only'}, status=405)


# Промпт для ИИ-админа
SYSTEM_PROMPT_ADMIN = """Ты — ИИ-помощник администратора компьютерного клуба "Catalyst Cyber Lounge" (г. Курск).
Твои задачи:
1. Писать тексты для новостей, акций, постов в Telegram/VK.
2. Отвечать на отзывы клиентов (негативные и позитивные).
3. Придумывать идеи для турниров и мероприятий.
4. Составлять расписание для персонала.
Клуб работает 24/7. Адрес: Курск, пр-т Хрущёва, 2. 
Стиль общения: дерзкий, киберпанковый, с игровым сленгом."""

@csrf_exempt
def ai_admin_assistant(request):
    """Помощник для админа — только для superuser"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Доступ только для администратора.'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        user_query = data.get('query', '')
        
        if not user_query:
            return JsonResponse({'reply': 'Напиши, что нужно сделать, босс.'})
        
        reply = ask_gigachat(SYSTEM_PROMPT_ADMIN, user_query)
        return JsonResponse({'reply': reply})
    
    return JsonResponse({'error': 'POST only'}, status=405)