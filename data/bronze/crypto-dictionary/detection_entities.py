import re
import logging
from dictionnaire import all_entities        
from regex_generator import all_patterns     


logging.basicConfig(
    filename='entity_detection.log',  
    level=logging.INFO,              
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Sample text to test

sample_text = "Yesterday, I traded ETH on Binance and later read a tweet from the influencer CryptoGuru about the future of Cardano. Meanwhile, Coinbase announced support for a new coin called Solana. I’m curious if BTC will continue to rise."


# Function to detect entities

def detect_entities(text, patterns_dict):
    found = {
        'cryptos': set(),
        'exchanges': set(),
        'influencers': set()
    }
    
    # Check each entity type
    for entity_type in patterns_dict:
        for key, pattern in patterns_dict[entity_type].items():
            if re.search(pattern, text):
                found[entity_type].add(key)
    
    return found


# Test on sample text

detected = detect_entities(sample_text, all_patterns)


# Log results instead of printing

logging.info("=== Entity Detection Results ===")
for entity_type, entities in detected.items():
    entity_list = ', '.join(entities) if entities else 'None'
    logging.info(f"{entity_type.capitalize()}: {entity_list}")
