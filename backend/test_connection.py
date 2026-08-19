from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL

def verify_connection():
    print("Testing connection to Google Gemini API...")
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.1
    )
    response = llm.invoke("Hello! Respond with 'System Ready' if you can read this.")
    print(f"Response: {response.content.strip()}")

if __name__ == "__main__":
    verify_connection()