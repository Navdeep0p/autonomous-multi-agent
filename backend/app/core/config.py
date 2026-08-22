import os
import itertools
import threading
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

# 1. Parse Gemini Keys
raw_keys = os.getenv("GEMINI_API_KEYS", "")
key_list = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not key_list:
    single_key = os.getenv("GEMINI_API_KEY", "")
    if single_key:
        key_list = [single_key.strip()]

if not key_list:
    raise ValueError("No Gemini API key found. Please set GEMINI_API_KEYS or GEMINI_API_KEY in your .env file.")

# Compatibility exports
GEMINI_API_KEY = key_list[0]
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DEFAULT_TEMPERATURE = 0.2

class KeyPool:
    def __init__(self, keys: list[str]):
        self.keys = keys
        self._cycle = itertools.cycle(self.keys)
        self._lock = threading.Lock()

    def get_next_key(self) -> str:
        with self._lock:
            return next(self._cycle)

gemini_pool = KeyPool(key_list)

# 2. Local Model Settings
USE_LOCAL_FOR_INTERNAL = os.getenv("USE_LOCAL_FOR_INTERNAL", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# 3. Model Factories
def get_gemini_llm(model: str = None, temperature: float = DEFAULT_TEMPERATURE):
    target_model = model or DEFAULT_MODEL
    api_key = gemini_pool.get_next_key()
    return ChatGoogleGenerativeAI(
        model=target_model,
        temperature=temperature,
        google_api_key=api_key,
        max_retries=3,
        timeout=45
    )

def get_local_llm(model: str = None, temperature: float = DEFAULT_TEMPERATURE):
    target_model = model or OLLAMA_MODEL
    try:
        return ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=target_model,
            temperature=temperature,
            timeout=60
        )
    except Exception:
        return get_gemini_llm(temperature=temperature)

def get_agent_llm(agent_role: str = "supervisor", temperature: float = DEFAULT_TEMPERATURE):
    if USE_LOCAL_FOR_INTERNAL and agent_role in ["supervisor", "coder"]:
        return get_local_llm(temperature=temperature)
    return get_gemini_llm(temperature=temperature)

def get_llm(temperature: float = DEFAULT_TEMPERATURE):
    return get_gemini_llm(temperature=temperature)