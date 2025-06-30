import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_reply(message):
    prompt = f"Antwortvorschlag für folgende Nachricht eines Nutzers:\n\"{message}\"\n\nAntwort:"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.7
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"[Fehler bei GPT: {str(e)}]"
