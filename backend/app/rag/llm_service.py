# app/rag/llm_service.py

import requests
from app.rag.config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL
from app.rag.logger import get_logger

logger = get_logger("llm_service")

# =====================================================================
# ✅ PROMPTS CORRIGÉS ET SPÉCIALISÉS
# =====================================================================

# Prompt générique (conservé pour compatibilité)
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

# ✅ NOUVEAU: Prompt spécialisé pour les PRIX
PRICE_SYSTEM_PROMPT = """
Tu es un expert en données de prix de cryptomonnaies.

🎯 INSTRUCTIONS POUR LES PRIX:
- Fournis TOUJOURS le prix exact (jamais approximer ou estimer)
- Format requis: "Bitcoin le 2024-01-15 était $43,200"
- Inclus toujours: Crypto, Date, Prix exact
- Si variation disponible: "Bitcoin: $43,200 (+2.5%)"
- N'INVENTE JAMAIS de prix

❌ Réponse INCORRECTE: "Bitcoin coûte environ $40,000 quelque part"
✅ Réponse CORRECTE: "Bitcoin le 2024-01-15 était $43,200 (+2.5%)"

Si le prix n'est pas dans les données fournies:
Dis simplement: "Je n'ai pas trouvé le prix pour cette date"
"""

# ✅ NOUVEAU: Prompt spécialisé pour le SENTIMENT
SENTIMENT_SYSTEM_PROMPT = """
Tu es un expert en analyse du sentiment du marché crypto.

🎯 INSTRUCTIONS POUR LE SENTIMENT:
- Analyse les posts Twitter/Reddit fournis
- Calcule le sentiment moyen (score de -1 à +1)
- Labels: 
  * BULLISH (score > 0.3): Optimisme
  * BEARISH (score < -0.1): Pessimisme
  * NEUTRAL: Entre -0.1 et +0.3

Format requis: "Le sentiment pour Bitcoin est BULLISH (score: +0.65)"

Explique POURQUOI ce sentiment:
- Cite des exemples de posts
- Mentionne les mots clés positifs/négatifs
- Explique la tendance observée
"""

# ✅ NOUVEAU: Prompt spécialisé pour l'ANALYSE
ANALYSIS_SYSTEM_PROMPT = """
Tu es un expert en analyse statistique des cryptomonnaies.

🎯 INSTRUCTIONS POUR L'ANALYSE:
- Interpréte les analyses de corrélation
- Format: "La corrélation est FAIBLE/MODÉRÉE/FORTE (r=0.XX)"
- Explique ce que signifie le coefficient

Pour le LAG temporel:
- Format: "Délai détecté: X heures"
- Explique l'impact sur le prix

Utilise UNIQUEMENT les données fournies:
- N'invente pas de patterns
- Reste factuel et basé sur les données
"""

USER_PROMPT_TEMPLATE = """
Contexte (documents pertinents):
{context}

Question de l'utilisateur: {question}

Réponds en utilisant UNIQUEMENT les informations du contexte ci-dessus.
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

    def generate_with_context(self, question, context, query_type=None):
        """
        ✅ AMÉLIORÉ: Génère une réponse adaptée au type de question
        
        Args:
            question: La question de l'utilisateur
            context: Le contexte (documents trouvés)
            query_type: "price", "sentiment", "analysis", ou "general"
        """
        
        # ✅ Sélectionner le prompt adapté au type
        if query_type == "price":
            system_prompt = PRICE_SYSTEM_PROMPT
            logger.debug("Utilisant PRICE_SYSTEM_PROMPT")
            
        elif query_type == "sentiment":
            system_prompt = SENTIMENT_SYSTEM_PROMPT
            logger.debug("Utilisant SENTIMENT_SYSTEM_PROMPT")
            
        elif query_type == "analysis":
            system_prompt = ANALYSIS_SYSTEM_PROMPT
            logger.debug("Utilisant ANALYSIS_SYSTEM_PROMPT")
            
        else:
            system_prompt = SYSTEM_PROMPT
            logger.debug("Utilisant SYSTEM_PROMPT générique")
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

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