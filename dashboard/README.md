# Crypto Sentiment Analysis - Dashboard Frontend

Dashboard React pour visualiser l'analyse de sentiment des cryptomonnaies avec chatbot IA intégré.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DASHBOARD                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │    Pages     │    │  Components  │    │    Store     │          │
│  │  (Routes)    │───▶│  (UI/Charts) │◀──▶│  (Context)   │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                    │                    │                  │
│         └────────────────────┼────────────────────┘                  │
│                              ▼                                       │
│                    ┌──────────────┐                                 │
│                    │   API Layer  │                                 │
│                    │  (fetch)     │                                 │
│                    └──────────────┘                                 │
│                              │                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               ▼
                    ┌──────────────┐
                    │   Backend    │
                    │   :8000      │
                    └──────────────┘
```

## Installation

```bash
cd dashboard
npm install
```

## Lancer le dashboard

```bash
npm start
```

Le dashboard sera disponible sur http://localhost:3000

## Structure

```
dashboard/
├── package.json
├── public/
│   └── index.html
├── src/
│   ├── index.js              # Point d'entrée React
│   ├── App.jsx               # Composant principal + Routes
│   │
│   ├── api/
│   │   └── index.js          # Appels API backend
│   │
│   ├── store/
│   │   ├── index.js          # Export des providers
│   │   └── CryptoContext.js  # State global (cryptos, sentiment)
│   │
│   ├── components/
│   │   ├── Header.jsx        # Navigation + logo
│   │   ├── MetricCard.jsx    # Cartes métriques
│   │   ├── SentimentGauge.jsx # Jauge sentiment circulaire
│   │   ├── CryptoChart.jsx   # Graphiques Recharts
│   │   ├── Chatbot.jsx       # Composant chatbot complet
│   │   └── ChatbotWidget.jsx # Widget flottant chatbot
│   │
│   ├── pages/
│   │   ├── Overview.jsx      # Vue d'ensemble
│   │   ├── Timeline.jsx      # Timeline sentiment
│   │   ├── Analysis.jsx      # Analyse corrélation
│   │   ├── Events.jsx        # Liste des posts
│   │   ├── AIChat.jsx        # Page chatbot dédiée
│   │   └── About.jsx         # À propos
│   │
│   ├── styles/
│   │   ├── commonStyles.js   # Styles partagés
│   │   └── about.css         # Styles page About
│   │
│   └── data/
│       └── mockData.js       # Données mock (fallback)
│
└── images/
    └── ...                   # Images équipe
```

## Pages

### Overview (`/`)
- Vue d'ensemble du marché crypto
- Cartes métriques (prix, variation, sentiment)
- Graphique de prix
- Jauge de sentiment global

### Timeline (`/timeline`)
- Timeline du sentiment par crypto
- Graphique LineChart avec moyenne mobile (MA7)
- Sélecteur de période (7, 30, 90 jours)

### Analysis (`/analysis`)
- Corrélation Pearson sentiment/prix
- Scatter plot interactif
- Analyse lag (daily, weekly, monthly)
- Statistiques détaillées

### Events (`/events`)
- Liste des posts Twitter/Reddit
- Filtres par crypto et sentiment
- Statistiques (total, positif, négatif, neutre)
- Pagination

### AI Chat (`/chat`)
- Interface chatbot dédiée pleine page
- Historique des conversations
- Suggestions de questions
- Affichage des sources RAG

### About (`/about`)
- Présentation du projet
- Équipe
- Technologies utilisées

## Composants

### Header
Navigation principale avec liens vers toutes les pages.

### MetricCard
Carte affichant une métrique avec icône et variation.

```jsx
<MetricCard
  title="Prix BTC"
  value="$42,500"
  change={2.5}
  icon={<TrendingUp />}
