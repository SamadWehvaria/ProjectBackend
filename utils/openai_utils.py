
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def translate_text(text: str, target_lang: str) -> str:
    prompt = f"Translate the following medical phrase to {target_lang}:\n\n{text}\n\nTranslation:"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response["choices"][0]["message"]["content"].strip()
