from gigachat import GigaChat


GIGACHAT_CREDENTIALS = "MDE5ZGQ5NzMtZTg2Ny03ZjNkLTkyNmQtMDU2NWMwZDk3OWE5OjllYjQ1Njk0LTY3MDgtNDQ0OC1iNjcyLTlkNmY5MWQxNjM1MA=="

def ask_gigachat(system_prompt: str, user_message: str) -> str:
    """
    Универсальная функция для запросов к GigaChat.
    Принимает системный промпт (роль) и сообщение пользователя.
    Возвращает ответ нейросети.
    """
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7  # 0.5 - строгие ответы, 0.9 - креативные
    }
    
    with GigaChat(credentials=GIGACHAT_CREDENTIALS) as client:
        response = client.chat(payload)
        return response.choices[0].message.content