/>
```

### SentimentGauge
Jauge circulaire affichant le score de sentiment.

```jsx
<SentimentGauge score={0.65} label="Bullish" />
```

### CryptoChart
Graphique Recharts pour les prix et le sentiment.

```jsx
<CryptoChart data={priceData} type="line" />
```

### Chatbot / ChatbotWidget
Chatbot IA avec interface conversationnelle.

```jsx
// Widget flottant (toutes les pages)
<ChatbotWidget />

// Composant complet (page dédiée)
<Chatbot />
```

## State Management

### CryptoContext

```jsx
// Utilisation dans un composant
import { useCrypto } from '../store/CryptoContext';

function MyComponent() {
  const {
    cryptos,          // Liste des cryptos
    selectedCrypto,   // Crypto sélectionnée
    setSelectedCrypto,
    sentiment,        // Données sentiment
    loading,          // État chargement
    error             // Erreur éventuelle
  } = useCrypto();

  // ...
}
```

## API Layer

### Fonctions disponibles (`src/api/index.js`)

```javascript
// Cryptos
getCryptos()                    // Liste des cryptos
getCryptoDetails(symbol)        // Détails d'une crypto
getCryptoChart(symbol, days)    // Historique prix

// Sentiment
getGlobalSentiment()            // Sentiment global
getSentimentTimeline(symbol, days)  // Timeline

// Analysis
getCorrelation(symbol)          // Corrélation Pearson
getLagAnalysis(symbol)          // Analyse lag
getScatterData(symbol, days)    // Données scatter

// Events
getEvents(params)               // Liste des posts
getEventsStats(crypto)          // Statistiques

// Chat
sendChatMessage(message, crypto)  // Envoyer message
getChatHealth()                   // État du chatbot
getChatSuggestions()              // Suggestions
```

### Configuration API

```javascript
// src/api/index.js
const API_BASE_URL = 'http://localhost:8000/api';
```

## Design

### Thème
- **Mode sombre** avec fond gradient
- **Glassmorphism** : backdrop-blur, transparence
- **Couleurs** :
  - Primaire : `#667eea` (violet)
  - Secondaire : `#764ba2` (violet foncé)
  - Positif : `#00b894` (vert)
  - Négatif : `#e74c3c` (rouge)

### Styles partagés

```javascript
// src/styles/commonStyles.js
export const cardStyle = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
};
```

## Scripts disponibles

```bash
# Développement
npm start

# Build production
npm run build

# Tests
npm test

# Linter
npm run lint
```

## Intégration Backend

Le dashboard communique avec l'API backend sur `localhost:8000`.

### Prérequis
1. Backend lancé : `uvicorn app.main:app --reload --port 8000`
2. Index Pinecone initialisé (pour le chatbot)

### CORS
Le backend est configuré pour accepter les requêtes depuis `localhost:3000`.

## Chatbot IA

Le chatbot utilise le système RAG du backend :

1. **Question** envoyée au backend
2. **Embedding** généré avec MiniLM
3. **Recherche** dans Pinecone (documents similaires)
4. **Génération** de réponse avec Groq LLM
5. **Affichage** avec sources

### Fonctionnalités
- Historique de conversation
- Suggestions de questions cliquables
- Affichage des sources avec scores
- Indicateur de chargement
- Widget flottant sur toutes les pages

## Tech Stack

- **React 18** - Framework UI
- **React Router v6** - Navigation SPA
- **Recharts** - Graphiques (LineChart, ScatterChart, PieChart)
- **Lucide React** - Icônes
- **CSS-in-JS** - Styles inline

## Cryptomonnaies supportées

| Symbol | Nom |
|--------|-----|
| BTC | Bitcoin |
| ETH | Ethereum |
| SOL | Solana |

## Captures d'écran

### Overview
Vue d'ensemble avec métriques et graphiques.

### Timeline
Évolution du sentiment dans le temps.

### Analysis
Corrélation et scatter plot interactif.

### Events
Liste des posts avec filtres.

### AI Chat
Interface conversationnelle avec le chatbot.
