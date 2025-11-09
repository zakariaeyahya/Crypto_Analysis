import re
from dictionnaire import all_entities  

#Function to generate regex patterns

def generate_regex(entity_dict):
    """
    Génère un pattern regex optimisé pour matcher toutes les variantes
    Exemple : r'\b(BTC|Bitcoin|₿)\b'
    """
    patterns = {}
    for key, variants in entity_dict.items():
        escaped_variants = [re.escape(v) for v in variants]
        pattern = r'\b(' + '|'.join(escaped_variants) + r')\b'
        patterns[key] = pattern
    return patterns

# Generate patterns for each entity type

crypto_patterns = generate_regex(all_entities['cryptos'])
exchange_patterns = generate_regex(all_entities['exchanges'])
influencer_patterns = generate_regex(all_entities['influencers'])

# Global dictionary of patterns

all_patterns = {
    'cryptos': crypto_patterns,
    'exchanges': exchange_patterns,
    'influencers': influencer_patterns
}

