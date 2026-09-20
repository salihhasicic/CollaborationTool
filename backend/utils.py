import os
import openai
from dotenv import load_dotenv

load_dotenv()

class AIUnavailable(Exception):
    pass

def get_gpt_reply(message):
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise AIUnavailable('Die KI ist noch nicht eingerichtet. Bitte einen API-Schlüssel konfigurieren.')
    try:
        response = openai.ChatCompletion.create(
            api_key=key, model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[{'role': 'user', 'content': f'Formuliere eine kurze Antwort auf diese Nachricht: {message}'}],
            max_tokens=80, temperature=0.7, request_timeout=15)
        return response.choices[0].message['content'].strip()
    except Exception as error:
        raise AIUnavailable('Die KI ist momentan nicht verfügbar. Bitte später erneut versuchen.') from error
