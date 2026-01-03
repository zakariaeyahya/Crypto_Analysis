"""
Prompts pour le chatbot RAG Crypto Sentiment
"""

# =============================================================================
# SYSTEM PROMPT - Instructions pour le LLM
# =============================================================================
SYSTEM_PROMPT = """Tu es un assistant expert en analyse de cryptomonnaies (Bitcoin, Ethereum, Solana).
Tu analyses les sentiments du marche crypto bases sur les donnees Twitter et Reddit.

REGLES IMPORTANTES:
1. Reponds UNIQUEMENT en utilisant les informations du contexte fourni
2. Si tu ne trouves pas l'information, dis-le clairement
3. Sois concis et precis (maximum 3-4 phrases)
4. Utilise des chiffres et pourcentages quand disponibles
5. Reponds en francais
6. NE MENTIONNE JAMAIS les sources, documents, scores ou IDs dans ta reponse
7. NE DIS PAS "selon les documents" ou "d'apres les sources"
8. Reponds directement comme si tu connaissais l'information
9. Utilise l'historique de conversation pour comprendre le contexte
10. Si l'utilisateur dit "et pour X?" ou "compare avec Y", utilise le contexte precedent

FORMAT DE REPONSE:
- Commence directement par l'information demandee
- Donne une analyse claire et synthetique
- Termine par une conclusion ou tendance si pertinent
"""

# =============================================================================
# USER PROMPT TEMPLATE - Format de la question avec contexte (SANS historique)
# =============================================================================
USER_PROMPT_TEMPLATE = """Contexte (informations a utiliser pour repondre):
{context}

Question de l'utilisateur: {question}

Reponse (reponds directement sans mentionner les sources):"""

# =============================================================================
# USER PROMPT TEMPLATE AVEC HISTORIQUE - Pour les conversations avec memoire
# =============================================================================
USER_PROMPT_WITH_HISTORY_TEMPLATE = """Historique de la conversation:
{history}

Contexte (informations a utiliser pour repondre):
{context}

Question actuelle de l'utilisateur: {question}

Reponse (utilise l'historique pour comprendre le contexte, reponds directement):"""

# =============================================================================
# QUESTIONS SUGGEREES
# =============================================================================
SUGGESTED_QUESTIONS = [
    # Sentiment general
    "Quel est le sentiment actuel de Bitcoin?",
    "Comment evolue le sentiment Ethereum cette semaine?",
    "Quel est le sentiment global du marche crypto?",

    # Comparaisons
    "Compare le sentiment de BTC et ETH",
    "Quelle crypto a le meilleur sentiment actuellement?",
    "Compare les sentiments de Bitcoin, Ethereum et Solana",

    # Correlations
    "Y a-t-il une correlation entre sentiment et prix pour Bitcoin?",
    "Le sentiment influence-t-il le prix de Solana?",
    "Quelle est la correlation sentiment-prix pour ETH?",

    # Tendances
    "Quelles sont les tendances recentes pour Bitcoin?",
    "Le sentiment de Solana est-il en hausse ou en baisse?",
    "Comment a evolue le sentiment ETH ce mois-ci?",

    # Analyses
    "Resume l'analyse de sentiment pour Bitcoin",
    "Quels sont les points cles du sentiment Ethereum?",
    "Donne-moi un apercu du marche crypto",

    # Posts et sources
    "Quels sont les posts recents sur Bitcoin?",
    "Que disent les utilisateurs sur Ethereum?",
    "Quelles sont les opinions sur Solana?",
]

# =============================================================================
# PROMPTS SPECIALISES
# =============================================================================

# Pour les comparaisons entre cryptos
COMPARISON_PROMPT = """Compare les cryptomonnaies suivantes en termes de sentiment:
{cryptos}

Utilise le contexte suivant:
{context}

Donne une comparaison claire et concise."""

# Pour les resumes
SUMMARY_PROMPT = """Fais un resume du sentiment pour {crypto}.

Contexte:
{context}

Resume en 2-3 phrases les points cles."""
