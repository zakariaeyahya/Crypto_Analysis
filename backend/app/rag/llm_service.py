# backend/app/rag/llm_service.py

import requests
from app.rag.config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL
from app.rag.logger import get_logger

logger = get_logger("llm_service")

# Prompts
SYSTEM_PROMPT = """
Tu es un assistant expert en analyse de cryptomonnaies.
Tu analyses les sentiments du marché crypto basés sur les données Twitter et Reddit.

Règles:
- Réponds UNIQUEMENT en utilisant les informations du contexte fourni
- Si tu ne trouves pas l'information, dis-le clairement
- Sois concis et précis
- Utilise des chiffres quand disponibles
- Mentionne les sources (Twitter, Reddit) si pertinent
- Réponds en français
"""

USER_PROMPT_TEMPLATE = """
Contexte:
{context}

Question: {question}

Réponse:
"""

class LLMService:
    """Service pour interfacer le LLM (Groq, OpenAI, Ollama)"""

    def __init__(self, provider=LLM_PROVIDER):
        self.provider = provider
        self.groq_client = None
        self.groq_model = GROQ_MODEL
        self.openai_client = None
        self.ollama_url = "http://localhost:11434"
        self.max_tokens = 500
        self.temperature = 0.7

        if self.provider == "groq" and GROQ_API_KEY:
            from groq import Groq
            self.groq_client = Groq(api_key=GROQ_API_KEY)
            logger.info(f"Groq initialisé avec modèle: {self.groq_model}")

        if self.provider == "openai" and OPENAI_API_KEY:
            import openai
            self.openai_client = openai
            self.openai_client.api_key = OPENAI_API_KEY

    def generate_groq(self, prompt, system_prompt=None):
        if self.groq_client is None:
            raise Exception("Groq non initialisé")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def generate_openai(self, prompt, system_prompt=None):
        if self.openai_client is None:
            raise Exception("OpenAI non initialisé")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def generate_ollama(self, prompt, system_prompt=None):
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature, "num_predict": self.max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60)
            if response.ok:
                return response.json()["response"]
            else:
                raise Exception(f"Ollama error: {response.status_code}")
        except requests.ConnectionError:
            raise Exception("Ollama non disponible")

    def generate(self, prompt, system_prompt=None):
        if self.provider == "groq":
            return self.generate_groq(prompt, system_prompt)
        elif self.provider == "openai":
            return self.generate_openai(prompt, system_prompt)
        elif self.provider == "ollama":
            return self.generate_ollama(prompt, system_prompt)
        else:
            raise Exception(f"Provider inconnu: {self.provider}")

    def generate_with_context(self, question, context):
        user_prompt = USER_PROMPT_TEMPLATE.format(context=context, question=question)
        return self.generate(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)

    def is_available(self):
        if self.provider == "groq":
            return self.groq_client is not None
        elif self.provider == "openai":
            return self.openai_client is not None
        elif self.provider == "ollama":
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                return response.ok
            except:
                return False
        return False

    def get_provider_info(self):
        return {
            "provider": self.provider,
            "model": self.groq_model if self.provider == "groq" else "...",
            "available": self.is_available(),
        }


# Singleton global
_llm_service = None

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
        logger.info("✓ Singleton LLMService créé")
    return _llm_service
