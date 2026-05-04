import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalyst.settings')
django.setup()
from django.utils import timezone
from typing import Dict
from gigachat import GigaChat

# ---------- ТВОИ КЛЮЧИ ----------
GIGACHAT_CLIENT_ID = "019dc95d-faec-701b-a533-9e40f335da6e"
GIGACHAT_CLIENT_SECRET = "MDE5ZGM5NWQtZmFlYy03MDFiLWE1MzMtOWU0MGYzMzVkYTZlOjUwZTU5MTExLWI3N2MtNDczMi1hOTk0LTQ1Mzc5ZmE0ZTlmOQ=="
# ------------------------------

def _get_active_bookings_map() -> Dict[int, dict]:
    now = timezone.now()
    from booking.models import Booking
    bookings = Booking.objects.filter(
        status=Booking.STATUS_ACTIVE,
        start_time__lte=now,
        end_time__gt=now
    ).select_related('user', 'place')
    result = {}
    for b in bookings:
        result[b.place_id] = {
            "username": b.user.username,
            "end_time": b.end_time.strftime("%d.%m %H:%M")
        }
    return result

def _get_places_full_info() -> str:
    from places.models import Place
    places = Place.objects.select_related('category', 'tariff').all()
    busy_map = _get_active_bookings_map()
    lines = []
    for p in places:
        status = "СВОБОДНО"
        if p.id in busy_map:
            info = busy_map[p.id]
            status = f"ЗАНЯТО (до {info['end_time']}, игрок {info['username']})"
        lines.append(
            f"• Зона #{p.number} «{p.title}» [{p.category.name}] – {status}\n"
            f"  Железо: CPU={p.cpu or '—'}, GPU={p.gpu or '—'}, RAM={p.ram or '—'}, Монитор={p.monitor or '—'}\n"
            f"  Цена: {p.tariff.price_per_hour} ₽/час"
        )
    return "\n".join(lines)

def _get_tariffs_full_info() -> str:
    from tariffs.models import Tariff
    tariffs = Tariff.objects.select_related('category').all()
    lines = []
    for t in tariffs:
        lines.append(
            f"• Тариф «{t.name}» (категория {t.category.name}): {t.price_per_hour} ₽/час"
        )
    return "\n".join(lines)

def _get_club_meta() -> str:
    return (
        "Catalyst Cyber Lounge, г. Курск, пр-т Хрущёва, 2, 2 этаж.\n"
        "Телефон: +7 (904) 525-22-29\n"
        "Режим работы: круглосуточно (24/7).\n"
        "Особенности: RTX 4090/4080, PS5-зона, лаунж-диваны, бар."
    )

def _build_system_prompt() -> str:
    return f"""Ты – ИИ-консультант компьютерного клуба **Catalyst Cyber Lounge** (Курск).
Ты имеешь доступ к актуальной информации о клубе (места, тарифы, занятость, характеристики ПК) и можешь отвечать на любые вопросы, используя эти данные.

{_get_club_meta()}

=== АКТУАЛЬНЫЕ МЕСТА И ИХ СТАТУС (свободно/занято) ===
{_get_places_full_info()}

=== ТАРИФЫ ===
{_get_tariffs_full_info()}

### ТВОИ ОБЯЗАННОСТИ:

1. 🔍 **Поиск мест под требования**: если пользователь говорит, во что хочет играть или какие характеристики нужны (например, «хочу RTX 4090 до 300 ₽/час»), ты ОБЯЗАН найти среди списка выше подходящие варианты. Учитывай цену тарифа, железо, категорию. Сообщи номера зон, цены и что именно подошло.
2. 🟢/🔴 **Статус мест**: всегда говори, свободно место сейчас или занято (и до какого времени). Если подходящее место занято – предложи альтернативы.
3. 💰 **Тарифы и цены**: если спрашивают про тарифы – показывай все варианты с ценами.
4. 🧠 **Консультации по играм**: можешь давать советы по играм, настройкам графики, подбору ПК под конкретную игру.
5. 🍕 **Бар**: напоминай, что в клубе есть бар, энергетики, закуски. Можешь советовать, что заказать под настроение или игру.
6. 🗺️ **Навигация**: если нужен адрес или телефон – выдаёшь контакты.
7. 📢 **Акции/новости**: если бы ты знал об акциях (пока их нет) – сообщал бы. Можешь предлагать идеи для турниров или событий.
8. ❌ **Запрещено**: выдумывать несуществующие зоны или тарифы; указывать неверные цены; если точного ответа нет – честно скажи и предложи связаться с администратором.

Отвечай на русском языке, дружелюбно, используй эмодзи. Выделяй названия зон и цены жирным."""

def ask_gigachat(user_message: str) -> str:
    try:
        # 👇 Вот так правильно для библиотеки gigachat
        with GigaChat(
            credentials=GIGACHAT_CLIENT_SECRET,   # ← только секрет, без client_id
            verify_ssl_certs=False
        ) as client:
            system_prompt = _build_system_prompt()
            response = client.chat({
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            })
            reply = response.choices[0].message.content
            reply = add_links(reply)
            return reply

    except Exception as e:
        print(f"[GigaChat ERROR] {e}")
        return "🤖 ИИ временно недоступен. Попробуйте через минуту или обратитесь к администратору."


def get_ai_suggestions(user_preferences: str) -> str:
    prompt = (
        f"Пользователь хочет: {user_preferences}\n"
        "Подбери до 3 лучших вариантов из доступных мест, учитывая цену и характеристики. "
        "Если ничего не подходит – предложи ближайшие альтернативы."
    )
    return ask_gigachat(prompt)

def get_barman_suggestion(mood: str) -> str:
    prompt = (
        f"Настроение/ситуация: {mood}\n"
        "Посоветуй, что заказать в нашем баре (энергетики, кофе, чай, снэки, сэндвичи). "
        "Будь креативным, используй эмодзи."
    )
    return ask_gigachat(prompt)

def get_tournament_idea() -> str:
    return ask_gigachat(
        "Придумай идею для киберспортивного турнира в Catalyst Cyber Lounge. "
        "Формат, призы, расписание."
    )

def add_links(reply: str) -> str:
    """
    Добавляет кликабельные HTML-кнопки на места и тарифы,
    если они упоминаются в ответе нейросети.
    """
    from places.models import Place
    from tariffs.models import Tariff
    import re

    links = []

    # Ищем упоминания конкретных тарифов по названию
    tariffs = Tariff.objects.all()
    for t in tariffs:
        if t.name.lower() in reply.lower():
            links.append(f'<a href="/places/?tariff={t.id}" class="ai-link-btn">🎮 {t.name} — {t.price_per_hour} ₽/час</a>')

    # Ищем упоминания зон по названию
    places = Place.objects.select_related('tariff').all()
    for p in places:
        if p.title.lower() in reply.lower():
            links.append(f'<a href="/places/{p.id}/" class="ai-link-btn">💻 {p.title} (зона #{p.number})</a>')

    if links:
        reply += '<div class="ai-links-block">' + ''.join(links) + '</div>'

    return reply