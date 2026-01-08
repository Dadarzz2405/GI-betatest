from groq import Groq

GROQ_API_KEY = "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"  # keep private
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
