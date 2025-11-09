# BuildCryptoDictionnaire

## Description

This project consists of building a **dictionary of entities related to cryptocurrencies**, including:  
- Main **cryptos**  
- Most popular **exchanges**  
- Major **influencers** in the crypto field  

For this purpose, we created Excel files, Python dictionaries, and regex patterns to easily detect these entities in texts.

---

## Sources

- **Top 50 cryptocurrencies:** based on [CoinGecko](https://www.coingecko.com/)  
  - Criteria used: market capitalization, 24h trading volume, global adoption  
- **Top 20 exchanges:** selection of the most popular platforms  
- **Influencers:** around 30 major influencers in the crypto field (Twitter, specialized media, crypto communities)

---

## Files and Contents

1. **cryptos.xlsx**  
   - Contains the list of the top 50 cryptos and their variants (e.g., BTC, Bitcoin, ₿)  
2. **exchanges.xlsx**  
   - Contains the list of the top 20 exchanges and their variants  
3. **influencers.xlsx**  
   - Contains the list of 30 major influencers and their variants  
4. **dictionnaire.py**  
   - Contains the global dictionary `all_entities` built from the Excel files  
5. **regex_generator.py**  
   - Generates **regex patterns** for each entity, allowing detection of all variants in a text  
6. **detection_entities.py**  
   - Contains the `detect_entities` function to test a text and identify present cryptos, exchanges, and influencers  
   - Results are saved in a **log file** for further analysis

---

## How It Works

1. Load the Excel files and create Python dictionaries.  
2. Generate **regex patterns** to match all variants of each entity.  
3. Test a text using the `detect_entities` function to identify entities present.  
4. Results are recorded in a log file (e.g., `entity_detection.log`).  

Example log:  
```bash
2025-11-09 22:22:47,464 - INFO - Cryptos: Solana, Ethereum, Cardano, Bitcoin
2025-11-09 22:22:47,464 - INFO - Exchanges: Binance, Coinbase
2025-11-09 22:22:47,464 - INFO - Influencers: Vitalik Buterin, Changpeng Zhao

