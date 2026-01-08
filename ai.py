from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

# Load API key from environment (or .env). Use the literal name 'API_KEY'.
GROQ_API_KEY = os.getenv('API_KEY')
if not GROQ_API_KEY:
    raise RuntimeError("GROQ API key not set. Set API_KEY in your environment or in a .env file")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are an Islamic educational assistant for a school Rohis organization.
Explain concepts clearly and respectfully.
Do not issue fatwas or definitive rulings.
If a question requires a scholar, advise consulting a trusted ustadz.
Give concise short answers focused on Islamic teachings and values.
Avoid using table format in your responses.
"""

def call_chatbot_groq(message: str) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": message}
        ],
        temperature=0.4,
        max_tokens=200
    )

    return completion.choices[0].message.content
